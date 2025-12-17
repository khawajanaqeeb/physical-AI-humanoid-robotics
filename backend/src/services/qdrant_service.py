"""
Qdrant service for vector storage and similarity search.

Provides methods for managing collections, upserting vectors, and searching.
"""

from typing import List, Dict, Any, Optional
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    SearchRequest,
    Filter,
)

from src.core.config import settings
from src.core.exceptions import QdrantConnectionError
from src.core.logging_config import get_logger
from src.utils.retry import retry_qdrant

logger = get_logger(__name__)


class QdrantService:
    """
    Service for Qdrant vector database operations.

    Handles collection management, vector upsert, and similarity search.
    """

    # Vector configuration
    VECTOR_DIMENSION = 1024
    DISTANCE_METRIC = Distance.COSINE

    def __init__(self):
        """Initialize Qdrant client and ensure collection exists."""
        try:
            self.client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key,
            )
            self.collection_name = settings.qdrant_collection_name

            logger.info(
                "Qdrant service initialized",
                extra={
                    "collection_name": self.collection_name,
                    "qdrant_url": settings.qdrant_url,
                },
            )

            # Ensure collection exists
            self._initialize_collection()

        except Exception as e:
            logger.error(f"Failed to initialize Qdrant client: {e}", exc_info=True)
            raise QdrantConnectionError(
                message="Failed to initialize Qdrant client",
                details={"error": str(e)},
            )

    def _initialize_collection(self) -> None:
        """
        Initialize collection if it doesn't exist.

        Creates collection with:
        - 1024-dimensional vectors
        - COSINE distance metric
        - on_disk_payload=True for efficient storage
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name in collection_names:
                logger.info(
                    f"Collection '{self.collection_name}' already exists",
                    extra={"collection_name": self.collection_name},
                )
                return

            # Create collection
            self.create_collection()

        except Exception as e:
            logger.error(f"Failed to initialize collection: {e}", exc_info=True)
            raise QdrantConnectionError(
                message="Failed to initialize collection",
                details={
                    "error": str(e),
                    "collection_name": self.collection_name,
                },
            )

    @retry_qdrant(max_attempts=3, min_wait=1, max_wait=10)
    def create_collection(self) -> None:
        """
        Create a new Qdrant collection for textbook chunks.

        Creates collection with COSINE distance and on-disk payload storage.

        Raises:
            QdrantConnectionError: If collection creation fails
        """
        try:
            logger.info(
                f"Creating collection '{self.collection_name}'",
                extra={"collection_name": self.collection_name},
            )

            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.VECTOR_DIMENSION,
                    distance=self.DISTANCE_METRIC,
                    on_disk=False,  # Vectors in memory for fast search
                ),
                on_disk_payload=True,  # Payloads on disk to save memory
            )

            logger.info(
                f"Successfully created collection '{self.collection_name}'",
                extra={
                    "collection_name": self.collection_name,
                    "vector_dimension": self.VECTOR_DIMENSION,
                    "distance_metric": self.DISTANCE_METRIC.value,
                },
            )

        except Exception as e:
            logger.error(f"Failed to create collection: {e}", exc_info=True)
            raise QdrantConnectionError(
                message="Failed to create collection",
                details={
                    "error": str(e),
                    "collection_name": self.collection_name,
                },
            )

    @retry_qdrant(max_attempts=3, min_wait=1, max_wait=10)
    def upsert_vectors(
        self,
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]],
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Upsert vectors with metadata into the collection.

        Args:
            vectors: List of embedding vectors (each 1024 dimensions)
            payloads: List of metadata dictionaries (chunk text, URL, title, etc.)
            ids: Optional list of IDs (UUIDs generated if not provided)

        Returns:
            List of point IDs that were upserted

        Raises:
            QdrantConnectionError: If upsert fails
            ValueError: If vectors and payloads lengths don't match
        """
        if len(vectors) != len(payloads):
            raise ValueError(
                f"Vectors and payloads must have same length: "
                f"{len(vectors)} vs {len(payloads)}"
            )

        if not vectors:
            logger.warning("No vectors to upsert")
            return []

        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid4()) for _ in range(len(vectors))]
        elif len(ids) != len(vectors):
            raise ValueError(
                f"IDs length must match vectors length: "
                f"{len(ids)} vs {len(vectors)}"
            )

        try:
            logger.debug(
                f"Upserting {len(vectors)} vectors",
                extra={"vector_count": len(vectors)},
            )

            # Create points
            points = [
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
                for point_id, vector, payload in zip(ids, vectors, payloads)
            ]

            # Upsert to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )

            logger.info(
                f"Successfully upserted {len(vectors)} vectors",
                extra={"vector_count": len(vectors)},
            )

            return ids

        except Exception as e:
            logger.error(f"Failed to upsert vectors: {e}", exc_info=True)
            raise QdrantConnectionError(
                message="Failed to upsert vectors",
                details={
                    "error": str(e),
                    "vector_count": len(vectors),
                    "collection_name": self.collection_name,
                },
            )

    @retry_qdrant(max_attempts=3, min_wait=1, max_wait=10)
    def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in the collection.

        Args:
            query_vector: Query embedding vector (1024 dimensions)
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score (0.0-1.0)

        Returns:
            List of search results with 'id', 'score', and 'payload' fields

        Raises:
            QdrantConnectionError: If search fails
        """
        try:
            logger.debug(
                f"Searching for top-{limit} results (threshold={score_threshold})",
                extra={
                    "limit": limit,
                    "score_threshold": score_threshold,
                },
            )

            # Use the newer query_points method which is the current standard
            # score_threshold parameter handling - some versions don't accept 0
            actual_score_threshold = score_threshold if score_threshold > 0 else None

            search_result = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit,
                score_threshold=actual_score_threshold,
            )

            results = [
                {
                    "id": str(hit.id),
                    "score": hit.score,
                    "payload": hit.payload,
                }
                for hit in search_result.points
            ]

            logger.info(
                f"Search returned {len(results)} results",
                extra={"result_count": len(results)},
            )

            return results

        except Exception as e:
            logger.error(f"Failed to search vectors: {e}", exc_info=True)
            raise QdrantConnectionError(
                message="Failed to search vectors",
                details={
                    "error": str(e),
                    "collection_name": self.collection_name,
                },
            )


# Global service instance
qdrant_service = QdrantService()
