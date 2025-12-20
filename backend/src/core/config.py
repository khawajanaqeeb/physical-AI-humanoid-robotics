"""
Configuration management using pydantic-settings.

Loads and validates environment variables from .env file.
"""

from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Cohere API Configuration
    cohere_api_key: str = Field(
        ...,
        description="Cohere API key from https://dashboard.cohere.com/api-keys",
    )

    # Qdrant Cloud Configuration
    qdrant_url: str = Field(
        ...,
        description="Qdrant cluster URL (e.g., https://your-cluster.qdrant.io)",
    )
    qdrant_api_key: str = Field(
        ...,
        description="Qdrant API key from https://cloud.qdrant.io/",
    )
    qdrant_collection_name: str = Field(
        default="textbook_chunks",
        description="Name of the Qdrant collection for textbook embeddings",
    )

    # Textbook Configuration
    textbook_sitemap_url: str = Field(
        ...,
        description="Sitemap URL for textbook content ingestion",
    )

    # CORS Configuration
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:3001,http://localhost:8080,https://*.vercel.app",
        description="Comma-separated list of allowed CORS origins",
    )

    # API Security
    api_key: Optional[str] = Field(
        default=None,
        description="Optional API key to protect /api/v1/ingest endpoint",
    )

    # Database Configuration (PostgreSQL on Neon)
    database_url: str = Field(
        ...,
        description="PostgreSQL connection string from Neon (postgresql://user:pass@host/db)",
    )

    # Authentication & JWT Configuration
    better_auth_secret: str = Field(
        ...,
        description="Secret key for JWT token signing (64-character hex string)",
        min_length=32,
    )
    access_token_expire_minutes: int = Field(
        default=15,
        description="JWT access token expiration time in minutes",
        ge=1,
        le=60,
    )
    refresh_token_expire_days: int = Field(
        default=7,
        description="Refresh token expiration time in days",
        ge=1,
        le=30,
    )

    # Server Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    @field_validator("cors_origins")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in v.split(",") if origin.strip()]

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the allowed values."""
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v_upper


# Global settings instance (lazy-loaded to avoid circular imports)
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get the global settings instance (singleton pattern).

    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# For backward compatibility
settings = get_settings()
