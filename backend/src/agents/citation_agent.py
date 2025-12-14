"""
Citation Agent for RAG pipeline.

This agent matches answer claims to source chunks and formats
citations with Docusaurus anchor links.
"""

import time
from typing import List

from src.models import Citation
from src.utils.docusaurus_anchors import build_citation_url
from src.config.logging import get_logger

logger = get_logger(__name__)


class CitationAgent:
    """
    Agent responsible for generating citations for answers.

    This agent:
    1. Matches answer content to source chunks
    2. Extracts document titles and section anchors
    3. Formats citations as Docusaurus links
    """

    def __init__(self):
        """Initialize the Citation Agent."""
        logger.info("citation_agent_initialized")

    async def generate_citations(
        self,
        answer: str,
        source_chunks: List[dict],
    ) -> tuple[List[Citation], int]:
        """
        Generate citations for an answer based on source chunks.

        Args:
            answer: Generated answer text
            source_chunks: List of chunks used to generate the answer

        Returns:
            Tuple of (citations, citation_time_ms)
            - citations: List of Citation objects with title, anchor, url
            - citation_time_ms: Time taken in milliseconds

        Example:
            >>> agent = CitationAgent()
            >>> citations, time_ms = await agent.generate_citations(
            ...     answer="Forward kinematics is...",
            ...     source_chunks=[{...}, {...}]
            ... )
        """
        start_time = time.time()

        logger.info(
            "citation_generation_started",
            answer_length=len(answer),
            source_chunks_count=len(source_chunks),
        )

        try:
            citations = []
            seen_anchors = set()  # Avoid duplicate citations

            # For each source chunk, create a citation
            for chunk in source_chunks:
                # Extract metadata
                document_title = chunk.get("document_title", "Unknown Document")
                section_anchor = chunk.get("section_anchor", "")
                file_path = chunk.get("file_path", "")

                # Skip if we've already cited this section
                if section_anchor in seen_anchors:
                    continue

                seen_anchors.add(section_anchor)

                # Build citation URL
                url = build_citation_url(
                    file_path=file_path,
                    anchor=section_anchor,
                    base_path="/docs"
                )

                # Create Citation object
                citation = Citation(
                    title=document_title,
                    anchor=section_anchor,
                    url=url
                )

                citations.append(citation)

                logger.debug(
                    "citation_created",
                    title=document_title,
                    anchor=section_anchor,
                    url=url,
                )

            citation_time_ms = int((time.time() - start_time) * 1000)

            logger.info(
                "citations_generated",
                citations_count=len(citations),
                citation_time_ms=citation_time_ms,
            )

            return citations, citation_time_ms

        except Exception as e:
            citation_time_ms = int((time.time() - start_time) * 1000)
            logger.error(
                "citation_generation_failed",
                error=str(e),
                citation_time_ms=citation_time_ms,
            )
            raise

    def extract_unique_sources(self, citations: List[Citation]) -> List[str]:
        """
        Extract unique document titles from citations.

        Args:
            citations: List of Citation objects

        Returns:
            List of unique document titles

        Example:
            >>> sources = agent.extract_unique_sources(citations)
            >>> print(sources)  # ["Robotics Fundamentals", "Kinematics Guide"]
        """
        seen_titles = set()
        unique_sources = []

        for citation in citations:
            if citation.title not in seen_titles:
                seen_titles.add(citation.title)
                unique_sources.append(citation.title)

        logger.debug("unique_sources_extracted", count=len(unique_sources))

        return unique_sources

    def format_citations_for_display(self, citations: List[Citation]) -> str:
        """
        Format citations as a readable string (for debugging/logging).

        Args:
            citations: List of Citation objects

        Returns:
            Formatted citation string

        Example:
            >>> formatted = agent.format_citations_for_display(citations)
            >>> print(formatted)
            [1] Robotics Fundamentals (forward-kinematics)
            [2] Kinematics Guide (inverse-kinematics)
        """
        if not citations:
            return "No citations"

        lines = []
        for i, citation in enumerate(citations, 1):
            line = f"[{i}] {citation.title} ({citation.anchor})"
            lines.append(line)

        return "\n".join(lines)


# Singleton instance
_citation_agent = None


def get_citation_agent() -> CitationAgent:
    """
    Get or create the Citation Agent instance.

    Returns:
        CitationAgent singleton instance
    """
    global _citation_agent

    if _citation_agent is None:
        _citation_agent = CitationAgent()

    return _citation_agent
