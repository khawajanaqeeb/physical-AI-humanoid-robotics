"""
Text chunking utility for splitting documents into overlapping chunks.

This module provides functions for splitting markdown content into
chunks of 500-800 tokens with 20% overlap (100-160 tokens).
"""

import re
from typing import List, Tuple

from src.config.logging import get_logger

logger = get_logger(__name__)


def estimate_token_count(text: str) -> int:
    """
    Estimate token count for text.

    Uses a simple heuristic: ~4 characters per token (approximation for English).
    For production, use tiktoken for accurate counts.

    Args:
        text: Text to estimate

    Returns:
        Estimated token count

    Example:
        >>> estimate_token_count("Hello world")  # ~3 tokens
        3
    """
    # Simple estimation: 4 characters ≈ 1 token
    return len(text) // 4


def chunk_text(
    text: str,
    target_chunk_size: int = 800,
    overlap_size: int = 160,
) -> List[Tuple[str, int, int]]:
    """
    Split text into overlapping chunks.

    Args:
        text: Text to chunk
        target_chunk_size: Target size in tokens (default: 800)
        overlap_size: Overlap between chunks in tokens (default: 160, ~20% of 800)

    Returns:
        List of (chunk_text, start_index, overlap_tokens) tuples

    Example:
        >>> chunks = chunk_text("Long document...", target_chunk_size=800, overlap_size=160)
        >>> len(chunks)  # Number of chunks created
    """
    if not text or not text.strip():
        return []

    # Split by paragraphs first to preserve structure
    paragraphs = text.split("\n\n")

    chunks = []
    current_chunk = []
    current_token_count = 0
    chunk_index = 0

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        paragraph_tokens = estimate_token_count(paragraph)

        # If adding this paragraph exceeds target, finalize current chunk
        if current_token_count + paragraph_tokens > target_chunk_size and current_chunk:
            # Finalize current chunk
            chunk_text = "\n\n".join(current_chunk)
            chunks.append((chunk_text, chunk_index, 0))  # overlap calculated later
            chunk_index += 1

            # Start new chunk with overlap
            # Calculate how much of the previous chunk to include
            overlap_text = _extract_overlap(chunk_text, overlap_size)
            current_chunk = [overlap_text] if overlap_text else []
            current_token_count = estimate_token_count(overlap_text) if overlap_text else 0

        # Add paragraph to current chunk
        current_chunk.append(paragraph)
        current_token_count += paragraph_tokens

    # Add final chunk if not empty
    if current_chunk:
        chunk_text = "\n\n".join(current_chunk)
        chunks.append((chunk_text, chunk_index, 0))

    # Calculate actual overlap tokens for each chunk
    chunks_with_overlap = []
    for i, (chunk_text, idx, _) in enumerate(chunks):
        if i == 0:
            overlap = 0  # First chunk has no overlap
        else:
            # Overlap is from the end of previous chunk
            overlap = overlap_size

        chunks_with_overlap.append((chunk_text, idx, overlap))

    logger.info(
        "text_chunked",
        total_chunks=len(chunks_with_overlap),
        target_size=target_chunk_size,
        overlap_size=overlap_size
    )

    return chunks_with_overlap


def _extract_overlap(text: str, overlap_tokens: int) -> str:
    """
    Extract the last N tokens worth of text for overlap.

    Args:
        text: Source text
        overlap_tokens: Number of tokens to extract

    Returns:
        Text fragment of approximately overlap_tokens

    Example:
        >>> _extract_overlap("This is a long text...", overlap_tokens=100)
    """
    # Estimate characters needed for overlap tokens
    overlap_chars = overlap_tokens * 4  # ~4 chars per token

    if len(text) <= overlap_chars:
        return text

    # Extract from the end, but try to break at sentence boundary
    overlap_text = text[-overlap_chars:]

    # Find last sentence boundary (. ! ? followed by space)
    sentence_end = max(
        overlap_text.rfind(". "),
        overlap_text.rfind("! "),
        overlap_text.rfind("? "),
    )

    if sentence_end > 0:
        # Start from sentence boundary
        overlap_text = overlap_text[sentence_end + 2:]

    return overlap_text.strip()


def chunk_markdown_with_headings(
    content: str,
    headings: List[dict],
    target_chunk_size: int = 800,
    overlap_size: int = 160,
) -> List[dict]:
    """
    Chunk markdown content while preserving heading context.

    Each chunk includes its heading hierarchy for better context.

    Args:
        content: Markdown content
        headings: List of heading dicts with level, text, anchor
        target_chunk_size: Target size in tokens
        overlap_size: Overlap size in tokens

    Returns:
        List of chunk dictionaries with content and heading hierarchy

    Example:
        >>> headings = [{"level": 1, "text": "Chapter 1", "anchor": "chapter-1"}, ...]
        >>> chunks = chunk_markdown_with_headings(content, headings)
    """
    # Simple implementation: chunk the full content
    # In production, split by sections based on headings

    chunks = chunk_text(content, target_chunk_size, overlap_size)

    chunk_dicts = []

    for chunk_text, idx, overlap in chunks:
        # Determine which heading this chunk falls under
        # For now, use document-level headings (simplified)

        # Extract top-level headings (level 1 and 2)
        hierarchy = [h["text"] for h in headings if h["level"] <= 2]

        chunk_dict = {
            "content": chunk_text,
            "chunk_index": idx,
            "overlap_tokens": overlap,
            "heading_hierarchy": hierarchy if hierarchy else ["Document"],
            "section_anchor": headings[0]["anchor"] if headings else "top",
        }

        chunk_dicts.append(chunk_dict)

    return chunk_dicts


__all__ = [
    "estimate_token_count",
    "chunk_text",
    "chunk_markdown_with_headings",
]
