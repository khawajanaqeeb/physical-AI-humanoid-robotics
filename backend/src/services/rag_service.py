"""
RAG Service - Orchestrates the multi-agent RAG pipeline.

This service coordinates Retrieval → Answer → Citation agents
to process user queries and generate responses.
"""

import time
from typing import Optional
from uuid import UUID

from src.agents.retrieval_agent import get_retrieval_agent
from src.agents.answer_agent import get_answer_agent
from src.agents.citation_agent import get_citation_agent
from src.models import Query, Citation
from src.middleware.language_validator import validate_query_language, detect_out_of_scope_query
from src.config.logging import get_logger
from fastapi import HTTPException

logger = get_logger(__name__)


class RAGService:
    """
    Service that orchestrates the RAG pipeline.

    Pipeline flow:
    1. Validate language (English only)
    2. Retrieval Agent: Get relevant chunks
    3. Answer Agent: Generate answer from chunks
    4. Citation Agent: Create citations
    5. Return response with timing
    """

    def __init__(self):
        """Initialize RAG Service with all agents."""
        self.retrieval_agent = get_retrieval_agent()
        self.answer_agent = get_answer_agent()
        self.citation_agent = get_citation_agent()
        logger.info("rag_service_initialized")

    async def process_query(
        self,
        query_text: str,
        session_id: UUID,
        selected_text: Optional[str] = None,
    ) -> Query:
        """
        Process a user query through the RAG pipeline.

        Args:
            query_text: User question
            session_id: Browser session UUID
            selected_text: Optional text selection for context

        Returns:
            Query object with answer, citations, and timing

        Raises:
            HTTPException: If query validation fails

        Example:
            >>> service = RAGService()
            >>> result = await service.process_query(
            ...     "What is forward kinematics?",
            ...     session_id=UUID("...")
            ... )
            >>> print(result.answer_text)
        """
        pipeline_start = time.time()

        logger.info(
            "rag_pipeline_started",
            session_id=str(session_id),
            query_preview=query_text[:50],
            has_selection=selected_text is not None,
        )

        try:
            # Step 0: Validate language
            await validate_query_language(query_text)

            # Step 0.5: Check if query is out of scope
            is_out_of_scope = await detect_out_of_scope_query(query_text)
            if is_out_of_scope:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "This question is outside the scope of the textbook. Please ask about robotics, AI, or related topics covered in the textbook.",
                        "error_code": "OUT_OF_SCOPE",
                    }
                )

            # Step 1: Retrieval Agent - Get relevant chunks
            file_path_filter = None
            if selected_text:
                # If text selection is provided, we could extract file path
                # For now, just use it as additional context in the query
                logger.debug("text_selection_provided", selection_preview=selected_text[:50])

            chunks, retrieval_time_ms = await self.retrieval_agent.retrieve(
                query=query_text,
                file_path_filter=file_path_filter,
            )

            if not chunks:
                # No relevant chunks found
                logger.warning("no_chunks_retrieved", query_preview=query_text[:50])

                return Query(
                    query_id=UUID(),
                    query_text=query_text,
                    user_session_id=session_id,
                    selected_text=selected_text,
                    retrieved_chunk_ids=[],
                    answer_text="I couldn't find relevant information in the textbook to answer this question. Please try rephrasing or asking about a topic covered in the textbook.",
                    citations=[],
                    similarity_scores=[],
                    retrieval_time_ms=retrieval_time_ms,
                    answer_time_ms=0,
                    citation_time_ms=0,
                    total_time_ms=int((time.time() - pipeline_start) * 1000),
                )

            # Extract context for Answer Agent
            context = self.retrieval_agent.extract_context(chunks)

            # Extract chunk IDs and similarity scores
            chunk_ids = [chunk["chunk_id"] for chunk in chunks]
            similarity_scores = [chunk["similarity_score"] for chunk in chunks]

            # Step 2: Answer Agent - Generate answer
            answer, answer_time_ms = await self.answer_agent.generate_answer(
                query=query_text,
                context=context,
            )

            # Validate answer
            is_valid = self.answer_agent.validate_answer(answer, context)
            if not is_valid:
                logger.warning("answer_validation_failed")
                # Could implement retry logic here

            # Step 3: Citation Agent - Generate citations
            citations, citation_time_ms = await self.citation_agent.generate_citations(
                answer=answer,
                source_chunks=chunks,
            )

            # Calculate total time
            total_time_ms = int((time.time() - pipeline_start) * 1000)

            # Create Query object
            query_result = Query(
                query_text=query_text,
                user_session_id=session_id,
                selected_text=selected_text,
                retrieved_chunk_ids=chunk_ids,
                answer_text=answer,
                citations=citations,
                similarity_scores=similarity_scores,
                retrieval_time_ms=retrieval_time_ms,
                answer_time_ms=answer_time_ms,
                citation_time_ms=citation_time_ms,
                total_time_ms=total_time_ms,
            )

            logger.info(
                "rag_pipeline_completed",
                query_id=str(query_result.query_id),
                session_id=str(session_id),
                chunks_retrieved=len(chunks),
                citations_generated=len(citations),
                total_time_ms=total_time_ms,
            )

            return query_result

        except HTTPException:
            # Re-raise HTTP exceptions (validation errors)
            raise

        except Exception as e:
            total_time_ms = int((time.time() - pipeline_start) * 1000)
            logger.error(
                "rag_pipeline_failed",
                error=str(e),
                error_type=type(e).__name__,
                total_time_ms=total_time_ms,
            )
            raise


# Singleton instance
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """
    Get or create the RAG Service instance.

    Returns:
        RAGService singleton instance
    """
    global _rag_service

    if _rag_service is None:
        _rag_service = RAGService()

    return _rag_service
