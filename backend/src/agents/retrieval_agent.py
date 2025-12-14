"""
Retrieval Agent for RAG pipeline.

This agent embeds queries and retrieves relevant chunks from Qdrant
with similarity scoring.
"""

import time
from typing import List, Optional

from src.clients.openai_client import generate_embeddings
from src.clients.qdrant_client import search_similar_chunks
from src.config.logging import get_logger
from src.config.settings import get_settings

logger = get_logger(__name__)


class RetrievalAgent:
    """
    Agent responsible for retrieving relevant document chunks.

    This agent:
    1. Embeds the user query using OpenAI embeddings
    2. Searches Qdrant for similar chunks
    3. Returns ranked chunks with similarity scores
    """

    def __init__(self):
        """Initialize the Retrieval Agent."""
        self.settings = get_settings()
        logger.info("retrieval_agent_initialized")

    async def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None,
        file_path_filter: Optional[str] = None,
    ) -> tuple[List[dict], int]:
        """
        Retrieve relevant chunks for a query.

        Args:
            query: User question
            top_k: Number of results (default: from settings)
            score_threshold: Minimum similarity score (default: from settings)
            file_path_filter: Optional file path to filter results (for text selection context)

        Returns:
            Tuple of (chunks, retrieval_time_ms)
            - chunks: List of chunk dictionaries with content and metadata
            - retrieval_time_ms: Time taken in milliseconds

        Example:
            >>> agent = RetrievalAgent()
            >>> chunks, time_ms = await agent.retrieve("What is forward kinematics?")
            >>> len(chunks)  # Number of chunks retrieved
        """
        start_time = time.time()

        # Use defaults from settings if not provided
        top_k = top_k or self.settings.retrieval_top_k
        score_threshold = score_threshold or self.settings.retrieval_score_threshold

        logger.info(
            "retrieval_started",
            query_preview=query[:50],
            top_k=top_k,
            threshold=score_threshold,
            has_filter=file_path_filter is not None,
        )

        try:
            # Step 1: Embed the query
            query_embeddings = await generate_embeddings(
                texts=[query],
                model=self.settings.embedding_model,
            )

            query_embedding = query_embeddings[0]

            logger.debug(
                "query_embedded",
                embedding_dims=len(query_embedding),
                model=self.settings.embedding_model,
            )

            # Step 2: Search Qdrant for similar chunks
            chunks = await search_similar_chunks(
                query_embedding=query_embedding,
                top_k=top_k,
                score_threshold=score_threshold,
                file_path_filter=file_path_filter,
            )

            retrieval_time_ms = int((time.time() - start_time) * 1000)

            logger.info(
                "retrieval_completed",
                chunks_found=len(chunks),
                retrieval_time_ms=retrieval_time_ms,
                top_score=chunks[0]["similarity_score"] if chunks else 0,
            )

            return chunks, retrieval_time_ms

        except Exception as e:
            retrieval_time_ms = int((time.time() - start_time) * 1000)
            logger.error(
                "retrieval_failed",
                error=str(e),
                retrieval_time_ms=retrieval_time_ms,
            )
            raise

    def extract_context(self, chunks: List[dict]) -> str:
        """
        Extract and format context from retrieved chunks.

        Args:
            chunks: List of chunk dictionaries

        Returns:
            Formatted context string for Answer Agent

        Example:
            >>> context = agent.extract_context(chunks)
            >>> print(context)
            Source: Robotics Fundamentals
            Section: Forward Kinematics
            Content: ...
        """
        if not chunks:
            return "No relevant information found."

        context_parts = []

        for i, chunk in enumerate(chunks, 1):
            context_part = f"""
Source {i}: {chunk['document_title']}
Section: {' > '.join(chunk['heading_hierarchy'])}
Similarity: {chunk['similarity_score']:.2f}

{chunk['content_text']}
"""
            context_parts.append(context_part.strip())

        full_context = "\n\n---\n\n".join(context_parts)

        logger.debug("context_extracted", chunks_count=len(chunks), context_length=len(full_context))

        return full_context


# Singleton instance
_retrieval_agent: Optional[RetrievalAgent] = None


def get_retrieval_agent() -> RetrievalAgent:
    """
    Get or create the Retrieval Agent instance.

    Returns:
        RetrievalAgent singleton instance
    """
    global _retrieval_agent

    if _retrieval_agent is None:
        _retrieval_agent = RetrievalAgent()

    return _retrieval_agent
