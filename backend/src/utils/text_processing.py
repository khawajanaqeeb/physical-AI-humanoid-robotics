"""
Text processing utilities for content cleaning and normalization.

Provides functions to clean HTML content and prepare text for chunking.
"""

import re
from typing import Optional


def remove_navigation_elements(text: str) -> str:
    """
    Remove navigation-specific patterns from text.

    Args:
        text: Raw text content

    Returns:
        Text with navigation elements removed
    """
    # Common navigation patterns in Docusaurus
    nav_patterns = [
        r"Edit this page",
        r"Previous\s*\n.*?\n",
        r"Next\s*\n.*?\n",
        r"On this page",
        r"Docs\s*\n",
        r"Tutorial\s*\n",
        r"Blog\s*\n",
        r"GitHub\s*\n",
    ]

    for pattern in nav_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    return text


def remove_footer_content(text: str) -> str:
    """
    Remove footer patterns from text.

    Args:
        text: Text content

    Returns:
        Text with footer content removed
    """
    # Common footer patterns
    footer_patterns = [
        r"Copyright\s+©.*",
        r"Built with\s+.*",
        r"Powered by\s+.*",
        r"Last updated.*",
        r"Created by.*",
    ]

    for pattern in footer_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    return text


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.

    - Replaces multiple spaces with single space
    - Replaces multiple newlines with maximum two newlines
    - Removes leading/trailing whitespace

    Args:
        text: Text content

    Returns:
        Text with normalized whitespace
    """
    # Replace multiple spaces with single space
    text = re.sub(r" +", " ", text)

    # Replace more than 2 consecutive newlines with 2 newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Replace tabs with spaces
    text = text.replace("\t", " ")

    # Strip leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)

    # Remove leading/trailing whitespace from entire text
    text = text.strip()

    return text


def remove_code_blocks(text: str) -> str:
    """
    Remove code blocks from text (optional - for semantic content only).

    Args:
        text: Text content

    Returns:
        Text with code blocks removed
    """
    # Remove markdown code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`[^`]+`", "", text)

    return text


def clean_html_artifacts(text: str) -> str:
    """
    Remove HTML artifacts that may remain after parsing.

    Args:
        text: Text content

    Returns:
        Text with HTML artifacts removed
    """
    # Remove HTML entities
    html_entities = {
        "&nbsp;": " ",
        "&amp;": "&",
        "&lt;": "<",
        "&gt;": ">",
        "&quot;": '"',
        "&#39;": "'",
    }

    for entity, char in html_entities.items():
        text = text.replace(entity, char)

    # Remove any remaining HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    return text


def clean_text(
    text: str,
    remove_nav: bool = True,
    remove_footer: bool = True,
    remove_code: bool = False,
) -> str:
    """
    Apply all text cleaning operations.

    Args:
        text: Raw text content
        remove_nav: Whether to remove navigation elements
        remove_footer: Whether to remove footer content
        remove_code: Whether to remove code blocks

    Returns:
        Cleaned and normalized text
    """
    if not text:
        return ""

    # Apply cleaning operations
    if remove_nav:
        text = remove_navigation_elements(text)

    if remove_footer:
        text = remove_footer_content(text)

    if remove_code:
        text = remove_code_blocks(text)

    # Always clean HTML artifacts and normalize whitespace
    text = clean_html_artifacts(text)
    text = normalize_whitespace(text)

    return text


def extract_heading_context(text: str) -> Optional[str]:
    """
    Extract the first heading from text to use as section context.

    Args:
        text: Text content

    Returns:
        First heading found, or None
    """
    # Match markdown headings (# Heading)
    heading_match = re.search(r"^#+\s+(.+)$", text, re.MULTILINE)
    if heading_match:
        return heading_match.group(1).strip()

    return None


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length with suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length (including suffix)
        suffix: Suffix to add when truncating

    Returns:
        Truncated text with suffix if needed
    """
    if len(text) <= max_length:
        return text

    truncate_at = max_length - len(suffix)
    return text[:truncate_at] + suffix
