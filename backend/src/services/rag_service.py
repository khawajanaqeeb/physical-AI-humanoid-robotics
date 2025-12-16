"""
RAG (Retrieval-Augmented Generation) service for answering user queries.

Orchestrates query embedding, vector search, answer generation, and citation extraction.
"""

import time
from typing import List, Dict, Any, Optional

from src.core.logging_config import get_logger
from src.models.query_session import QuerySession, SourceCitation
from src.models.chunk import DocumentChunk
from src.services.cohere_service import cohere_service
from src.services.qdrant_service import qdrant_service
from src.utils.text_processing import truncate_text

logger = get_logger(__name__)


class RAGService:
    """
    Service for Retrieval-Augmented Generation.

    Workflow:
    1. Embed user query
    2. Search Qdrant for similar chunks
    3. Generate answer using Cohere with retrieved context
    4. Extract citations from response
    """

    # RAG configuration
    DEFAULT_TOP_K = 5
    DEFAULT_SCORE_THRESHOLD = 0.5
    GENERATION_TEMPERATURE = 0.3
    MAX_GENERATION_TOKENS = 500

    # Response constants
    NOT_FOUND_MESSAGE = "I could not find this information in the textbook."

    def __init__(self):
        """Initialize RAG service."""
        logger.info("RAGService initialized")

    def query_textbook(
        self,
        query_text: str,
        max_results: int = DEFAULT_TOP_K,
        score_threshold: float = DEFAULT_SCORE_THRESHOLD,
    ) -> QuerySession:
        """
        Process complete query workflow.

        Args:
            query_text: User's question
            max_results: Maximum number of chunks to retrieve
            score_threshold: Minimum similarity score (0.0-1.0)

        Returns:
            QuerySession with answer and citations
        """
        start_time = time.time()

        try:
            logger.info(
                "Processing query",
                extra={
                    "query_length": len(query_text),
                    "max_results": max_results,
                    "score_threshold": score_threshold,
                },
            )

            # Step 1: Embed query
            embedding_start = time.time()
            query_embedding = cohere_service.embed(
                texts=[query_text],
                input_type="search_query",
            )[0]
            embedding_time = int((time.time() - embedding_start) * 1000)

            # Step 2: Retrieve similar chunks
            retrieval_start = time.time()
            search_results = qdrant_service.search(
                query_vector=query_embedding,
                limit=max_results,
                score_threshold=score_threshold,
            )
            retrieval_time = int((time.time() - retrieval_start) * 1000)

            logger.debug(
                f"Retrieved {len(search_results)} chunks",
                extra={"result_count": len(search_results)},
            )

            # Check if any results found
            if not search_results:
                # No relevant information found
                total_time = int((time.time() - start_time) * 1000)

                return QuerySession(
                    query_text=query_text,
                    embedding_vector=query_embedding,
                    retrieved_chunks=[],
                    generated_response=self.NOT_FOUND_MESSAGE,
                    source_citations=[],
                    response_time_ms=total_time,
                    retrieval_score_threshold=score_threshold,
                )

            # Convert search results to DocumentChunk objects
            retrieved_chunks = self._results_to_chunks(search_results)

            # Step 3: Generate answer
            generation_start = time.time()
            answer_data = self.generate_answer(
                query=query_text,
                chunks=retrieved_chunks,
            )
            generation_time = int((time.time() - generation_start) * 1000)

            # Step 4: Extract citations
            citation_start = time.time()
            logger.info("Starting citation extraction...")
            citations = self.extract_citations(
                chunks=retrieved_chunks,
                cohere_citations=answer_data.get("citations", []),
                search_results=search_results,
            )
            citation_time = int((time.time() - citation_start) * 1000)
            logger.info(f"Citation extraction completed: {len(citations)} citations")

            total_time = int((time.time() - start_time) * 1000)

            # Create QuerySession
            session = QuerySession(
                query_text=query_text,
                embedding_vector=query_embedding,
                retrieved_chunks=retrieved_chunks,
                generated_response=answer_data.get("answer", ""),
                source_citations=citations,
                response_time_ms=total_time,
                retrieval_score_threshold=score_threshold,
            )

            logger.info(
                "Query completed successfully",
                extra={
                    "session_id": str(session.session_id),
                    "response_time_ms": total_time,
                    "chunks_retrieved": len(retrieved_chunks),
                    "citations": len(citations),
                    "timing": {
                        "embedding_ms": embedding_time,
                        "retrieval_ms": retrieval_time,
                        "generation_ms": generation_time,
                        "citation_ms": citation_time,
                    },
                },
            )

            return session

        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)

            # Return error session
            total_time = int((time.time() - start_time) * 1000)
            return QuerySession(
                query_text=query_text,
                embedding_vector=[0.0] * 1024,  # Placeholder
                retrieved_chunks=[],
                generated_response="",
                source_citations=[],
                response_time_ms=total_time,
                retrieval_score_threshold=score_threshold,
                error=str(e),
            )

    def generate_answer(
        self,
        query: str,
        chunks: List[DocumentChunk],
    ) -> Dict[str, Any]:
        """
        Generate answer using Cohere with retrieved chunks.

        Args:
            query: User's question
            chunks: Retrieved DocumentChunk objects

        Returns:
            dict with 'answer' and 'citations' fields
        """
        # Prepare documents for Cohere
        documents = [
            {
                "text": chunk.content_text,
                "title": chunk.page_title,
                "url": chunk.page_url,
            }
            for chunk in chunks
        ]

        logger.debug(f"Generating answer with {len(documents)} documents")

        # Call Cohere generate
        result = cohere_service.generate(
            query=query,
            documents=documents,
            temperature=self.GENERATION_TEMPERATURE,
            max_tokens=self.MAX_GENERATION_TOKENS,
        )

        return result

    def extract_citations(
        self,
        chunks: List[DocumentChunk],
        cohere_citations: List[Any],
        search_results: List[Dict[str, Any]],
    ) -> List[SourceCitation]:
        """
        Extract citations from Cohere response and retrieved chunks.

        Args:
            chunks: Retrieved DocumentChunk objects
            cohere_citations: Citations from Cohere response
            search_results: Raw search results with scores

        Returns:
            List of SourceCitation objects
        """
        citations = []
        seen_urls = set()

        # Create score lookup
        score_lookup = {
            result["payload"]["chunk_id"]: result["score"]
            for result in search_results
        }

        logger.info(f"Extracting citations from {len(chunks)} chunks, cohere_citations={len(cohere_citations)}")

        # If Cohere provides specific citations, use those
        if cohere_citations:
            logger.info("Using Cohere citations")
            # Create chunk lookup by index (Cohere citations reference document indices)
            chunk_lookup = {i: chunk for i, chunk in enumerate(chunks)}

            for i, cohere_citation in enumerate(cohere_citations):
                # Get document IDs from Cohere citation
                # Cohere citations have 'document_ids' which is a list of document indices
                document_ids = getattr(cohere_citation, 'document_ids', None)

                if i == 0:  # Log first citation details for debugging
                    logger.info(f"First citation: document_ids={document_ids}")

                if not document_ids or len(document_ids) == 0:
                    continue

                # Extract document index from Cohere's format (e.g., 'doc_3' -> 3)
                doc_id_str = document_ids[0]
                try:
                    # Parse 'doc_N' format to extract integer index
                    if isinstance(doc_id_str, str) and doc_id_str.startswith('doc_'):
                        doc_idx = int(doc_id_str.split('_')[1])
                    else:
                        doc_idx = int(doc_id_str)
                except (ValueError, IndexError):
                    logger.warning(f"Could not parse document ID: {doc_id_str}")
                    continue

                if doc_idx in chunk_lookup:
                    chunk = chunk_lookup[doc_idx]

                    # Skip duplicate URLs
                    if chunk.page_url in seen_urls:
                        continue

                    seen_urls.add(chunk.page_url)

                    # Get relevance score
                    relevance_score = score_lookup.get(chunk.chunk_id, 0.0)

                    # Truncate chunk text for preview
                    chunk_preview = truncate_text(
                        text=chunk.content_text,
                        max_length=300,
                        suffix="...",
                    )

                    citation = SourceCitation(
                        page_url=chunk.page_url,
                        page_title=chunk.page_title,
                        chunk_text=chunk_preview,
                        relevance_score=relevance_score,
                    )

                    citations.append(citation)
        else:
            # Fallback: use all chunks if no specific citations from Cohere
            logger.debug("Using fallback citation extraction from all chunks")
            for chunk in chunks:
                try:
                    # Skip duplicate URLs
                    if chunk.page_url in seen_urls:
                        continue

                    seen_urls.add(chunk.page_url)

                    # Get relevance score
                    relevance_score = score_lookup.get(chunk.chunk_id, 0.0)

                    # Truncate chunk text for preview
                    chunk_preview = truncate_text(
                        text=chunk.content_text,
                        max_length=300,
                        suffix="...",
                    )

                    # Ensure chunk_preview is not empty
                    if not chunk_preview or not chunk_preview.strip():
                        logger.warning(f"Empty chunk text for {chunk.chunk_id}, skipping citation")
                        continue

                    # Ensure page_title is not empty
                    page_title = chunk.page_title if chunk.page_title and chunk.page_title.strip() else "Untitled"

                    citation = SourceCitation(
                        page_url=chunk.page_url,
                        page_title=page_title,
                        chunk_text=chunk_preview,
                        relevance_score=relevance_score,
                    )

                    citations.append(citation)
                    logger.debug(f"Added citation for {chunk.page_url}")
                except Exception as e:
                    logger.error(f"Error creating citation for chunk {chunk.chunk_id}: {e}", exc_info=True)
                    continue

        logger.info(f"Extracted {len(citations)} citations")

        return citations

    def _results_to_chunks(
        self,
        search_results: List[Dict[str, Any]],
    ) -> List[DocumentChunk]:
        """
        Convert Qdrant search results to DocumentChunk objects.

        Args:
            search_results: List of search results from Qdrant

        Returns:
            List of DocumentChunk objects
        """
        chunks = []

        for result in search_results:
            payload = result["payload"]

            # Note: embedding_vector not returned from search, use placeholder
            chunk = DocumentChunk(
                chunk_id=payload["chunk_id"],
                content_text=payload["content_text"],
                embedding_vector=[0.0] * 1024,  # Placeholder (not needed for response)
                page_url=payload["page_url"],
                page_title=payload["page_title"],
                section_heading=payload.get("section_heading"),
                chunk_index=payload["chunk_index"],
                character_count=payload["character_count"],
                ingestion_timestamp=payload["ingestion_timestamp"],
            )

            chunks.append(chunk)

        return chunks


# Global service instance
rag_service = RAGService()
