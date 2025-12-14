"""
Gemini Query API Endpoint

Handles RAG queries using Gemini embeddings and generation.
Implements the POST /query endpoint for the Gemini-based chatbot.
"""

import time
from datetime import datetime
from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException, status
import structlog

from src.api.gemini_schemas import QueryRequest, QueryResponse, ErrorResponse
from src.services.gemini_rag_service import get_gemini_rag_service

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post(
    "/query",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
        503: {"model": ErrorResponse, "description": "Service temporarily unavailable"}
    },
    summary="Submit a question to the chatbot",
    description="""
    Process a natural language question using the Gemini RAG pipeline:
    1. Embed query with Gemini embedding-001
    2. Retrieve relevant chunks from Qdrant
    3. Generate response with Gemini Pro
    4. Return answer with source citations
    """
)
async def process_gemini_query(request: QueryRequest) -> QueryResponse:
    """
    Process a user question through the Gemini RAG pipeline.

    Args:
        request: QueryRequest with question, session_id, and max_results

    Returns:
        QueryResponse with answer, sources, confidence, and timing

    Raises:
        HTTPException 400: Invalid request
        HTTPException 500: Internal server error
    """
    start_time = time.time()

    # Generate session_id if not provided
    if request.session_id:
        try:
            session_uuid = UUID(request.session_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Validation error",
                    "message": "session_id must be a valid UUID format",
                    "code": "INVALID_SESSION_ID"
                }
            )
    else:
        session_uuid = uuid4()

    logger.info(
        "gemini_query_received",
        session_id=str(session_uuid),
        question_preview=request.question[:50],
        max_results=request.max_results
    )

    try:
        # Input validation
        if len(request.question.strip()) < 3:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Validation error",
                    "message": "Question must be at least 3 characters long",
                    "code": "INVALID_INPUT"
                }
            )

        # Process query through Gemini RAG pipeline
        rag_service = get_gemini_rag_service()

        result = await rag_service.process_query(
            query_text=request.question,
            session_id=session_uuid,
            top_k=request.max_results,
            score_threshold=0.7
        )

        # Calculate total response time
        response_time_ms = int((time.time() - start_time) * 1000)

        # Build response
        response = QueryResponse(
            answer=result.answer_text,
            sources=[
                {
                    "chapter": source.chapter,
                    "section": source.section,
                    "source_url": source.source_url,
                    "relevance_score": source.relevance_score
                }
                for source in result.sources
            ],
            confidence=result.confidence,
            response_time_ms=response_time_ms
        )

        logger.info(
            "gemini_query_completed",
            session_id=str(session_uuid),
            response_time_ms=response_time_ms,
            confidence=result.confidence,
            sources_count=len(result.sources)
        )

        return response

    except ValueError as e:
        # Input validation errors
        logger.warning(
            "gemini_query_validation_failed",
            error=str(e),
            question_preview=request.question[:50]
        )

        raise HTTPException(
            status_code=400,
            detail={
                "error": "Validation error",
                "message": str(e),
                "code": "INVALID_INPUT"
            }
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        # Internal server errors
        logger.error(
            "gemini_query_failed",
            error=str(e),
            error_type=type(e).__name__,
            session_id=str(session_uuid)
        )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An error occurred while processing your query. Please try again.",
                "code": "INTERNAL_ERROR"
            }
        )
