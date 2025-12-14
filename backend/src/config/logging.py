"""
Structured logging configuration using structlog.

This module sets up structured logging with JSON formatting for production
and human-readable formatting for development.
"""

import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, Processor


def add_log_level(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add log level to the event dictionary."""
    if method_name == "warn":
        # Ensure "warn" is converted to "warning"
        method_name = "warning"
    event_dict["level"] = method_name.upper()
    return event_dict


def configure_logging(log_level: str = "INFO", json_logs: bool = False) -> None:
    """
    Configure structured logging for the application.

    Args:
        log_level: The minimum log level to output (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: If True, output logs in JSON format. If False, use console format.
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Define processors for structlog
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if json_logs:
        # Production: JSON formatting
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer()
        ]
    else:
        # Development: Console formatting
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.

    Args:
        name: The name of the logger (typically __name__)

    Returns:
        A configured structlog logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("user_query_processed",
        ...             query_id="123",
        ...             duration_ms=45.2)
    """
    return structlog.get_logger(name)


# Example usage functions for common logging patterns
def log_query_processing(
    logger: structlog.stdlib.BoundLogger,
    query_id: str,
    session_id: str,
    query_text: str,
    retrieval_time_ms: int,
    answer_time_ms: int,
    citation_time_ms: int,
    total_time_ms: int,
) -> None:
    """Log a completed query processing event."""
    logger.info(
        "query_processed",
        query_id=query_id,
        session_id=session_id,
        query_length=len(query_text),
        retrieval_time_ms=retrieval_time_ms,
        answer_time_ms=answer_time_ms,
        citation_time_ms=citation_time_ms,
        total_time_ms=total_time_ms,
    )


def log_sync_job(
    logger: structlog.stdlib.BoundLogger,
    sync_id: str,
    status: str,
    files_processed: int,
    files_failed: int,
    duration_seconds: float,
) -> None:
    """Log a completed sync job event."""
    logger.info(
        "sync_job_completed",
        sync_id=sync_id,
        status=status,
        files_processed=files_processed,
        files_failed=files_failed,
        duration_seconds=duration_seconds,
    )


def log_api_request(
    logger: structlog.stdlib.BoundLogger,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    user_agent: str | None = None,
) -> None:
    """Log an API request event."""
    logger.info(
        "api_request",
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=duration_ms,
        user_agent=user_agent,
    )
