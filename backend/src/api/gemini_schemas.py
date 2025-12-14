"""
Gemini API Schemas

Pydantic models for Gemini RAG API requests and responses.
Based on the OpenAPI specification in contracts/api.openapi.yaml
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request schema for Gemini query endpoint."""

    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="User's natural language question about the book content",
        examples=["What is the difference between forward and inverse kinematics?"]
    )
    session_id: Optional[str] = Field(
        None,
        description="Optional session ID for multi-turn conversations (UUID format)",
        examples=["b4c3d2e1-6789-1234-cdef-567890abcdef"]
    )
    max_results: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of relevant chunks to retrieve from vector database"
    )


class SourceCitation(BaseModel):
    """Source citation schema."""

    chapter: str = Field(..., description="Chapter title from the book", max_length=256)
    section: Optional[str] = Field(None, description="Section heading within the chapter", max_length=256)
    source_url: str = Field(..., description="Public URL to the book page containing this information")
    relevance_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Similarity score from vector search (cosine similarity)"
    )


class QueryResponse(BaseModel):
    """Response schema for Gemini query endpoint."""

    answer: str = Field(..., min_length=10, description="AI-generated answer based on retrieved book content")
    sources: List[SourceCitation] = Field(..., description="List of book sections used to generate the answer")
    confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Confidence score for the generated answer (0.0 = low, 1.0 = high)"
    )
    response_time_ms: int = Field(..., ge=0, description="Time taken to process the query in milliseconds")


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    error: str = Field(..., description="High-level error category")
    message: str = Field(..., description="Human-readable error message")
    code: str = Field(
        ...,
        description="Machine-readable error code",
        examples=["INVALID_INPUT", "RATE_LIMIT_EXCEEDED", "INTERNAL_ERROR"]
    )


class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""

    status: str = Field(..., description="Overall system health status", examples=["healthy", "degraded", "unhealthy"])
    qdrant_connected: bool = Field(..., description="Qdrant vector database connection status")
    postgres_connected: bool = Field(..., description="Neon Postgres database connection status")
    gemini_api_available: bool = Field(..., description="Google Gemini API availability")
    timestamp: str = Field(..., description="ISO 8601 timestamp of health check")
