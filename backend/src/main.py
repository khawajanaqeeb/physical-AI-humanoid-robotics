"""
FastAPI application entry point.

Main application with CORS middleware, error handlers, and route registration.
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.core.config import settings
from src.core.exceptions import (
    RAGChatbotError,
    CohereAPIError,
    QdrantConnectionError,
    ValidationError,
    RateLimitError,
)
from src.core.logging_config import get_logger, setup_logging

logger = get_logger(__name__)

# Configure rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Application lifespan context manager.

    Handles startup and shutdown events.
    """
    # Startup
    setup_logging(settings.log_level)
    logger.info(
        "Application starting",
        extra={
            "qdrant_collection": settings.qdrant_collection_name,
            "cors_origins": settings.cors_origins,
        },
    )
    yield
    # Shutdown
    logger.info("Application shutting down")


# Create FastAPI application
app = FastAPI(
    title="RAG Chatbot API",
    description="Cohere + Qdrant RAG chatbot for Physical AI & Humanoid Robotics textbook",
    version="1.0.0",
    lifespan=lifespan,
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(ValidationError)
async def validation_error_handler(
    request: Request,
    exc: ValidationError,
) -> JSONResponse:
    """Handle validation errors with 400 Bad Request."""
    logger.warning(
        f"Validation error: {exc.message}",
        extra={"details": exc.details},
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Validation Error",
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(RateLimitError)
async def rate_limit_error_handler(
    request: Request,
    exc: RateLimitError,
) -> JSONResponse:
    """Handle rate limit errors with 429 Too Many Requests."""
    logger.warning(
        f"Rate limit exceeded: {exc.message}",
        extra={"details": exc.details},
    )
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "Rate Limit Exceeded",
            "message": exc.message,
        },
    )


@app.exception_handler(CohereAPIError)
async def cohere_api_error_handler(
    request: Request,
    exc: CohereAPIError,
) -> JSONResponse:
    """Handle Cohere API errors with 502 Bad Gateway."""
    logger.error(
        f"Cohere API error: {exc.message}",
        extra={"details": exc.details},
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={
            "error": "External API Error",
            "message": "Failed to communicate with AI service",
        },
    )


@app.exception_handler(QdrantConnectionError)
async def qdrant_error_handler(
    request: Request,
    exc: QdrantConnectionError,
) -> JSONResponse:
    """Handle Qdrant errors with 503 Service Unavailable."""
    logger.error(
        f"Qdrant connection error: {exc.message}",
        extra={"details": exc.details},
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": "Database Unavailable",
            "message": "Vector database is temporarily unavailable",
        },
    )


@app.exception_handler(RAGChatbotError)
async def generic_rag_error_handler(
    request: Request,
    exc: RAGChatbotError,
) -> JSONResponse:
    """Handle generic RAG chatbot errors with 500 Internal Server Error."""
    logger.error(
        f"Application error: {exc.message}",
        extra={"details": exc.details},
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": exc.message,
        },
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """
    Health check endpoint.

    Returns:
        dict: Service health status
    """
    return {
        "status": "healthy",
        "service": "rag-chatbot-api",
        "version": "1.0.0",
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> dict:
    """
    Root endpoint with API information.

    Returns:
        dict: Welcome message and documentation link
    """
    return {
        "message": "RAG Chatbot API",
        "docs": "/docs",
        "health": "/health",
    }


# Register query route
from src.api.routes import query
app.include_router(query.router, prefix="/api/v1", tags=["Query"])

# TODO: Register ingestion route in Phase 5
# from src.api.routes import ingest
# app.include_router(ingest.router, prefix="/api/v1", tags=["Ingestion"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )