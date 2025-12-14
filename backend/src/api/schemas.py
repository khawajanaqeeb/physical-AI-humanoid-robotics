"""
API request/response models for all endpoints.

This module defines Pydantic schemas for API validation and documentation.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.models import Citation, FeedbackType, SyncStatus


# Query Endpoint Schemas

class QueryRequest(BaseModel):
    """Request schema for query endpoint."""

    query: str = Field(..., min_length=1, max_length=5000, description="User question in English")
    session_id: str = Field(..., description="Browser session UUID from sessionStorage")
    selected_text: Optional[str] = Field(None, max_length=2000, description="Optional text selection for context")

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "What is forward kinematics?",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "selected_text": "The robot arm consists of multiple joints..."
            }
        }
    }


class QueryResponse(BaseModel):
    """Response schema for query endpoint."""

    answer: str = Field(..., description="Generated answer from Answer Agent")
    citations: List[Citation] = Field(..., description="Source citations with links")
    sources: List[str] = Field(..., description="Unique document titles referenced")
    retrieval_time_ms: int = Field(..., ge=0, description="Time spent in Retrieval Agent (ms)")
    answer_time_ms: int = Field(..., ge=0, description="Time spent in Answer Agent (ms)")
    citation_time_ms: int = Field(..., ge=0, description="Time spent in Citation Agent (ms)")
    total_time_ms: int = Field(..., ge=0, description="Total query processing time (ms)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "answer": "Forward kinematics is the process of calculating...",
                "citations": [
                    {
                        "title": "Robotics Fundamentals",
                        "anchor": "forward-kinematics",
                        "url": "/docs/chapter-01#forward-kinematics"
                    }
                ],
                "sources": ["Robotics Fundamentals"],
                "retrieval_time_ms": 45,
                "answer_time_ms": 1200,
                "citation_time_ms": 30,
                "total_time_ms": 1275
            }
        }
    }


# Feedback Endpoint Schemas

class FeedbackRequest(BaseModel):
    """Request schema for feedback endpoint."""

    query_id: UUID = Field(..., description="Query ID to provide feedback for")
    feedback_type: FeedbackType = Field(..., description="Thumbs up or thumbs down")

    model_config = {
        "json_schema_extra": {
            "example": {
                "query_id": "123e4567-e89b-12d3-a456-426614174000",
                "feedback_type": "positive"
            }
        }
    }


class FeedbackResponse(BaseModel):
    """Response schema for feedback endpoint."""

    feedback_id: UUID
    message: str = Field(default="Feedback recorded successfully")


# Sync Endpoint Schemas

class SyncTriggerRequest(BaseModel):
    """Request schema for sync trigger endpoint."""

    force: bool = Field(default=False, description="Force re-sync all files (ignores timestamps)")


class SyncTriggerResponse(BaseModel):
    """Response schema for sync trigger endpoint."""

    sync_id: UUID
    status: str = Field(default="running")
    message: str = Field(default="Sync job started successfully")


class SyncJobStatus(BaseModel):
    """Response schema for sync status endpoint."""

    sync_id: UUID
    start_time: str
    end_time: Optional[str] = None
    status: SyncStatus
    files_processed: int = Field(..., ge=0)
    files_failed: int = Field(..., ge=0)
    error_log: Optional[List[dict]] = None


# Health Check Schema

class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""

    status: str = Field(..., description="Overall health status")
    checks: dict = Field(..., description="Individual component health checks")
    version: str = Field(default="1.0.0", description="API version")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "checks": {
                    "database": "ok",
                    "qdrant": "ok",
                    "mcp_server": "ok",
                    "openai_api": "ok"
                },
                "version": "1.0.0"
            }
        }
    }


# Error Response Schema

class ErrorResponse(BaseModel):
    """Standard error response schema."""

    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Machine-readable error code")
    details: Optional[dict] = Field(None, description="Additional error context")


__all__ = [
    "QueryRequest",
    "QueryResponse",
    "FeedbackRequest",
    "FeedbackResponse",
    "SyncTriggerRequest",
    "SyncTriggerResponse",
    "SyncJobStatus",
    "HealthResponse",
    "ErrorResponse",
]
