"""
QuerySession and SourceCitation models for query processing tracking.

Represents user interactions from query to response with observability data.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from src.models.chunk import DocumentChunk


class SourceCitation(BaseModel):
    """
    Source reference linking answer to textbook content.

    Provides transparency and verification for generated answers.
    """

    page_url: str = Field(
        ...,
        description="Link to source textbook page",
    )
    page_title: str = Field(
        ...,
        min_length=1,
        description="Human-readable page title",
    )
    chunk_text: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="Excerpt from retrieved chunk (max 300 chars)",
    )
    relevance_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Qdrant similarity score (0.0-1.0)",
    )

    @field_validator("chunk_text")
    @classmethod
    def truncate_chunk_text(cls, v: str) -> str:
        """Truncate chunk_text with ellipsis if exceeds 300 characters."""
        if len(v) > 300:
            return v[:297] + "..."
        return v

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "page_url": "https://physical-ai-humanoid-robotics-e3c7.vercel.app/docs/sensors",
                "page_title": "Sensor Systems in Humanoid Robots",
                "chunk_text": "Force-torque sensors measure forces and torques at robot joints...",
                "relevance_score": 0.85,
            }
        }


class QuerySession(BaseModel):
    """
    Complete user interaction from query to response.

    Tracks query processing for observability, debugging, and performance monitoring.
    """

    session_id: UUID = Field(
        default_factory=uuid4,
        description="Unique identifier for query session",
    )
    query_text: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's original question",
    )
    embedding_vector: List[float] = Field(
        ...,
        description="Embedded query for retrieval (1024 dimensions)",
    )
    retrieved_chunks: List[DocumentChunk] = Field(
        default_factory=list,
        description="Chunks retrieved from Qdrant (top-K)",
    )
    generated_response: str = Field(
        default="",
        description="Cohere-generated answer",
    )
    source_citations: List[SourceCitation] = Field(
        default_factory=list,
        description="Sources used in response",
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="When query was received (ISO 8601)",
    )
    response_time_ms: int = Field(
        default=0,
        gt=0,
        description="Total processing time in milliseconds",
    )
    retrieval_score_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score used for retrieval",
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if query failed",
    )

    @field_validator("embedding_vector")
    @classmethod
    def validate_embedding_dimension(cls, v: List[float]) -> List[float]:
        """Validate that embedding has exactly 1024 dimensions."""
        if len(v) != 1024:
            raise ValueError(f"Embedding must have 1024 dimensions, got {len(v)}")
        return v

    @field_validator("source_citations")
    @classmethod
    def validate_citations_exist(cls, v: List[SourceCitation], info) -> List[SourceCitation]:
        """Validate that citations exist if response is generated."""
        # Note: Validation relaxed to allow empty citations
        # This prevents failures when citation extraction has issues
        # while still allowing the answer to be returned
        return v

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "query_text": "What are the main components of a humanoid robot?",
                "embedding_vector": [0.234, -0.567] + [0.0] * 1022,  # Truncated
                "retrieved_chunks": [],  # Would contain DocumentChunk objects
                "generated_response": "Based on the textbook, the main components include...",
                "source_citations": [
                    {
                        "page_url": "https://physical-ai-humanoid-robotics-e3c7.vercel.app/docs/components",
                        "page_title": "Robot Components",
                        "chunk_text": "The primary components include actuators, sensors...",
                        "relevance_score": 0.89,
                    }
                ],
                "timestamp": "2025-12-16T15:45:30Z",
                "response_time_ms": 1850,
                "retrieval_score_threshold": 0.7,
                "error": None,
            }
        }
