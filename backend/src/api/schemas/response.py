"""
API response schemas.

Pydantic models for API responses.
"""

from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class SourceCitationResponse(BaseModel):
    """
    Source citation in query response.

    Links answer to specific textbook pages with relevance scores.
    """

    page_url: str = Field(
        ...,
        description="URL to source textbook page",
    )

    page_title: str = Field(
        ...,
        description="Human-readable page title",
    )

    chunk_text: str = Field(
        ...,
        description="Excerpt from source chunk (max 300 chars)",
    )

    relevance_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Similarity score from vector search (0.0-1.0)",
    )

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


class QueryResponse(BaseModel):
    """
    Response schema for POST /api/v1/query endpoint.

    Contains generated answer with source citations and metadata.
    """

    session_id: UUID = Field(
        ...,
        description="Unique identifier for this query session",
    )

    query: str = Field(
        ...,
        description="Original user question",
    )

    answer: str = Field(
        ...,
        description="Generated answer from textbook content",
    )

    sources: List[SourceCitationResponse] = Field(
        ...,
        description="Source citations with page URLs and relevance scores",
    )

    response_time_ms: int = Field(
        ...,
        description="Total processing time in milliseconds",
    )

    chunks_retrieved: int = Field(
        ...,
        description="Number of textbook chunks used to generate answer",
    )

    personalization_applied: bool = Field(
        default=False,
        description="Whether personalized system prompt was applied based on user profile",
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "query": "What are the main components of a humanoid robot?",
                "answer": "Based on the textbook, the main components of a humanoid robot include...",
                "sources": [
                    {
                        "page_url": "https://physical-ai-humanoid-robotics-e3c7.vercel.app/docs/components",
                        "page_title": "Robot Components",
                        "chunk_text": "The primary components include actuators, sensors...",
                        "relevance_score": 0.89,
                    }
                ],
                "response_time_ms": 1850,
                "chunks_retrieved": 5,
                "personalization_applied": True,
            }
        }
