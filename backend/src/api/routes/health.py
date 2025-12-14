"""
Health check API endpoint.

This module provides a health check endpoint that verifies
the status of all system components.
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from src.api.schemas import HealthResponse
from src.database import check_database_connection
from src.clients.qdrant_client import check_qdrant_connection
from src.clients.mcp_client import check_mcp_connection
from src.config.logging import get_logger

# Gemini health check
async def check_gemini_connection() -> bool:
    """Check if Gemini API is accessible."""
    try:
        import google.generativeai as genai
        from src.config.settings import get_settings

        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)

        # Simple API check - list available models
        models = genai.list_models()
        return True
    except Exception:
        return False

logger = get_logger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check the health of all system components.

    This endpoint checks:
    - Database connection (Neon Postgres)
    - Qdrant Cloud connection
    - Google Gemini API connection
    - MCP server accessibility

    Returns:
        HealthResponse with overall status and individual component checks

    Example:
        ```
        GET /health

        Response:
        {
            "status": "healthy",
            "checks": {
                "database": "ok",
                "qdrant": "ok",
                "mcp_server": "ok",
                "gemini_api": "ok"
            },
            "version": "2.0.0"
        }
        ```
    """
    logger.info("health_check_started")

    checks = {}
    all_healthy = True

    # Check database
    try:
        db_healthy = await check_database_connection()
        checks["database"] = "ok" if db_healthy else "error"
        if not db_healthy:
            all_healthy = False
            logger.warning("database_health_check_failed")
    except Exception as e:
        checks["database"] = "error"
        all_healthy = False
        logger.error("database_health_check_error", error=str(e))

    # Check Qdrant
    try:
        qdrant_healthy = await check_qdrant_connection()
        checks["qdrant"] = "ok" if qdrant_healthy else "error"
        if not qdrant_healthy:
            all_healthy = False
            logger.warning("qdrant_health_check_failed")
    except Exception as e:
        checks["qdrant"] = "error"
        all_healthy = False
        logger.error("qdrant_health_check_error", error=str(e))

    # Check MCP Server
    try:
        mcp_healthy = await check_mcp_connection()
        checks["mcp_server"] = "ok" if mcp_healthy else "error"
        if not mcp_healthy:
            all_healthy = False
            logger.warning("mcp_health_check_failed")
    except Exception as e:
        checks["mcp_server"] = "error"
        all_healthy = False
        logger.error("mcp_health_check_error", error=str(e))

    # Check Gemini API
    try:
        gemini_healthy = await check_gemini_connection()
        checks["gemini_api"] = "ok" if gemini_healthy else "error"
        if not gemini_healthy:
            all_healthy = False
            logger.warning("gemini_health_check_failed")
    except Exception as e:
        checks["gemini_api"] = "error"
        all_healthy = False
        logger.error("gemini_health_check_error", error=str(e))

    overall_status = "healthy" if all_healthy else "unhealthy"

    logger.info(
        "health_check_completed",
        status=overall_status,
        checks=checks,
    )

    response_data = {
        "status": overall_status,
        "checks": checks,
        "version": "2.0.0",
    }

    # Return 503 if unhealthy, otherwise 200
    if not all_healthy:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=response_data
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response_data
    )
