"""
Chunking service for semantic text segmentation.

Implements recursive semantic chunking with configurable chunk size and overlap.
"""

import re
from typing import List, Optional, Tuple

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class ChunkingService:
    """
    Service for splitting text into semantically coherent chunks.

    Implements recursive chunking strategy with:
    - Target chunk size: 500-800 characters
    - Overlap: 100 characters between consecutive chunks
    - Heading context preservation
    """

    # Chunking configuration
    MIN_CHUNK_SIZE = 500
    MAX_CHUNK_SIZE = 800
    CHUNK_OVERLAP = 100

    # Splitting delimiters (in order of preference)
    DELIMITERS = [
        "\n\n",  # Paragraph breaks (highest priority)
        "\n",    # Line breaks
        ". ",    # Sentence boundaries
        ", ",    # Clause boundaries
        " ",     # Word boundaries
    ]

    def __init__(
        self,
        min_chunk_size: int = MIN_CHUNK_SIZE,
        max_chunk_size: int = MAX_CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP,
    ):
        """
        Initialize chunking service with configuration.

        Args:
            min_chunk_size: Minimum characters per chunk
            max_chunk_size: Maximum characters per chunk
            chunk_overlap: Overlap between consecutive chunks
        """
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.chunk_overlap = chunk_overlap

        logger.info(
            "ChunkingService initialized",
            extra={
                "min_chunk_size": min_chunk_size,
                "max_chunk_size": max_chunk_size,
                "chunk_overlap": chunk_overlap,
            },
        )

    def chunk_text(
        self,
        text: str,
        preserve_heading: Optional[str] = None,
    ) -> List[str]:
        """
        Split text into semantic chunks.

        Args:
            text: Text content to chunk
            preserve_heading: Optional heading to prepend to each chunk

        Returns:
            List of text chunks (500-800 characters each)
        """
        if not text:
            return []

        # Prepend heading if provided
        if preserve_heading:
            text = f"{preserve_heading}\n\n{text}"

        chunks = self._recursive_split(text)

        logger.debug(
            f"Chunked text into {len(chunks)} chunks",
            extra={"chunk_count": len(chunks)},
        )

        return chunks

    def _recursive_split(
        self,
        text: str,
        delimiter_index: int = 0,
    ) -> List[str]:
        """
        Recursively split text using progressively finer delimiters.

        Args:
            text: Text to split
            delimiter_index: Current delimiter index in DELIMITERS

        Returns:
            List of text chunks
        """
        # Base case: text is within acceptable range
        if len(text) <= self.max_chunk_size:
            if len(text) >= self.min_chunk_size or delimiter_index >= len(self.DELIMITERS):
                return [text.strip()] if text.strip() else []

        # Base case: no more delimiters to try, force split
        if delimiter_index >= len(self.DELIMITERS):
            return self._force_split(text)

        # Try to split using current delimiter
        delimiter = self.DELIMITERS[delimiter_index]
        splits = text.split(delimiter)

        # If no split occurred, try next delimiter
        if len(splits) == 1:
            return self._recursive_split(text, delimiter_index + 1)

        # Merge splits into chunks
        chunks = []
        current_chunk = ""

        for i, split in enumerate(splits):
            # Reconstruct delimiter (except for last split)
            split_with_delimiter = split + (delimiter if i < len(splits) - 1 else "")

            # Check if adding this split exceeds max size
            potential_chunk = current_chunk + split_with_delimiter

            if len(potential_chunk) <= self.max_chunk_size:
                current_chunk = potential_chunk
            else:
                # Save current chunk if it meets minimum size
                if current_chunk and len(current_chunk) >= self.min_chunk_size:
                    chunks.append(current_chunk.strip())
                    # Start new chunk with overlap
                    current_chunk = self._get_overlap(current_chunk) + split_with_delimiter
                elif current_chunk:
                    # Current chunk too small, try finer delimiter
                    sub_chunks = self._recursive_split(
                        potential_chunk,
                        delimiter_index + 1,
                    )
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    # Split is larger than max size, recursively split it
                    sub_chunks = self._recursive_split(
                        split_with_delimiter,
                        delimiter_index + 1,
                    )
                    chunks.extend(sub_chunks)

        # Add remaining chunk
        if current_chunk and len(current_chunk.strip()) > 0:
            chunks.append(current_chunk.strip())

        return [c for c in chunks if c]  # Filter empty chunks

    def _force_split(self, text: str) -> List[str]:
        """
        Force split text at max_chunk_size when no delimiters work.

        Args:
            text: Text to split

        Returns:
            List of chunks split at character boundaries
        """
        chunks = []
        start = 0

        while start < len(text):
            end = min(start + self.max_chunk_size, len(text))
            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            start = end - self.chunk_overlap

        return chunks

    def _get_overlap(self, chunk: str) -> str:
        """
        Get overlap text from end of chunk.

        Args:
            chunk: Source chunk

        Returns:
            Last `chunk_overlap` characters from chunk
        """
        if len(chunk) <= self.chunk_overlap:
            return chunk

        return chunk[-self.chunk_overlap:]

    def extract_heading(self, text: str) -> Optional[str]:
        """
        Extract first heading from text.

        Args:
            text: Text content

        Returns:
            First markdown heading found, or None
        """
        # Match markdown headings (# Heading, ## Heading, etc.)
        heading_match = re.search(r"^(#{1,6})\s+(.+)$", text, re.MULTILINE)

        if heading_match:
            heading_text = heading_match.group(2).strip()
            logger.debug(f"Extracted heading: {heading_text}")
            return heading_text

        return None


# Global service instance
chunking_service = ChunkingService()
