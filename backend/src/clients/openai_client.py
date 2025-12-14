"""
OpenAI client wrapper for embeddings and chat completions.

This module provides async operations for generating embeddings
and chat completions using OpenAI's API.
"""

from typing import Any

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config.settings import get_settings
from src.config.logging import get_logger

logger = get_logger(__name__)

# Global client instance
_openai_client: AsyncOpenAI | None = None


def get_openai_client() -> AsyncOpenAI:
    """
    Get or create the OpenAI client instance.

    Returns:
        AsyncOpenAI client instance

    Example:
        >>> client = get_openai_client()
        >>> response = await client.embeddings.create(...)
    """
    global _openai_client

    if _openai_client is None:
        settings = get_settings()
        _openai_client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=60.0,  # 60 second timeout
        )
        logger.info("openai_client_initialized")

    return _openai_client


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True,
)
async def generate_embeddings(
    texts: list[str],
    model: str | None = None,
) -> list[list[float]]:
    """
    Generate embeddings for a list of texts with retry logic.

    Args:
        texts: List of text strings to embed
        model: Embedding model name (default: from settings)

    Returns:
        List of embedding vectors

    Raises:
        Exception: If embedding generation fails after retries

    Example:
        >>> texts = ["Hello world", "Another text"]
        >>> embeddings = await generate_embeddings(texts)
        >>> len(embeddings)  # 2
        >>> len(embeddings[0])  # 3072 for text-embedding-3-large
    """
    client = get_openai_client()
    settings = get_settings()

    model = model or settings.embedding_model

    try:
        logger.debug("generating_embeddings", count=len(texts), model=model)

        response = await client.embeddings.create(
            model=model,
            input=texts,
        )

        embeddings = [item.embedding for item in response.data]

        logger.info(
            "embeddings_generated",
            count=len(embeddings),
            model=model,
            total_tokens=response.usage.total_tokens,
        )

        return embeddings
    except Exception as e:
        logger.error("embedding_generation_failed", count=len(texts), error=str(e))
        raise


async def generate_embeddings_batch(
    texts: list[str],
    batch_size: int | None = None,
    model: str | None = None,
) -> list[list[float]]:
    """
    Generate embeddings in batches to handle large lists.

    Args:
        texts: List of text strings to embed
        batch_size: Number of texts per batch (default: from settings)
        model: Embedding model name (default: from settings)

    Returns:
        List of embedding vectors

    Example:
        >>> texts = ["Text 1", "Text 2", ..., "Text 200"]
        >>> embeddings = await generate_embeddings_batch(texts, batch_size=100)
    """
    settings = get_settings()
    batch_size = batch_size or settings.embedding_batch_size

    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_embeddings = await generate_embeddings(batch, model=model)
        all_embeddings.extend(batch_embeddings)

    return all_embeddings


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True,
)
async def generate_chat_completion(
    messages: list[dict[str, str]],
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int | None = None,
) -> str:
    """
    Generate a chat completion with retry logic.

    Args:
        messages: List of message dictionaries with "role" and "content"
        model: Chat model name (default: from settings)
        temperature: Sampling temperature (0.0 to 2.0)
        max_tokens: Maximum tokens to generate

    Returns:
        Generated response text

    Example:
        >>> messages = [
        ...     {"role": "system", "content": "You are a helpful assistant."},
        ...     {"role": "user", "content": "Explain quantum computing."}
        ... ]
        >>> response = await generate_chat_completion(messages)
    """
    client = get_openai_client()
    settings = get_settings()

    model = model or settings.chat_model

    try:
        logger.debug("generating_chat_completion", model=model, messages_count=len(messages))

        response = await client.chat.completions.create(
            model=model,
            messages=messages,  # type: ignore[arg-type]
            temperature=temperature,
            max_tokens=max_tokens,
        )

        answer = response.choices[0].message.content or ""

        logger.info(
            "chat_completion_generated",
            model=model,
            prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
            completion_tokens=response.usage.completion_tokens if response.usage else 0,
            total_tokens=response.usage.total_tokens if response.usage else 0,
        )

        return answer
    except Exception as e:
        logger.error("chat_completion_failed", error=str(e))
        raise


async def check_openai_connection() -> bool:
    """
    Check if OpenAI API connection is healthy.

    Returns:
        True if connection is healthy, False otherwise

    Example:
        >>> is_healthy = await check_openai_connection()
        >>> print(f"OpenAI: {'ok' if is_healthy else 'error'}")
    """
    try:
        # Try a minimal embedding request
        await generate_embeddings(["test"], model="text-embedding-3-small")
        return True
    except Exception:
        return False


def close_openai_client() -> None:
    """
    Close OpenAI client (cleanup placeholder).

    The AsyncOpenAI client doesn't require explicit closing,
    but this function is provided for consistency.
    """
    global _openai_client
    _openai_client = None
    logger.info("openai_client_closed")
