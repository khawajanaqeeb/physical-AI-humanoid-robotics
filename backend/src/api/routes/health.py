"""
Health check API endpoint.

This module provides a health check endpoint that verifies
the status of all system components.
"""

from fastapi import APIRouter, status

from src.api.schemas import HealthResponse
from src.database import check_database_connection
from src.clients.qdrant_client import check_qdrant_connection
from src.clients.openai_client import check_openai_connection
from src.clients.mcp_client import check_mcp_connection
from src.config.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check the health of all system components.

    This endpoint checks:
    - Database connection (Neon Postgres)
    - Qdrant Cloud connection
    - OpenAI API connection
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
                "openai_api": "ok"
            },
            "version": "1.0.0"
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

    # Check OpenAI API
    try:
        openai_healthy = await check_openai_connection()
        checks["openai_api"] = "ok" if openai_healthy else "error"
        if not openai_healthy:
            all_healthy = False
            logger.warning("openai_health_check_failed")
    except Exception as e:
        checks["openai_api"] = "error"
        all_healthy = False
        logger.error("openai_health_check_error", error=str(e))

    overall_status = "healthy" if all_healthy else "unhealthy"

    logger.info(
        "health_check_completed",
        status=overall_status,
        checks=checks,
    )

    response = HealthResponse(
        status=overall_status,
        checks=checks,
        version="1.0.0",
    )

    # Return 503 if unhealthy
    if not all_healthy:
        return response, status.HTTP_503_SERVICE_UNAVAILABLE

    return response
