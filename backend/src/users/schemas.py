"""
Pydantic schemas for user profiles and management.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserProfileResponse(BaseModel):
    """Response schema for user profile."""

    user_id: UUID = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User email address")
    software_experience: str = Field(..., description="Software experience level")
    hardware_experience: str = Field(..., description="Hardware experience level")
    interests: list[str] = Field(..., description="List of user interests")
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")

    class Config:
        from_attributes = True  # For SQLAlchemy model compatibility


class UpdateProfileRequest(BaseModel):
    """Request schema for updating user profile."""

    software_experience: Optional[str] = Field(None, description="Software experience level: BEGINNER, INTERMEDIATE, or ADVANCED")
    hardware_experience: Optional[str] = Field(None, description="Hardware experience level: NONE, BASIC, or ADVANCED")
    interests: Optional[list[str]] = Field(None, description="List of interests (e.g., ['robotics', 'AI'])")

    @field_validator("software_experience", mode="before")
    @classmethod
    def validate_software_experience(cls, v: Optional[str]) -> Optional[str]:
        """Validate software experience level if provided."""
        if v is None:
            return v
        allowed = {"BEGINNER", "INTERMEDIATE", "ADVANCED"}
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"software_experience must be one of {allowed}")
        return v_upper

    @field_validator("hardware_experience", mode="before")
    @classmethod
    def validate_hardware_experience(cls, v: Optional[str]) -> Optional[str]:
        """Validate hardware experience level if provided."""
        if v is None:
            return v
        allowed = {"NONE", "BASIC", "ADVANCED"}
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"hardware_experience must be one of {allowed}")
        return v_upper

    class Config:
        # Allow partial updates
        exclude_none = True


class ChatbotQueryRequest(BaseModel):
    """Request schema for chatbot query (with optional personalization)."""

    query: str = Field(..., min_length=1, max_length=5000, description="User question")
    selected_text: Optional[str] = Field(None, description="Optional selected text for context")


class ChatbotQueryResponse(BaseModel):
    """Response schema for chatbot query."""

    answer: str = Field(..., description="Generated answer")
    citations: list[dict] = Field(..., description="Source citations")
    personalization_applied: bool = Field(default=False, description="Whether personalization was applied")

    class Config:
        from_attributes = True
