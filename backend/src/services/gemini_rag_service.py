"""
Gemini RAG Service

Orchestrates the complete RAG pipeline using Gemini embeddings and generation.
Coordinates retrieval, generation, and response formatting.
"""

import time
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from dataclasses import dataclass
import structlog

from src.services.retrieval import get_retrieval_service, RetrievedChunk
from src.services.generation import get_generation_service, SourceCitation

logger = structlog.get_logger(__name__)


@dataclass
class QueryResult:
    """Complete result from RAG pipeline."""
    query_id: UUID
    session_id: UUID
    query_text: str
    answer_text: str
    sources: List[SourceCitation]
    confidence: float
    chunks_retrieved: int
    retrieval_time_ms: int
    generation_time_ms: int
    total_time_ms: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "query_id": str(self.query_id),
            "session_id": str(self.session_id),
            "query": self.query_text,
            "answer": self.answer_text,
            "sources": [s.to_dict() for s in self.sources],
            "confidence": round(self.confidence, 3),
            "chunks_retrieved": self.chunks_retrieved,
            "retrieval_time_ms": self.retrieval_time_ms,
            "generation_time_ms": self.generation_time_ms,
            "total_time_ms": self.total_time_ms
        }


class GeminiRAGService:
    """
    Main service orchestrating Gemini-based RAG pipeline.

    Pipeline:
    1. Query validation
    2. Embedding generation (Gemini)
    3. Vector search (Qdrant)
    4. Response generation (Gemini Pro)
    5. Source citation extraction
    6. Response formatting
    """

    def __init__(self):
        self.retrieval_service = get_retrieval_service()
        self.generation_service = get_generation_service()
        logger.info("Gemini RAG Service initialized")

    async def process_query(
        self,
        query_text: str,
        session_id: UUID,
        top_k: int = 5,
        score_threshold: float = 0.7,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> QueryResult:
        """
        Process a user query through the complete RAG pipeline.

        Args:
            query_text: User's natural language question
            session_id: Conversation session identifier
            top_k: Number of chunks to retrieve
            score_threshold: Minimum similarity threshold
            conversation_history: Optional previous conversation context

        Returns:
            QueryResult with answer, sources, and timing information

        Raises:
            ValueError: If query_text is invalid
            Exception: If pipeline fails
        """
        start_time = time.time()
        query_id = uuid4()

        logger.info(
            "Starting RAG pipeline",
            query_id=str(query_id),
            session_id=str(session_id),
            query_preview=query_text[:50]
        )

        try:
            # Step 1: Validate query
            if not query_text or not query_text.strip():
                raise ValueError("Query text cannot be empty")

            if len(query_text) < 3:
                raise ValueError("Query text too short (minimum 3 characters)")

            if len(query_text) > 1000:
                raise ValueError("Query text too long (maximum 1000 characters)")

            # Step 2: Retrieve relevant chunks
            retrieval_start = time.time()

            chunks = await self.retrieval_service.retrieve(
                query=query_text,
                top_k=top_k,
                score_threshold=score_threshold
            )

            retrieval_time_ms = int((time.time() - retrieval_start) * 1000)

            logger.debug(
                "Retrieval completed",
                chunks_retrieved=len(chunks),
                time_ms=retrieval_time_ms
            )

            # Step 3: Calculate confidence
            confidence = self.retrieval_service.calculate_confidence(chunks)

            # Step 4: Generate response
            generation_start = time.time()

            generated_response = await self.generation_service.generate(
                query=query_text,
                chunks=chunks,
                confidence=confidence,
                conversation_history=conversation_history
            )

            generation_time_ms = int((time.time() - generation_start) * 1000)

            logger.debug(
                "Generation completed",
                answer_length=len(generated_response.answer),
                sources_count=len(generated_response.sources),
                time_ms=generation_time_ms
            )

            # Step 5: Build result
            total_time_ms = int((time.time() - start_time) * 1000)

            result = QueryResult(
                query_id=query_id,
                session_id=session_id,
                query_text=query_text,
                answer_text=generated_response.answer,
                sources=generated_response.sources,
                confidence=confidence,
                chunks_retrieved=len(chunks),
                retrieval_time_ms=retrieval_time_ms,
                generation_time_ms=generation_time_ms,
                total_time_ms=total_time_ms
            )

            logger.info(
                "RAG pipeline completed",
                query_id=str(query_id),
                total_time_ms=total_time_ms,
                confidence=confidence
            )

            return result

        except ValueError as e:
            logger.warning(
                "Query validation failed",
                error=str(e),
                query_preview=query_text[:50]
            )
            raise

        except Exception as e:
            logger.error(
                "RAG pipeline failed",
                error=str(e),
                error_type=type(e).__name__,
                query_id=str(query_id)
            )
            raise

    async def process_batch_queries(
        self,
        queries: List[str],
        session_id: UUID
    ) -> List[QueryResult]:
        """
        Process multiple queries in batch (future optimization).

        Args:
            queries: List of user queries
            session_id: Conversation session identifier

        Returns:
            List of QueryResult objects
        """
        results = []

        for query in queries:
            result = await self.process_query(
                query_text=query,
                session_id=session_id
            )
            results.append(result)

        logger.info(
            "Batch processing completed",
            queries_processed=len(results)
        )

        return results


# Singleton instance
_gemini_rag_service = None


def get_gemini_rag_service() -> GeminiRAGService:
    """Get singleton instance of GeminiRAGService."""
    global _gemini_rag_service
    if _gemini_rag_service is None:
        _gemini_rag_service = GeminiRAGService()
    return _gemini_rag_service
