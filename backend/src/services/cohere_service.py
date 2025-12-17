"""
Cohere service for embeddings and text generation.

Provides methods for embedding text and generating answers with citations.
"""

from typing import List, Dict, Any, Optional

import cohere
from cohere.types import ChatMessage

from src.core.config import settings
from src.core.exceptions import CohereAPIError
from src.core.logging_config import get_logger
from src.utils.retry import retry_cohere

logger = get_logger(__name__)


class CohereService:
    """
    Service for Cohere API operations.

    Handles text embedding and answer generation with automatic retry logic.
    """

    # Model configuration
    EMBEDDING_MODEL = "embed-english-v3.0"
    GENERATION_MODEL = "command-r7b-12-2024"  # Updated to current available model
    EMBEDDING_DIMENSION = 1024

    def __init__(self):
        """Initialize Cohere client with API key from settings."""
        try:
            self.client = cohere.Client(api_key=settings.cohere_api_key)
            logger.info(
                "Cohere service initialized",
                extra={
                    "embedding_model": self.EMBEDDING_MODEL,
                    "generation_model": self.GENERATION_MODEL,
                },
            )
        except Exception as e:
            logger.error(f"Failed to initialize Cohere client: {e}", exc_info=True)
            raise CohereAPIError(
                message="Failed to initialize Cohere client",
                details={"error": str(e)},
            )

    @retry_cohere(max_attempts=3, min_wait=1, max_wait=10)
    def embed(
        self,
        texts: List[str],
        input_type: str = "search_document",
    ) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed
            input_type: Type of input ("search_document" for indexing, "search_query" for queries)

        Returns:
            List of embedding vectors (each 1024 dimensions)

        Raises:
            CohereAPIError: If embedding generation fails
        """
        if not texts:
            raise CohereAPIError(
                message="Cannot embed empty text list",
                details={"texts": texts},
            )

        try:
            logger.debug(
                f"Embedding {len(texts)} texts with input_type={input_type}",
                extra={"text_count": len(texts)},
            )

            response = self.client.embed(
                texts=texts,
                model=self.EMBEDDING_MODEL,
                input_type=input_type,
                embedding_types=["float"],
            )

            embeddings = response.embeddings.float_

            logger.debug(
                f"Successfully embedded {len(embeddings)} texts",
                extra={"embedding_count": len(embeddings)},
            )

            return embeddings

        except (cohere.BadRequestError, cohere.InternalServerError, cohere.ServiceUnavailableError, cohere.UnauthorizedError, cohere.TooManyRequestsError) as e:
            logger.error(f"Cohere embedding error: {e}", exc_info=True)
            raise CohereAPIError(
                message="Failed to generate embeddings",
                details={
                    "error": str(e),
                    "text_count": len(texts),
                    "model": self.EMBEDDING_MODEL,
                },
            )
        except Exception as e:
            logger.error(f"Unexpected error during embedding: {e}", exc_info=True)
            raise CohereAPIError(
                message="Unexpected error during embedding",
                details={"error": str(e)},
            )

    @retry_cohere(max_attempts=3, min_wait=1, max_wait=10)
    def generate(
        self,
        query: str,
        documents: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Generate an answer using retrieved documents with strict grounding.

        Args:
            query: User's question
            documents: List of retrieved documents with "text" field
            temperature: Sampling temperature (0.0-1.0, lower = more deterministic)
            max_tokens: Maximum tokens in response (None = model default)

        Returns:
            dict: Contains "answer" (str) and "citations" (list) fields

        Raises:
            CohereAPIError: If generation fails
        """
        if not query:
            raise CohereAPIError(
                message="Cannot generate answer for empty query",
                details={"query": query},
            )

        try:
            logger.debug(
                f"Generating answer for query with {len(documents)} documents",
                extra={
                    "query_length": len(query),
                    "document_count": len(documents),
                },
            )

            # System prompt enforcing strict grounding
            preamble = (
                "You are an AI assistant for a university-level textbook on Physical AI and Humanoid Robotics. "
                "You must answer questions using ONLY the provided textbook context. "
                "Do not use external knowledge. "
                "Do not make assumptions. "
                "If the answer is not present in the context, you must respond EXACTLY with: "
                "'I could not find this information in the textbook.' "
                "Your tone must be factual, concise, and academic. "
                "Do not mention that you are an AI model, the retrieval process, or any internal systems."
            )

            # Structured prompt with explicit instructions
            structured_message = (
                f"Question: {query}\n\n"
                "Instructions:\n"
                "- Answer ONLY using the provided documents.\n"
                "- Do not add information not present in the documents.\n"
                "- If multiple documents are relevant, synthesize them into one coherent answer.\n"
                "- If the documents do not contain the answer, respond with: 'I could not find this information in the textbook.'\n"
                "- Use an academic, textbook-style tone.\n"
                "- Do not mention the retrieval process or your role as an AI."
            )

            response = self.client.chat(
                message=structured_message,
                documents=documents if documents else None,
                model=self.GENERATION_MODEL,
                temperature=temperature,
                max_tokens=max_tokens,
                preamble=preamble,
            )

            answer_text = response.text
            citations = getattr(response, "citations", None) or []

            logger.debug(
                "Successfully generated answer",
                extra={
                    "answer_length": len(answer_text),
                    "citation_count": len(citations),
                },
            )

            return {
                "answer": answer_text,
                "citations": citations,
            }

        except (cohere.BadRequestError, cohere.InternalServerError, cohere.ServiceUnavailableError, cohere.UnauthorizedError, cohere.TooManyRequestsError) as e:
            logger.error(f"Cohere generation error: {e}", exc_info=True)
            raise CohereAPIError(
                message="Failed to generate answer",
                details={
                    "error": str(e),
                    "query": query[:100],  # Log first 100 chars
                    "model": self.GENERATION_MODEL,
                },
            )
        except Exception as e:
            logger.error(f"Unexpected error during generation: {e}", exc_info=True)
            raise CohereAPIError(
                message="Unexpected error during generation",
                details={"error": str(e)},
            )


# Global service instance
cohere_service = CohereService()
