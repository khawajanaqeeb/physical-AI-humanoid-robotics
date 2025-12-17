"""
DocumentChunk model for textbook content chunks.

Represents a semantically coherent segment of textbook content with embedding.
"""

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class DocumentChunk(BaseModel):
    """
    Core unit of retrieval in the RAG system.

    Each chunk contains a portion of textbook content that can be
    independently embedded, stored, and retrieved from Qdrant.
    """

    chunk_id: str = Field(
        default_factory=lambda: uuid4().hex,
        description="Unique identifier for the chunk (UUID hex format)",
    )
    content_text: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Full text content of the chunk (500-1000 characters)",
    )
    embedding_vector: List[float] = Field(
        ...,
        description="Cohere embed-english-v3.0 embedding (1024 dimensions)",
    )
    page_url: str = Field(
        ...,
        description="Source page URL from textbook",
    )
    page_title: str = Field(
        ...,
        min_length=1,
        description="Human-readable page title",
    )
    section_heading: Optional[str] = Field(
        default=None,
        description="Heading/section context for chunk",
    )
    chunk_index: int = Field(
        ...,
        ge=0,
        description="Sequential position within page",
    )
    character_count: int = Field(
        ...,
        gt=0,
        description="Length of content_text",
    )
    ingestion_timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="When chunk was created/updated (ISO 8601)",
    )

    @field_validator("embedding_vector")
    @classmethod
    def validate_embedding_dimension(cls, v: List[float]) -> List[float]:
        """Validate that embedding has exactly 1024 dimensions."""
        if len(v) != 1024:
            raise ValueError(f"Embedding must have 1024 dimensions, got {len(v)}")
        return v

    @field_validator("character_count")
    @classmethod
    def validate_character_count(cls, v: int, info) -> int:
        """Validate that character_count matches content_text length."""
        content_text = info.data.get("content_text", "")
        if v != len(content_text):
            raise ValueError(
                f"character_count ({v}) must equal len(content_text) ({len(content_text)})"
            )
        return v

    @field_validator("page_url")
    @classmethod
    def validate_page_url(cls, v: str) -> str:
        """Validate that page_url is from textbook domain."""
        expected_domain = "physical-ai-humanoid-robotics-e3c7.vercel.app"
        if expected_domain not in v:
            raise ValueError(
                f"page_url must be from textbook domain: {expected_domain}"
            )
        return v

    def to_qdrant_payload(self) -> dict:
        """
        Convert chunk to Qdrant payload format.

        Returns:
            dict: Payload with all fields except embedding_vector
        """
        return {
            "chunk_id": self.chunk_id,
            "content_text": self.content_text,
            "page_url": self.page_url,
            "page_title": self.page_title,
            "section_heading": self.section_heading,
            "chunk_index": self.chunk_index,
            "character_count": self.character_count,
            "ingestion_timestamp": self.ingestion_timestamp,
        }

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "chunk_id": "a1b2c3d4e5f6",
                "content_text": "Humanoid robotics combines mechanical engineering with artificial intelligence to create robots that mimic human form and behavior.",
                "embedding_vector": [0.123, -0.456] + [0.0] * 1022,  # Truncated for example
                "page_url": "https://physical-ai-humanoid-robotics-e3c7.vercel.app/docs/intro",
                "page_title": "Introduction to Humanoid Robotics",
                "section_heading": "Overview",
                "chunk_index": 0,
                "character_count": 131,
                "ingestion_timestamp": "2025-12-16T10:30:00Z",
            }
        }
