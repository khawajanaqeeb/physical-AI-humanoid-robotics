"""
Custom exception classes for the RAG chatbot application.

Provides structured error handling across all components.
"""

from typing import Any, Dict, Optional


class RAGChatbotError(Exception):
    """Base exception for all RAG chatbot errors."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize exception with message and optional details.

        Args:
            message: Human-readable error message
            details: Additional error context (e.g., API response, request data)
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class CohereAPIError(RAGChatbotError):
    """
    Error raised when Cohere API calls fail.

    Examples:
        - API key invalid or expired
        - Rate limit exceeded
        - Embedding or generation request failure
        - Network timeout
    """

    pass


class QdrantConnectionError(RAGChatbotError):
    """
    Error raised when Qdrant operations fail.

    Examples:
        - Connection to Qdrant Cloud failed
        - Invalid API credentials
        - Collection not found
        - Vector upsert or search failure
    """

    pass


class IngestionError(RAGChatbotError):
    """
    Error raised during textbook content ingestion.

    Examples:
        - Sitemap fetch failure
        - HTML parsing error
        - Content extraction failure
        - Chunking errors
    """

    pass


class ValidationError(RAGChatbotError):
    """
    Error raised when data validation fails.

    Examples:
        - Invalid request payload
        - Missing required fields
        - Data type mismatches
        - Business rule violations
    """

    pass


class ConfigurationError(RAGChatbotError):
    """
    Error raised when configuration is invalid or missing.

    Examples:
        - Missing required environment variables
        - Invalid .env file format
        - Configuration validation failure
    """

    pass


class RateLimitError(RAGChatbotError):
    """
    Error raised when rate limits are exceeded.

    Examples:
        - Too many requests from single IP
        - API quota exceeded
    """

    pass
