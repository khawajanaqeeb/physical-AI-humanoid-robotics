"""
Pydantic schemas for authentication requests and responses.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class SignupRequest(BaseModel):
    """Request schema for user signup."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=72, description="Password (8-72 characters, bcrypt limit)")
    software_experience: str = Field(..., description="Software experience level: BEGINNER, INTERMEDIATE, or ADVANCED")
    hardware_experience: str = Field(..., description="Hardware experience level: NONE, BASIC, or ADVANCED")
    interests: list[str] = Field(default_factory=list, description="List of interests (e.g., ['robotics', 'AI'])")

    @field_validator("software_experience")
    @classmethod
    def validate_software_experience(cls, v: str) -> str:
        """Validate software experience level."""
        allowed = {"BEGINNER", "INTERMEDIATE", "ADVANCED"}
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"software_experience must be one of {allowed}")
        return v_upper

    @field_validator("hardware_experience")
    @classmethod
    def validate_hardware_experience(cls, v: str) -> str:
        """Validate hardware experience level."""
        allowed = {"NONE", "BASIC", "ADVANCED"}
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"hardware_experience must be one of {allowed}")
        return v_upper

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets minimum strength requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        # Check for at least one letter and one number
        has_letter = any(c.isalpha() for c in v)
        has_number = any(c.isdigit() for c in v)
        if not (has_letter and has_number):
            raise ValueError("Password must contain at least one letter and one number")
        return v


class SigninRequest(BaseModel):
    """Request schema for user signin."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    """Response schema for authentication tokens."""

    access_token: str = Field(..., description="JWT access token (short-lived)")
    refresh_token: str = Field(..., description="Refresh token for renewing access token")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")
    expires_in: int = Field(..., description="Access token expiration time in seconds")


class AuthResponse(BaseModel):
    """Response schema for successful authentication."""

    user_id: UUID = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User email address")
    tokens: TokenResponse = Field(..., description="Authentication tokens")


class RefreshTokenRequest(BaseModel):
    """Request schema for refreshing access token."""

    refresh_token: str = Field(..., description="Valid refresh token")


class SignoutRequest(BaseModel):
    """Request schema for user signout."""

    refresh_token: str = Field(..., description="Refresh token to invalidate")


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str = Field(..., description="Response message")
