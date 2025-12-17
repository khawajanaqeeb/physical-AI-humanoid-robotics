"""
IngestionJob and ErrorRecord models for content synchronization tracking.

Represents ingestion operations that crawl textbook and update vector database.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class JobStatus(str, Enum):
    """Ingestion job status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ErrorRecord(BaseModel):
    """
    Detailed error tracking for ingestion jobs.

    Purpose: Debugging and quality assurance during content ingestion.
    """

    page_url: str = Field(
        ...,
        description="URL where error occurred",
    )
    error_type: str = Field(
        ...,
        description="Exception class name or HTTP error code",
    )
    error_message: str = Field(
        ...,
        description="Detailed error description",
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="When error occurred (ISO 8601)",
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "page_url": "https://physical-ai-humanoid-robotics-e3c7.vercel.app/docs/broken",
                "error_type": "HTTPError",
                "error_message": "404 Not Found",
                "timestamp": "2025-12-16T08:02:15Z",
            }
        }


class IngestionJob(BaseModel):
    """
    Content synchronization operation tracking.

    Represents a complete ingestion run from sitemap crawl to vector database update.
    """

    job_id: UUID = Field(
        default_factory=uuid4,
        description="Unique identifier for ingestion job",
    )
    start_time: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="When job started (ISO 8601)",
    )
    end_time: Optional[str] = Field(
        default=None,
        description="When job completed/failed (ISO 8601)",
    )
    pages_processed: int = Field(
        default=0,
        ge=0,
        description="Count of pages successfully processed",
    )
    chunks_created: int = Field(
        default=0,
        ge=0,
        description="Count of new chunks added to Qdrant",
    )
    chunks_updated: int = Field(
        default=0,
        ge=0,
        description="Count of existing chunks updated",
    )
    errors_encountered: List[ErrorRecord] = Field(
        default_factory=list,
        description="Errors during processing",
    )
    status: JobStatus = Field(
        default=JobStatus.PENDING,
        description="Current job status",
    )

    @field_validator("end_time")
    @classmethod
    def validate_end_time(cls, v: Optional[str], info) -> Optional[str]:
        """Validate that end_time is after start_time."""
        if v is None:
            return v

        start_time = info.data.get("start_time")
        if start_time and v < start_time:
            raise ValueError("end_time must be after start_time")

        return v

    @field_validator("status")
    @classmethod
    def validate_status_with_end_time(cls, v: JobStatus, info) -> JobStatus:
        """Validate that status is completed/failed when end_time is set."""
        end_time = info.data.get("end_time")

        if end_time and v not in [JobStatus.COMPLETED, JobStatus.FAILED]:
            raise ValueError(
                "status must be COMPLETED or FAILED when end_time is set"
            )

        if not end_time and v in [JobStatus.COMPLETED, JobStatus.FAILED]:
            raise ValueError(
                "end_time must be set when status is COMPLETED or FAILED"
            )

        return v

    def mark_completed(self) -> None:
        """Mark job as completed and set end time."""
        self.status = JobStatus.COMPLETED
        self.end_time = datetime.utcnow().isoformat() + "Z"

    def mark_failed(self, error_message: str) -> None:
        """
        Mark job as failed and set end time.

        Args:
            error_message: Reason for failure
        """
        self.status = JobStatus.FAILED
        self.end_time = datetime.utcnow().isoformat() + "Z"

        # Add general error record
        self.errors_encountered.append(
            ErrorRecord(
                page_url="N/A",
                error_type="JobFailure",
                error_message=error_message,
            )
        )

    def add_error(
        self,
        page_url: str,
        error_type: str,
        error_message: str,
    ) -> None:
        """
        Add an error record to the job.

        Args:
            page_url: URL where error occurred
            error_type: Exception class name or HTTP error code
            error_message: Detailed error description
        """
        self.errors_encountered.append(
            ErrorRecord(
                page_url=page_url,
                error_type=error_type,
                error_message=error_message,
            )
        )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "job_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                "start_time": "2025-12-16T08:00:00Z",
                "end_time": "2025-12-16T08:07:30Z",
                "pages_processed": 150,
                "chunks_created": 1250,
                "chunks_updated": 0,
                "errors_encountered": [
                    {
                        "page_url": "https://physical-ai-humanoid-robotics-e3c7.vercel.app/docs/broken",
                        "error_type": "HTTPError",
                        "error_message": "404 Not Found",
                        "timestamp": "2025-12-16T08:02:15Z",
                    }
                ],
                "status": "completed",
            }
        }
