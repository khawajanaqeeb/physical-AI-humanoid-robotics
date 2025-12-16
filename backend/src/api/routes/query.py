"""
Query endpoint for textbook Q&A.

Handles user questions and returns generated answers with citations.
"""

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from src.api.middleware.rate_limit import limiter
from src.api.schemas.request import QueryRequest
from src.api.schemas.response import QueryResponse, SourceCitationResponse
from src.core.logging_config import get_logger
from src.services.rag_service import rag_service

logger = get_logger(__name__)

# Create router
router = APIRouter()


@router.post(
    "/query",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Query textbook content",
    description="Submit a question and receive an AI-generated answer with source citations from the textbook.",
)
@limiter.limit("10/minute")  # Rate limit: 10 requests per minute per IP
async def query_textbook(
    request: Request,
    query_request: QueryRequest,
) -> QueryResponse:
    """
    Process user query and return answer with citations.

    Args:
        request: FastAPI request object (for rate limiting)
        query_request: User query with optional parameters

    Returns:
        QueryResponse with answer and source citations

    Rate Limit:
        10 requests per minute per IP address

    Example Request:
        ```json
        {
            "query": "What are the main components of a humanoid robot?",
            "max_results": 5
        }
        ```

    Example Response:
        ```json
        {
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "query": "What are the main components of a humanoid robot?",
            "answer": "Based on the textbook...",
            "sources": [...],
            "response_time_ms": 1850,
            "chunks_retrieved": 5
        }
        ```
    """
    # Log request
    logger.info(
        "Query request received",
        extra={
            "query_length": len(query_request.query),
            "max_results": query_request.max_results,
            "client_ip": request.client.host if request.client else "unknown",
        },
    )

    try:
        # Process query through RAG service
        session = rag_service.query_textbook(
            query_text=query_request.query,
            max_results=query_request.max_results,
        )

        # Convert SourceCitation to SourceCitationResponse
        source_responses = [
            SourceCitationResponse(
                page_url=citation.page_url,
                page_title=citation.page_title,
                chunk_text=citation.chunk_text,
                relevance_score=citation.relevance_score,
            )
            for citation in session.source_citations
        ]

        # Create response
        response = QueryResponse(
            session_id=session.session_id,
            query=session.query_text,
            answer=session.generated_response,
            sources=source_responses,
            response_time_ms=session.response_time_ms,
            chunks_retrieved=len(session.retrieved_chunks),
        )

        # Log successful response
        logger.info(
            "Query processed successfully",
            extra={
                "session_id": str(session.session_id),
                "response_time_ms": session.response_time_ms,
                "chunks_retrieved": len(session.retrieved_chunks),
                "citations": len(session.source_citations),
            },
        )

        return response

    except Exception as e:
        # Log error
        logger.error(
            f"Query processing failed: {e}",
            extra={
                "query": query_request.query[:100],  # Log first 100 chars
                "error": str(e),
            },
            exc_info=True,
        )

        # Return error response
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "message": "Failed to process query. Please try again later.",
            },
        )
