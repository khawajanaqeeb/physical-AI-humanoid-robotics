"""
Answer Agent for RAG pipeline.

This agent synthesizes answers from retrieved context using GPT-4
with strict hallucination prevention.
"""

import time
from typing import Optional

from src.clients.openai_client import generate_chat_completion
from src.config.logging import get_logger
from src.config.settings import get_settings

logger = get_logger(__name__)


class AnswerAgent:
    """
    Agent responsible for generating answers from retrieved context.

    This agent:
    1. Receives user query and retrieved chunks
    2. Uses GPT-4 to synthesize a coherent response
    3. Ensures no hallucination (context-only answers)
    """

    def __init__(self):
        """Initialize the Answer Agent."""
        self.settings = get_settings()
        logger.info("answer_agent_initialized")

        # System prompt for hallucination prevention
        self.system_prompt = """You are a helpful AI assistant for a robotics and AI textbook.

Your task is to answer questions based ONLY on the provided context from the textbook.

CRITICAL RULES:
1. Use ONLY information from the provided context
2. Do NOT add information from your general knowledge
3. If the context doesn't contain enough information to answer the question fully, say so explicitly
4. Be concise and clear
5. Reference specific sections when appropriate

If the question cannot be answered from the context, respond with:
"I don't have enough information in the textbook to answer this question. Please try rephrasing or asking about a topic covered in the textbook."
"""

    async def generate_answer(
        self,
        query: str,
        context: str,
        temperature: float = 0.3,
    ) -> tuple[str, int]:
        """
        Generate an answer from query and context.

        Args:
            query: User question
            context: Retrieved and formatted context
            temperature: Sampling temperature (lower = more deterministic)

        Returns:
            Tuple of (answer, answer_time_ms)
            - answer: Generated answer text
            - answer_time_ms: Time taken in milliseconds

        Example:
            >>> agent = AnswerAgent()
            >>> answer, time_ms = await agent.generate_answer(
            ...     "What is forward kinematics?",
            ...     context="Forward kinematics is..."
            ... )
        """
        start_time = time.time()

        logger.info(
            "answer_generation_started",
            query_preview=query[:50],
            context_length=len(context),
            temperature=temperature,
        )

        try:
            # Build messages for GPT-4
            messages = [
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": f"""Context from textbook:
{context}

Question: {query}

Answer the question based on the context provided above. Be concise and accurate."""
                }
            ]

            # Generate answer using GPT-4
            answer = await generate_chat_completion(
                messages=messages,
                model=self.settings.chat_model,
                temperature=temperature,
                max_tokens=500,  # Keep answers concise
            )

            answer_time_ms = int((time.time() - start_time) * 1000)

            logger.info(
                "answer_generated",
                answer_length=len(answer),
                answer_time_ms=answer_time_ms,
                answer_preview=answer[:100],
            )

            return answer, answer_time_ms

        except Exception as e:
            answer_time_ms = int((time.time() - start_time) * 1000)
            logger.error(
                "answer_generation_failed",
                error=str(e),
                answer_time_ms=answer_time_ms,
            )
            raise

    def validate_answer(self, answer: str, context: str) -> bool:
        """
        Validate that answer doesn't hallucinate.

        This is a simple validation check. In production, you could use
        more sophisticated techniques like fact-checking against context.

        Args:
            answer: Generated answer
            context: Original context

        Returns:
            True if answer appears valid, False if likely hallucinated

        Example:
            >>> is_valid = agent.validate_answer(answer, context)
        """
        # Simple checks:
        # 1. Answer should not be too short (likely a refusal or error)
        # 2. Answer should not claim to have information if context is empty
        # 3. Answer should not be generic (could indicate hallucination)

        if len(answer.strip()) < 20:
            logger.warning("answer_too_short", length=len(answer))
            return False

        if not context or len(context.strip()) < 50:
            # If context is empty, answer should acknowledge this
            insufficient_phrases = [
                "don't have enough information",
                "cannot answer",
                "not enough context",
                "please try rephrasing",
            ]

            if not any(phrase in answer.lower() for phrase in insufficient_phrases):
                logger.warning("answer_claims_knowledge_without_context")
                return False

        logger.debug("answer_validation_passed")
        return True


# Singleton instance
_answer_agent: Optional[AnswerAgent] = None


def get_answer_agent() -> AnswerAgent:
    """
    Get or create the Answer Agent instance.

    Returns:
        AnswerAgent singleton instance
    """
    global _answer_agent

    if _answer_agent is None:
        _answer_agent = AnswerAgent()

    return _answer_agent
