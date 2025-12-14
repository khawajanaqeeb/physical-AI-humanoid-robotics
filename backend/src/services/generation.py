"""
Response Generation Service using Gemini Pro

Generates natural language responses based on retrieved context.
Implements prompt engineering for accurate, grounded answers with citations.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import os
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog

from src.services.retrieval import RetrievedChunk

logger = structlog.get_logger(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Model configuration
GENERATION_MODEL = "gemini-pro"


@dataclass
class SourceCitation:
    """Represents a source citation for an answer."""
    chapter: str
    section: Optional[str]
    source_url: str
    relevance_score: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "chapter": self.chapter or "Unknown",
            "section": self.section,
            "source_url": self.source_url,
            "relevance_score": round(self.relevance_score, 3)
        }


@dataclass
class GeneratedResponse:
    """Represents a generated response with metadata."""
    answer: str
    sources: List[SourceCitation]
    confidence: float
    model_used: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "answer": self.answer,
            "sources": [s.to_dict() for s in self.sources],
            "confidence": round(self.confidence, 3),
            "model_used": self.model_used
        }


class GenerationService:
    """
    Service for generating responses using Gemini Pro.

    Features:
    - Context-grounded response generation
    - Source citation extraction
    - Low-confidence handling
    - Prompt engineering for accuracy
    - Retry logic with exponential backoff
    """

    def __init__(self, model_name: str = GENERATION_MODEL):
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        logger.info("Generation Service initialized", model=model_name)

    def _build_prompt(
        self,
        query: str,
        chunks: List[RetrievedChunk],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Build prompt for Gemini Pro with retrieved context.

        Args:
            query: User's question
            chunks: Retrieved context chunks
            conversation_history: Optional conversation history

        Returns:
            Formatted prompt string
        """
        # Build context from chunks
        context_parts = []
        for idx, chunk in enumerate(chunks, 1):
            context_parts.append(f"[Source {idx}]")
            if chunk.chapter:
                context_parts.append(f"Chapter: {chunk.chapter}")
            if chunk.section:
                context_parts.append(f"Section: {chunk.section}")
            context_parts.append(f"Content: {chunk.chunk_text}")
            context_parts.append("")  # Blank line

        context_text = "\n".join(context_parts)

        # Build conversation context if provided
        history_text = ""
        if conversation_history:
            history_parts = []
            for exchange in conversation_history[-3:]:  # Last 3 exchanges
                history_parts.append(f"User: {exchange['user']}")
                history_parts.append(f"Assistant: {exchange['assistant']}")
            history_text = "\n\n".join(history_parts)

        # Build full prompt
        prompt = f"""You are a helpful assistant answering questions about a technical book.

Context from the book:
{context_text}

"""

        if history_text:
            prompt += f"""Conversation history:
{history_text}

"""

        prompt += f"""User question: {query}

Instructions:
1. Answer the question using ONLY information from the provided context above
2. Cite specific chapters and sections in your answer when relevant
3. If the context doesn't contain enough information to fully answer the question, say "I don't have enough information in the book to answer this question fully"
4. Do not make up or infer information not present in the context
5. Be concise but complete in your answer
6. If referencing sources, use [Source X] notation

Answer:"""

        return prompt

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def generate(
        self,
        query: str,
        chunks: List[RetrievedChunk],
        confidence: float,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> GeneratedResponse:
        """
        Generate response based on retrieved chunks.

        Args:
            query: User's question
            chunks: Retrieved context chunks
            confidence: Retrieval confidence score
            conversation_history: Optional conversation history

        Returns:
            GeneratedResponse with answer and citations

        Raises:
            ValueError: If chunks is empty or query invalid
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        # Handle low-confidence case
        if confidence < 0.5 or not chunks:
            logger.warning(
                "Low confidence retrieval",
                confidence=confidence,
                chunks_count=len(chunks)
            )
            return GeneratedResponse(
                answer="I don't have enough information in the book to answer this question confidently. Could you rephrase your question or ask about a different topic covered in the book?",
                sources=[],
                confidence=confidence,
                model_used=self.model_name
            )

        logger.info(
            "Generating response",
            query_length=len(query),
            chunks_count=len(chunks),
            confidence=confidence
        )

        try:
            # Build prompt
            prompt = self._build_prompt(query, chunks, conversation_history)

            logger.debug(
                "Prompt constructed",
                prompt_length=len(prompt)
            )

            # Generate response
            response = self.model.generate_content(prompt)

            answer_text = response.text

            logger.debug(
                "Response generated",
                answer_length=len(answer_text)
            )

            # Extract source citations from chunks
            sources = self._extract_sources(chunks)

            # Create response object
            generated_response = GeneratedResponse(
                answer=answer_text,
                sources=sources,
                confidence=confidence,
                model_used=self.model_name
            )

            logger.info(
                "Generation completed",
                answer_length=len(answer_text),
                sources_count=len(sources)
            )

            return generated_response

        except Exception as e:
            logger.error(
                "Generation failed",
                error=str(e),
                query=query[:50]
            )
            raise

    def _extract_sources(self, chunks: List[RetrievedChunk]) -> List[SourceCitation]:
        """
        Extract source citations from retrieved chunks.

        Args:
            chunks: Retrieved chunks with metadata

        Returns:
            List of unique source citations
        """
        citations = []
        seen_sources = set()

        for chunk in chunks:
            # Create unique key for deduplication
            source_key = (chunk.chapter or "", chunk.source_url)

            if source_key not in seen_sources:
                citation = SourceCitation(
                    chapter=chunk.chapter or "Unknown Chapter",
                    section=chunk.section,
                    source_url=chunk.source_url,
                    relevance_score=chunk.similarity_score
                )
                citations.append(citation)
                seen_sources.add(source_key)

        # Sort by relevance
        citations.sort(key=lambda c: c.relevance_score, reverse=True)

        # Limit to top 5 sources
        return citations[:5]

    async def generate_with_streaming(
        self,
        query: str,
        chunks: List[RetrievedChunk],
        confidence: float
    ):
        """
        Generate response with streaming support (future enhancement).

        Args:
            query: User's question
            chunks: Retrieved context chunks
            confidence: Retrieval confidence score

        Yields:
            Response chunks as they're generated
        """
        # Placeholder for streaming implementation
        # Gemini API supports streaming but requires different setup
        logger.warning("Streaming not yet implemented, falling back to regular generation")
        response = await self.generate(query, chunks, confidence)
        yield response.answer


# Singleton instance
_generation_service = None


def get_generation_service() -> GenerationService:
    """Get singleton instance of GenerationService."""
    global _generation_service
    if _generation_service is None:
        _generation_service = GenerationService()
    return _generation_service
