"""
API request schemas for validation.

Pydantic models for validating incoming API requests.
"""

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """
    Request schema for POST /api/v1/query endpoint.

    User submits a question and optionally configures retrieval parameters.
    """

    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's question about the textbook content",
        examples=["What are the main components of a humanoid robot?"],
    )

    max_results: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum number of source chunks to retrieve",
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "query": "What are the main components of a humanoid robot?",
                "max_results": 5,
            }
        }
