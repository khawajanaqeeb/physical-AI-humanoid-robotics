"""
Retrieval Service for Gemini RAG

Handles semantic search using Gemini embeddings and Qdrant vector database.
Implements retrieval with ranking, filtering, and metadata enrichment.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import structlog

from src.services.embedding import get_embedding_service
from src.clients.qdrant_client import get_qdrant_client
from src.config.settings import get_settings

logger = structlog.get_logger(__name__)


@dataclass
class RetrievedChunk:
    """Represents a retrieved chunk with metadata and score."""
    chunk_id: str
    chunk_text: str
    file_path: str
    chapter: Optional[str]
    section: Optional[str]
    heading_path: List[str]
    source_url: str
    chunk_index: int
    total_chunks: int
    similarity_score: float
    rank: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "chunk_id": self.chunk_id,
            "chunk_text": self.chunk_text,
            "file_path": self.file_path,
            "chapter": self.chapter,
            "section": self.section,
            "heading_path": self.heading_path,
            "source_url": self.source_url,
            "chunk_index": self.chunk_index,
            "total_chunks": self.total_chunks,
            "similarity_score": self.similarity_score,
            "rank": self.rank
        }


class RetrievalService:
    """
    Service for semantic retrieval using Gemini embeddings and Qdrant.

    Features:
    - Query embedding with Gemini
    - Vector search in Qdrant
    - Result ranking by similarity
    - Metadata enrichment
    - Filtering by chapter/section
    """

    def __init__(self):
        self.embedding_service = get_embedding_service()
        self.settings = get_settings()
        logger.info("Retrieval Service initialized")

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.7,
        file_path_filter: Optional[str] = None
    ) -> List[RetrievedChunk]:
        """
        Retrieve relevant chunks for a query.

        Args:
            query: User's natural language query
            top_k: Number of chunks to retrieve (1-10)
            score_threshold: Minimum similarity score (0.0-1.0)
            file_path_filter: Optional filter by file path

        Returns:
            List of RetrievedChunk objects ranked by similarity

        Raises:
            ValueError: If query is empty or parameters invalid
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if not 1 <= top_k <= 10:
            raise ValueError("top_k must be between 1 and 10")

        if not 0.0 <= score_threshold <= 1.0:
            raise ValueError("score_threshold must be between 0.0 and 1.0")

        logger.info(
            "Starting retrieval",
            query_length=len(query),
            top_k=top_k,
            threshold=score_threshold
        )

        try:
            # Step 1: Embed query using Gemini
            query_embedding = await self.embedding_service.embed_text(
                text=query,
                task_type="retrieval_query"
            )

            logger.debug(
                "Query embedded",
                embedding_dim=len(query_embedding)
            )

            # Step 2: Search Qdrant for similar chunks
            qdrant_client = get_qdrant_client()

            search_results = await qdrant_client.query_points(
                collection_name=self.settings.qdrant_collection_name,
                query=query_embedding,
                limit=top_k,
                score_threshold=score_threshold,
                with_payload=True
            )

            logger.debug(
                "Qdrant search completed",
                results_count=len(search_results.points)
            )

            # Step 3: Convert to RetrievedChunk objects with ranking
            retrieved_chunks = []
            for rank, hit in enumerate(search_results.points, start=1):
                chunk = RetrievedChunk(
                    chunk_id=hit.payload.get("chunk_id", f"unknown_{rank}"),
                    chunk_text=hit.payload.get("chunk_text", ""),
                    file_path=hit.payload.get("file_path", ""),
                    chapter=hit.payload.get("chapter"),
                    section=hit.payload.get("section"),
                    heading_path=hit.payload.get("heading_path", []),
                    source_url=hit.payload.get("source_url", ""),
                    chunk_index=hit.payload.get("chunk_index", 0),
                    total_chunks=hit.payload.get("total_chunks", 1),
                    similarity_score=hit.score,
                    rank=rank
                )
                retrieved_chunks.append(chunk)

            logger.info(
                "Retrieval completed",
                query=query[:50],
                chunks_retrieved=len(retrieved_chunks),
                top_score=retrieved_chunks[0].similarity_score if retrieved_chunks else 0.0
            )

            return retrieved_chunks

        except Exception as e:
            logger.error(
                "Retrieval failed",
                error=str(e),
                query=query[:50]
            )
            raise

    async def retrieve_with_reranking(
        self,
        query: str,
        top_k: int = 5,
        initial_k: int = 20,
        score_threshold: float = 0.7
    ) -> List[RetrievedChunk]:
        """
        Retrieve chunks with two-stage retrieval and reranking.

        Args:
            query: User's natural language query
            top_k: Final number of chunks to return
            initial_k: Initial retrieval size before reranking
            score_threshold: Minimum similarity score

        Returns:
            Reranked list of RetrievedChunk objects
        """
        # First stage: Retrieve more chunks
        chunks = await self.retrieve(
            query=query,
            top_k=initial_k,
            score_threshold=score_threshold
        )

        # Second stage: Rerank by similarity score (already sorted)
        # In future, could add semantic reranking here
        reranked = chunks[:top_k]

        # Update ranks after reranking
        for rank, chunk in enumerate(reranked, start=1):
            chunk.rank = rank

        logger.info(
            "Reranking completed",
            initial_count=len(chunks),
            final_count=len(reranked)
        )

        return reranked

    def calculate_confidence(self, chunks: List[RetrievedChunk]) -> float:
        """
        Calculate confidence score based on retrieval quality.

        Args:
            chunks: Retrieved chunks

        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not chunks:
            return 0.0

        # Confidence based on:
        # 1. Top score (weight: 0.6)
        # 2. Average score (weight: 0.3)
        # 3. Result count (weight: 0.1)

        top_score = chunks[0].similarity_score
        avg_score = sum(c.similarity_score for c in chunks) / len(chunks)
        count_factor = min(len(chunks) / 5.0, 1.0)  # Normalize to 5 chunks

        confidence = (
            top_score * 0.6 +
            avg_score * 0.3 +
            count_factor * 0.1
        )

        logger.debug(
            "Confidence calculated",
            top_score=top_score,
            avg_score=avg_score,
            count=len(chunks),
            confidence=confidence
        )

        return min(confidence, 1.0)


# Singleton instance
_retrieval_service = None


def get_retrieval_service() -> RetrievalService:
    """Get singleton instance of RetrievalService."""
    global _retrieval_service
    if _retrieval_service is None:
        _retrieval_service = RetrievalService()
    return _retrieval_service
