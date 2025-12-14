"""
Language detection middleware for validating English-only queries.

This middleware detects the language of incoming queries and rejects
non-English queries with a clear error message.
"""

from fastapi import HTTPException, Request
from langdetect import detect, LangDetectException

from src.config.logging import get_logger

logger = get_logger(__name__)


async def validate_query_language(query_text: str) -> None:
    """
    Validate that query text is in English.

    Args:
        query_text: The query text to validate

    Raises:
        HTTPException: If query is not in English

    Example:
        >>> await validate_query_language("What is forward kinematics?")  # OK
        >>> await validate_query_language("¿Qué es la cinemática?")  # Raises HTTPException
    """
    # Skip validation for very short queries (ambiguous)
    if len(query_text.strip()) < 10:
        logger.debug("query_too_short_for_language_detection", length=len(query_text))
        return

    try:
        detected_language = detect(query_text)

        if detected_language != "en":
            logger.warning(
                "non_english_query_detected",
                detected_language=detected_language,
                query_preview=query_text[:50]
            )

            raise HTTPException(
                status_code=400,
                detail={
                    "error": "This chatbot supports English queries only. Please rephrase your question in English.",
                    "error_code": "LANGUAGE_NOT_SUPPORTED",
                    "details": {
                        "detected_language": detected_language,
                        "supported_languages": ["en"]
                    }
                }
            )

        logger.debug("query_language_validated", language="en")

    except LangDetectException as e:
        # Language detection failed (ambiguous or too short)
        # Allow the query through - better to process than reject
        logger.debug(
            "language_detection_failed",
            error=str(e),
            query_preview=query_text[:50]
        )


def is_likely_code_or_technical(text: str) -> bool:
    """
    Check if text is likely code or technical content.

    Code and technical content often fails language detection.
    This function helps avoid false positives.

    Args:
        text: Text to check

    Returns:
        True if likely code/technical, False otherwise

    Example:
        >>> is_likely_code_or_technical("function isPrime(n) { ... }")  # True
        >>> is_likely_code_or_technical("What is a prime number?")  # False
    """
    # Common code indicators
    code_indicators = [
        "function",
        "class",
        "def ",
        "import ",
        "const ",
        "let ",
        "var ",
        "return ",
        "{",
        "}",
        "=>",
        "===",
        "!==",
    ]

    text_lower = text.lower()

    # Count code indicators
    indicator_count = sum(1 for indicator in code_indicators if indicator in text_lower)

    # If 3+ indicators, likely code
    return indicator_count >= 3


async def detect_out_of_scope_query(query_text: str) -> bool:
    """
    Detect if query is out of scope for the textbook.

    This is a placeholder for more sophisticated scope detection.
    In production, this could use semantic similarity to textbook topics.

    Args:
        query_text: The query text

    Returns:
        True if likely out of scope, False otherwise

    Example:
        >>> await detect_out_of_scope_query("What's the weather in Paris?")  # True
        >>> await detect_out_of_scope_query("What is forward kinematics?")  # False
    """
    # Simple keyword-based scope detection
    # In production, replace with semantic similarity check

    out_of_scope_keywords = [
        "weather",
        "stock",
        "news",
        "sports",
        "recipe",
        "movie",
        "celebrity",
        "politics",
    ]

    query_lower = query_text.lower()

    for keyword in out_of_scope_keywords:
        if keyword in query_lower:
            logger.info(
                "out_of_scope_query_detected",
                keyword=keyword,
                query_preview=query_text[:50]
            )
            return True

    return False


__all__ = [
    "validate_query_language",
    "is_likely_code_or_technical",
    "detect_out_of_scope_query",
]
