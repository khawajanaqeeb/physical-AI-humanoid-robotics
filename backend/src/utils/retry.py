"""
Retry decorators using tenacity for resilient API calls.

Provides exponential backoff retry logic for Cohere and Qdrant operations.
"""

import logging
from functools import wraps
from typing import Callable, Type, Union

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
)

from src.core.exceptions import CohereAPIError, QdrantConnectionError

logger = logging.getLogger(__name__)


def retry_cohere(
    max_attempts: int = 3,
    min_wait: int = 1,
    max_wait: int = 10,
) -> Callable:
    """
    Retry decorator for Cohere API calls.

    Retries on CohereAPIError with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time in seconds between retries
        max_wait: Maximum wait time in seconds between retries

    Returns:
        Decorated function with retry logic

    Example:
        @retry_cohere(max_attempts=3)
        def embed_text(text: str):
            return cohere_client.embed(texts=[text])
    """
    return retry(
        retry=retry_if_exception_type(CohereAPIError),
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )


def retry_qdrant(
    max_attempts: int = 3,
    min_wait: int = 1,
    max_wait: int = 10,
) -> Callable:
    """
    Retry decorator for Qdrant operations.

    Retries on QdrantConnectionError with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time in seconds between retries
        max_wait: Maximum wait time in seconds between retries

    Returns:
        Decorated function with retry logic

    Example:
        @retry_qdrant(max_attempts=3)
        def search_vectors(query_vector: list):
            return qdrant_client.search(collection_name, query_vector)
    """
    return retry(
        retry=retry_if_exception_type(QdrantConnectionError),
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )


def retry_on_exception(
    exception_types: Union[Type[Exception], tuple],
    max_attempts: int = 3,
    min_wait: int = 1,
    max_wait: int = 10,
) -> Callable:
    """
    Generic retry decorator for any exception type.

    Args:
        exception_types: Exception class or tuple of exception classes to retry on
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time in seconds between retries
        max_wait: Maximum wait time in seconds between retries

    Returns:
        Decorated function with retry logic

    Example:
        @retry_on_exception((ConnectionError, TimeoutError), max_attempts=5)
        def fetch_data():
            return requests.get(url)
    """
    return retry(
        retry=retry_if_exception_type(exception_types),
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
