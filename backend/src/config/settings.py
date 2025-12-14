"""
Application configuration management using Pydantic Settings.

This module loads and validates environment variables for the application.
"""

from functools import lru_cache
from typing import Literal

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

    # Google Gemini Configuration
    gemini_api_key: str = Field(..., description="Google Gemini API key")
    gemini_embedding_model: str = Field(
        default="models/embedding-001",
        description="Gemini embedding model (768 dimensions)"
    )
    gemini_generation_model: str = Field(
        default="gemini-pro",
        description="Gemini model for answer generation"
    )

    # OpenAI Configuration (Legacy - Optional)
    openai_api_key: str | None = Field(None, description="OpenAI API key (legacy)")
    embedding_model: str = Field(
        default="text-embedding-3-large",
        description="OpenAI embedding model (legacy)"
    )
    chat_model: str = Field(
        default="gpt-4",
        description="OpenAI chat model for answer generation (legacy)"
    )

    # Qdrant Configuration
    qdrant_url: str = Field(..., description="Qdrant Cloud URL")
    qdrant_api_key: str = Field(..., description="Qdrant API key")
    qdrant_collection_name: str = Field(
        default="gemini_embeddings",
        description="Qdrant collection name for Gemini 768-dim vectors"
    )

    # Database Configuration
    database_url: str = Field(..., description="PostgreSQL connection URL")

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Ensure database URL uses asyncpg driver."""
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "database_url must use asyncpg driver (postgresql+asyncpg://...)"
            )
        return v

    # MCP Server Configuration
    mcp_server_path: str = Field(..., description="Path to MCP server")
    mcp_server_port: int = Field(default=5000, description="MCP server port")

    # Application Configuration
    api_port: int = Field(default=8000, description="API server port")
    frontend_url: str = Field(
        default="http://localhost:3000",
        description="Frontend URL for CORS"
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )
    json_logs: bool = Field(
        default=False,
        description="Output logs in JSON format"
    )

    # CORS Configuration
    cors_origins: list[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins"
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse comma-separated CORS origins."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # Content Sync Configuration
    docs_path: str = Field(default="../docs", description="Path to documentation directory")
    sync_interval_hours: int = Field(default=6, description="Sync interval in hours")

    # API Authentication
    api_key: str = Field(..., description="API key for admin endpoints")

    # Performance Configuration
    embedding_batch_size: int = Field(
        default=100,
        description="Number of chunks to embed per batch"
    )
    max_concurrent_requests: int = Field(
        default=100,
        description="Maximum concurrent API requests"
    )
    request_timeout_seconds: int = Field(
        default=30,
        description="Request timeout in seconds"
    )

    # RAG Pipeline Configuration
    retrieval_top_k: int = Field(
        default=5,
        description="Number of top chunks to retrieve"
    )
    retrieval_score_threshold: float = Field(
        default=0.7,
        description="Minimum similarity score for retrieval"
    )
    chunk_size_tokens: int = Field(
        default=800,
        description="Target chunk size in tokens"
    )
    chunk_overlap_tokens: int = Field(
        default=160,
        description="Overlap between chunks in tokens"
    )

    # Database Connection Pool
    db_pool_size: int = Field(
        default=20,
        description="Database connection pool size"
    )
    db_max_overflow: int = Field(
        default=10,
        description="Database connection pool max overflow"
    )


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Singleton Settings instance loaded from environment

    Example:
        >>> from config.settings import get_settings
        >>> settings = get_settings()
        >>> print(settings.openai_api_key)
    """
    return Settings()  # type: ignore[call-arg]
