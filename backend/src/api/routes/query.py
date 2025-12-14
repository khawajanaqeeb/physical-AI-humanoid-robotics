"""
Query API endpoint for processing user questions.

This module handles the /api/query endpoint that orchestrates
the RAG pipeline and returns answers with citations.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from src.api.schemas import QueryRequest, QueryResponse
from src.services.rag_service import get_rag_service
from src.repositories.query_repository import get_query_repository
from src.config.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/query", response_model=QueryResponse, status_code=status.HTTP_200_OK)
async def process_query(request: QueryRequest):
    """
    Process a user query through the RAG pipeline.

    This endpoint:
    1. Validates the query (language, scope)
    2. Retrieves relevant chunks from Qdrant
    3. Generates an answer using GPT-4
    4. Creates citations with Docusaurus links
    5. Logs the query to the database
    6. Returns the response with timing information

    Args:
        request: QueryRequest with query, session_id, and optional selected_text

    Returns:
        QueryResponse with answer, citations, sources, and timing

    Raises:
        HTTPException 400: Invalid request (non-English, out of scope)
        HTTPException 422: Validation error
        HTTPException 500: Internal server error

    Example:
        ```
        POST /api/query
        {
            "query": "What is forward kinematics?",
            "session_id": "550e8400-e29b-41d4-a716-446655440000"
        }
        ```
    """
    logger.info(
        "query_request_received",
        session_id=request.session_id,
        query_preview=request.query[:50],
        has_selection=request.selected_text is not None,
    )

    try:
        # Parse session_id as UUID
        try:
            session_uuid = UUID(request.session_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid session_id format. Must be a valid UUID.",
                    "error_code": "INVALID_SESSION_ID",
                }
            )

        # Process query through RAG service
        rag_service = get_rag_service()
        query_result = await rag_service.process_query(
            query_text=request.query,
            session_id=session_uuid,
            selected_text=request.selected_text,
        )

        # Save query to database (async, don't block response)
        try:
            query_repo = get_query_repository()
            await query_repo.save_query(query_result)
        except Exception as e:
            # Log error but don't fail the request
            logger.error(
                "query_logging_failed",
                query_id=str(query_result.query_id),
                error=str(e),
            )

        # Extract unique sources
        citation_agent = rag_service.citation_agent
        sources = citation_agent.extract_unique_sources(query_result.citations)

        # Build response
        response = QueryResponse(
            answer=query_result.answer_text,
            citations=query_result.citations,
            sources=sources,
            retrieval_time_ms=query_result.retrieval_time_ms,
            answer_time_ms=query_result.answer_time_ms,
            citation_time_ms=query_result.citation_time_ms,
            total_time_ms=query_result.total_time_ms,
        )

        logger.info(
            "query_request_completed",
            query_id=str(query_result.query_id),
            session_id=str(session_uuid),
            total_time_ms=query_result.total_time_ms,
        )

        return response

    except HTTPException:
        # Re-raise HTTP exceptions (validation errors from language/scope checks)
        raise

    except Exception as e:
        logger.error(
            "query_request_failed",
            error=str(e),
            error_type=type(e).__name__,
        )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "An error occurred while processing your query. Please try again.",
                "error_code": "INTERNAL_ERROR",
            }
        )
