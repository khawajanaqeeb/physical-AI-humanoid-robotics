"""
Gemini Embedding Service

Provides embedding generation using Google's Gemini embedding-001 model.
Supports batch processing with rate limiting and retry logic.
"""

import os
import time
from typing import List, Literal
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog

logger = structlog.get_logger(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Model configuration
EMBEDDING_MODEL = "models/embedding-001"
EMBEDDING_DIMENSION = 768


class GeminiEmbeddingService:
    """
    Service for generating embeddings using Gemini embedding-001 model.

    Features:
    - 768-dimensional embeddings
    - Task-type specific embeddings (document vs query)
    - Batch processing support
    - Rate limiting with exponential backoff
    - Retry logic for transient failures
    """

    def __init__(self):
        self.model = EMBEDDING_MODEL
        self.dimension = EMBEDDING_DIMENSION
        logger.info("Gemini Embedding Service initialized", model=self.model)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def embed_text(
        self,
        text: str,
        task_type: Literal["retrieval_document", "retrieval_query"] = "retrieval_document"
    ) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed
            task_type: Type of task - "retrieval_document" for indexing,
                      "retrieval_query" for user queries

        Returns:
            List of 768 floats representing the embedding vector

        Raises:
            ValueError: If text is empty or invalid
            Exception: If API call fails after retries
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        try:
            logger.debug(
                "Generating embedding",
                text_length=len(text),
                task_type=task_type
            )

            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type=task_type
            )

            embedding = result['embedding']

            # Validate dimension
            if len(embedding) != self.dimension:
                raise ValueError(
                    f"Expected {self.dimension}-dim embedding, got {len(embedding)}"
                )

            logger.debug(
                "Embedding generated successfully",
                dimension=len(embedding)
            )

            return embedding

        except Exception as e:
            logger.error(
                "Failed to generate embedding",
                error=str(e),
                text_preview=text[:100]
            )
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def embed_batch(
        self,
        texts: List[str],
        task_type: Literal["retrieval_document", "retrieval_query"] = "retrieval_document",
        batch_size: int = 10,
        delay_between_batches: float = 1.0
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts with batching and rate limiting.

        Args:
            texts: List of texts to embed
            task_type: Type of task
            batch_size: Number of texts to process per batch (default: 10)
            delay_between_batches: Delay in seconds between batches (default: 1.0)

        Returns:
            List of embedding vectors

        Raises:
            ValueError: If texts list is empty
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")

        logger.info(
            "Starting batch embedding",
            total_texts=len(texts),
            batch_size=batch_size
        )

        embeddings = []

        # Process in batches to respect rate limits
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_num = i // batch_size + 1

            logger.debug(
                "Processing batch",
                batch_num=batch_num,
                batch_size=len(batch)
            )

            # Generate embeddings for batch
            for text in batch:
                embedding = await self.embed_text(text, task_type)
                embeddings.append(embedding)

            # Rate limiting delay between batches
            if i + batch_size < len(texts):
                logger.debug(
                    "Rate limit delay",
                    delay_seconds=delay_between_batches
                )
                time.sleep(delay_between_batches)

        logger.info(
            "Batch embedding completed",
            total_embeddings=len(embeddings)
        )

        return embeddings


# Singleton instance
_embedding_service = None


def get_embedding_service() -> GeminiEmbeddingService:
    """Get singleton instance of GeminiEmbeddingService."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = GeminiEmbeddingService()
    return _embedding_service
