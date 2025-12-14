"""
Docusaurus heading anchor generation utility.

This module provides functions for generating Docusaurus-style heading anchors
from markdown heading text.
"""

import re
from typing import List

from src.config.logging import get_logger

logger = get_logger(__name__)


def generate_anchor(heading_text: str) -> str:
    """
    Generate Docusaurus-style anchor from heading text.

    Docusaurus converts headings to lowercase, dash-separated anchors.

    Args:
        heading_text: Heading text (e.g., "Forward Kinematics")

    Returns:
        Anchor string (e.g., "forward-kinematics")

    Example:
        >>> generate_anchor("Forward Kinematics")
        'forward-kinematics'
        >>> generate_anchor("What is AI?")
        'what-is-ai'
        >>> generate_anchor("C++ Programming")
        'c-programming'
    """
    # Remove markdown formatting (**, *, `, etc.)
    text = re.sub(r"[*`_~]", "", heading_text)

    # Remove special characters except alphanumeric, spaces, and hyphens
    text = re.sub(r"[^a-zA-Z0-9\s-]", "", text)

    # Convert to lowercase
    text = text.lower()

    # Replace spaces with hyphens
    text = re.sub(r"\s+", "-", text)

    # Remove consecutive hyphens
    text = re.sub(r"-+", "-", text)

    # Trim hyphens from ends
    text = text.strip("-")

    logger.debug("anchor_generated", original=heading_text, anchor=text)

    return text


def extract_heading_from_markdown(line: str) -> tuple[int, str] | None:
    """
    Extract heading level and text from a markdown line.

    Args:
        line: Markdown line

    Returns:
        Tuple of (level, text) or None if not a heading

    Example:
        >>> extract_heading_from_markdown("## Introduction")
        (2, 'Introduction')
        >>> extract_heading_from_markdown("Regular text")
        None
    """
    # Match markdown headings (1-6 #)
    match = re.match(r"^(#{1,6})\s+(.+)$", line.strip())

    if match:
        level = len(match.group(1))
        text = match.group(2).strip()
        return (level, text)

    return None


def build_anchor_hierarchy(headings: List[dict]) -> dict[str, List[str]]:
    """
    Build a map of anchors to their heading hierarchy.

    This helps determine the context for each heading.

    Args:
        headings: List of heading dicts with level, text, anchor

    Returns:
        Dict mapping anchor to hierarchy list

    Example:
        >>> headings = [
        ...     {"level": 1, "text": "Chapter 1", "anchor": "chapter-1"},
        ...     {"level": 2, "text": "Introduction", "anchor": "introduction"},
        ... ]
        >>> build_anchor_hierarchy(headings)
        {
            "chapter-1": ["Chapter 1"],
            "introduction": ["Chapter 1", "Introduction"]
        }
    """
    hierarchy_map = {}
    current_hierarchy = [None] * 6  # Support up to H6

    for heading in headings:
        level = heading["level"]
        text = heading["text"]
        anchor = heading["anchor"]

        # Update hierarchy at this level
        current_hierarchy[level - 1] = text

        # Clear deeper levels
        for i in range(level, 6):
            current_hierarchy[i] = None

        # Build hierarchy list (filter None values)
        hierarchy = [h for h in current_hierarchy if h is not None]

        hierarchy_map[anchor] = hierarchy

        logger.debug(
            "hierarchy_built",
            anchor=anchor,
            level=level,
            hierarchy=hierarchy
        )

    return hierarchy_map


def parse_markdown_headings(content: str) -> List[dict]:
    """
    Parse all headings from markdown content.

    Args:
        content: Markdown content

    Returns:
        List of heading dictionaries with level, text, and anchor

    Example:
        >>> content = "# Title\\n## Section\\nText\\n### Subsection"
        >>> headings = parse_markdown_headings(content)
        >>> len(headings)
        3
    """
    headings = []

    for line in content.split("\n"):
        heading_data = extract_heading_from_markdown(line)

        if heading_data:
            level, text = heading_data
            anchor = generate_anchor(text)

            headings.append({
                "level": level,
                "text": text,
                "anchor": anchor,
            })

    logger.info("headings_parsed", count=len(headings))

    return headings


def build_citation_url(
    file_path: str,
    anchor: str,
    base_path: str = "/docs"
) -> str:
    """
    Build a citation URL for a Docusaurus page.

    Args:
        file_path: Relative file path (e.g., "chapter-01/intro.md")
        anchor: Heading anchor
        base_path: Base URL path (default: "/docs")

    Returns:
        Full citation URL

    Example:
        >>> build_citation_url("chapter-01/intro.md", "forward-kinematics")
        '/docs/chapter-01/intro#forward-kinematics'
    """
    # Remove .md extension and build URL
    page_path = file_path.replace(".md", "").replace("\\", "/")

    # Combine base path, page path, and anchor
    url = f"{base_path}/{page_path}#{anchor}"

    logger.debug("citation_url_built", file_path=file_path, anchor=anchor, url=url)

    return url


__all__ = [
    "generate_anchor",
    "extract_heading_from_markdown",
    "build_anchor_hierarchy",
    "parse_markdown_headings",
    "build_citation_url",
]
