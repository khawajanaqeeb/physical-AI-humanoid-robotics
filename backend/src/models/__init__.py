"""
Pydantic models for all entities.

This module defines data models for textbook chunks, queries, feedback,
and sync jobs.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Citation(BaseModel):
    """Citation linking answer to source chunk."""

    title: str = Field(..., description="Document title")
    anchor: str = Field(..., description="Heading anchor ID")
    url: str = Field(..., description="Full URL with hash")


class Query(BaseModel):
    """User query with retrieval results and generated answer."""

    query_id: UUID = Field(default_factory=uuid4)
    query_text: str = Field(..., min_length=1, max_length=5000)
    user_session_id: UUID
    selected_text: Optional[str] = None
    retrieved_chunk_ids: List[str] = Field(default_factory=list)
    answer_text: str = ""
    citations: List[Citation] = Field(default_factory=list)
    similarity_scores: List[float] = Field(default_factory=list)
    retrieval_time_ms: int = Field(default=0, ge=0)
    answer_time_ms: int = Field(default=0, ge=0)
    citation_time_ms: int = Field(default=0, ge=0)
    total_time_ms: int = Field(default=0, ge=0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class FeedbackType(str, Enum):
    """Feedback type enumeration."""
    POSITIVE = "positive"
    NEGATIVE = "negative"


class Feedback(BaseModel):
    """User feedback on query answer."""
    feedback_id: UUID = Field(default_factory=uuid4)
    query_id: UUID
    feedback_type: FeedbackType
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SyncStatus(str, Enum):
    """Sync job status enumeration."""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SyncError(BaseModel):
    """Error encountered during sync."""
    file_path: str
    error_message: str


class SyncJob(BaseModel):
    """Content synchronization job."""
    sync_id: UUID = Field(default_factory=uuid4)
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    status: SyncStatus = SyncStatus.RUNNING
    files_processed: int = Field(default=0, ge=0)
    files_failed: int = Field(default=0, ge=0)
    error_log: List[SyncError] = Field(default_factory=list)


class TextbookChunkMetadata(BaseModel):
    """Metadata for a textbook content chunk stored in Qdrant."""
    chunk_id: str
    file_path: str
    document_title: str
    heading_hierarchy: List[str]
    section_anchor: str
    chunk_index: int
    overlap_tokens: int
    content_text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
