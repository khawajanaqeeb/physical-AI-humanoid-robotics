"""
Qdrant client wrapper for vector database operations.

This module provides async operations for storing and retrieving
text embeddings from Qdrant Cloud.
"""

from typing import Any

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    SearchRequest,
    VectorParams,
    Filter,
    FieldCondition,
    MatchValue,
)

from src.config.settings import get_settings
from src.config.logging import get_logger

logger = get_logger(__name__)

# Global client instance
_qdrant_client: AsyncQdrantClient | None = None


def get_qdrant_client() -> AsyncQdrantClient:
    """
    Get or create the Qdrant client instance.

    Returns:
        AsyncQdrantClient instance with connection pooling

    Example:
        >>> client = get_qdrant_client()
        >>> await client.search(collection_name="chunks", ...)
    """
    global _qdrant_client

    if _qdrant_client is None:
        settings = get_settings()
        _qdrant_client = AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=30,  # 30 second timeout
        )
        logger.info("qdrant_client_initialized", url=settings.qdrant_url)

    return _qdrant_client


async def create_collection(
    collection_name: str,
    vector_size: int = 768,
    distance: Distance = Distance.COSINE,
) -> None:
    """
    Create a Qdrant collection with specified configuration.

    Args:
        collection_name: Name of the collection
        vector_size: Dimension of vectors (default: 768 for Gemini embedding-001)
        distance: Distance metric (COSINE, EUCLID, or DOT)

    Example:
        >>> await create_collection("textbook_chunks", vector_size=768)
    """
    client = get_qdrant_client()
    settings = get_settings()

    try:
        # Check if collection already exists
        collections = await client.get_collections()
        if collection_name in [c.name for c in collections.collections]:
            logger.info("collection_already_exists", collection=collection_name)
            return

        # Create collection
        await client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=distance),
        )

        # Create payload indexes for faster filtering
        await client.create_payload_index(
            collection_name=collection_name,
            field_name="file_path",
            field_schema="keyword",
        )
        await client.create_payload_index(
            collection_name=collection_name,
            field_name="section_anchor",
            field_schema="keyword",
        )

        logger.info(
            "collection_created",
            collection=collection_name,
            vector_size=vector_size,
            distance=distance.value,
        )
    except Exception as e:
        logger.error("collection_creation_failed", collection=collection_name, error=str(e))
        raise


async def upsert_chunks(
    chunks: list[dict[str, Any]],
    embeddings: list[list[float]],
) -> None:
    """
    Upsert text chunks with embeddings to Qdrant.

    Args:
        chunks: List of chunk metadata dictionaries
        embeddings: List of embedding vectors (must match chunks length)

    Example:
        >>> chunks = [{"chunk_id": "doc1:0", "content_text": "...", ...}]
        >>> embeddings = [[0.1, 0.2, ...], ...]
        >>> await upsert_chunks(chunks, embeddings)
    """
    client = get_qdrant_client()
    settings = get_settings()

    if len(chunks) != len(embeddings):
        raise ValueError("Number of chunks must match number of embeddings")

    # Create point structures
    points = [
        PointStruct(
            id=chunk["chunk_id"],
            vector=embedding,
            payload=chunk,
        )
        for chunk, embedding in zip(chunks, embeddings)
    ]

    try:
        await client.upsert(
            collection_name=settings.qdrant_collection_name,
            points=points,
        )
        logger.info(
            "chunks_upserted",
            collection=settings.qdrant_collection_name,
            count=len(points),
        )
    except Exception as e:
        logger.error("upsert_failed", count=len(points), error=str(e))
        raise


async def search_similar_chunks(
    query_embedding: list[float],
    top_k: int = 5,
    score_threshold: float = 0.7,
    file_path_filter: str | None = None,
) -> list[dict[str, Any]]:
    """
    Search for similar chunks in Qdrant.

    Args:
        query_embedding: Query vector
        top_k: Number of results to return
        score_threshold: Minimum similarity score
        file_path_filter: Optional file path to filter results

    Returns:
        List of chunk metadata with similarity scores

    Example:
        >>> results = await search_similar_chunks(
        ...     query_embedding=[0.1, 0.2, ...],
        ...     top_k=5,
        ...     file_path_filter="docs/chapter-01/intro.md"
        ... )
    """
    client = get_qdrant_client()
    settings = get_settings()

    # Build filter if file_path provided
    query_filter = None
    if file_path_filter:
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="file_path",
                    match=MatchValue(value=file_path_filter),
                )
            ]
        )

    try:
        search_result = await client.query_points(
            collection_name=settings.qdrant_collection_name,
            query=query_embedding,
            limit=top_k,
            score_threshold=score_threshold,
            query_filter=query_filter,
            with_payload=True,
        )

        chunks = [
            {
                **hit.payload,
                "similarity_score": hit.score,
            }
            for hit in search_result.points
        ]

        logger.info(
            "search_completed",
            collection=settings.qdrant_collection_name,
            results_count=len(chunks),
            top_k=top_k,
            threshold=score_threshold,
        )

        return chunks
    except Exception as e:
        logger.error("search_failed", error=str(e))
        raise


async def delete_chunks_by_file_path(file_path: str) -> None:
    """
    Delete all chunks for a specific file.

    Args:
        file_path: File path to match for deletion

    Example:
        >>> await delete_chunks_by_file_path("docs/chapter-01/intro.md")
    """
    client = get_qdrant_client()
    settings = get_settings()

    try:
        await client.delete(
            collection_name=settings.qdrant_collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="file_path",
                        match=MatchValue(value=file_path),
                    )
                ]
            ),
        )
        logger.info("chunks_deleted", file_path=file_path)
    except Exception as e:
        logger.error("deletion_failed", file_path=file_path, error=str(e))
        raise


async def check_qdrant_connection() -> bool:
    """
    Check if Qdrant connection is healthy.

    Returns:
        True if connection is healthy, False otherwise

    Example:
        >>> is_healthy = await check_qdrant_connection()
        >>> print(f"Qdrant: {'ok' if is_healthy else 'error'}")
    """
    try:
        client = get_qdrant_client()
        await client.get_collections()
        return True
    except Exception:
        return False


async def close_qdrant_client() -> None:
    """
    Close Qdrant client connection.

    Call this on application shutdown.
    """
    global _qdrant_client

    if _qdrant_client is not None:
        await _qdrant_client.close()
        _qdrant_client = None
        logger.info("qdrant_client_closed")
