"""
MCP (Model Context Protocol) client wrapper for file system operations.

This module provides async operations for reading markdown files and
extracting content using the MCP server.

Note: This is a simplified implementation. Full MCP integration requires
the MCP server to be running and properly configured.
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config.settings import get_settings
from src.config.logging import get_logger

logger = get_logger(__name__)


class MCPClient:
    """
    MCP client for file system operations and content extraction.

    This is a simplified implementation that directly reads files.
    In production, this should use the actual MCP protocol.
    """

    def __init__(self, docs_path: str | None = None):
        """
        Initialize MCP client.

        Args:
            docs_path: Path to documentation directory
        """
        settings = get_settings()
        self.docs_path = Path(docs_path or settings.docs_path)
        logger.info("mcp_client_initialized", docs_path=str(self.docs_path))

    async def list_markdown_files(self) -> list[str]:
        """
        List all markdown files in the documentation directory.

        Returns:
            List of file paths relative to docs_path

        Example:
            >>> client = MCPClient()
            >>> files = await client.list_markdown_files()
            >>> print(files)  # ['chapter-01/intro.md', ...]
        """
        markdown_files = []

        for file_path in self.docs_path.rglob("*.md"):
            if file_path.is_file():
                relative_path = file_path.relative_to(self.docs_path)
                markdown_files.append(str(relative_path).replace("\\", "/"))

        logger.info("markdown_files_listed", count=len(markdown_files))
        return sorted(markdown_files)

    async def read_file(self, file_path: str) -> str:
        """
        Read a markdown file's content.

        Args:
            file_path: Relative file path from docs_path

        Returns:
            File content as string

        Example:
            >>> client = MCPClient()
            >>> content = await client.read_file("chapter-01/intro.md")
        """
        full_path = self.docs_path / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        logger.debug("file_read", file_path=file_path, size=len(content))
        return content

    async def extract_heading_hierarchy(self, content: str) -> list[dict[str, Any]]:
        """
        Extract heading hierarchy from markdown content.

        Args:
            content: Markdown content

        Returns:
            List of heading dictionaries with level, text, and anchor

        Example:
            >>> headings = await client.extract_heading_hierarchy("# Title\\n## Section")
            >>> print(headings)
            [{'level': 1, 'text': 'Title', 'anchor': 'title'}, ...]
        """
        headings = []
        heading_pattern = r"^(#{1,6})\s+(.+)$"

        for line in content.split("\n"):
            match = re.match(heading_pattern, line)
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()
                anchor = self._generate_anchor(text)

                headings.append({
                    "level": level,
                    "text": text,
                    "anchor": anchor,
                })

        logger.debug("headings_extracted", count=len(headings))
        return headings

    async def get_file_metadata(self, file_path: str) -> dict[str, Any]:
        """
        Get metadata for a markdown file.

        Args:
            file_path: Relative file path from docs_path

        Returns:
            Metadata dictionary with modified time, size, etc.

        Example:
            >>> metadata = await client.get_file_metadata("chapter-01/intro.md")
            >>> print(metadata['modified_at'])
        """
        full_path = self.docs_path / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        stat = full_path.stat()

        return {
            "file_path": file_path,
            "size_bytes": stat.st_size,
            "modified_at": datetime.fromtimestamp(stat.st_mtime),
            "created_at": datetime.fromtimestamp(stat.st_ctime),
        }

    async def detect_file_changes(
        self,
        last_sync_time: datetime | None = None,
    ) -> list[str]:
        """
        Detect files that have changed since last sync.

        Args:
            last_sync_time: Timestamp of last sync (None = all files)

        Returns:
            List of changed file paths

        Example:
            >>> changed = await client.detect_file_changes(last_sync_time)
        """
        all_files = await self.list_markdown_files()
        changed_files = []

        for file_path in all_files:
            metadata = await self.get_file_metadata(file_path)

            if last_sync_time is None or metadata["modified_at"] > last_sync_time:
                changed_files.append(file_path)

        logger.info("file_changes_detected", count=len(changed_files))
        return changed_files

    def _generate_anchor(self, heading_text: str) -> str:
        """
        Generate Docusaurus-style anchor from heading text.

        Args:
            heading_text: Heading text

        Returns:
            Anchor string (lowercase, dash-separated)

        Example:
            >>> anchor = client._generate_anchor("Forward Kinematics")
            >>> print(anchor)  # "forward-kinematics"
        """
        # Remove special characters and convert to lowercase
        anchor = re.sub(r"[^a-zA-Z0-9\s-]", "", heading_text)
        anchor = anchor.lower()

        # Replace spaces with dashes
        anchor = re.sub(r"\s+", "-", anchor)

        # Remove consecutive dashes
        anchor = re.sub(r"-+", "-", anchor)

        # Trim dashes from ends
        anchor = anchor.strip("-")

        return anchor


# Global client instance
_mcp_client: MCPClient | None = None


def get_mcp_client() -> MCPClient:
    """
    Get or create the MCP client instance.

    Returns:
        MCPClient instance

    Example:
        >>> client = get_mcp_client()
        >>> files = await client.list_markdown_files()
    """
    global _mcp_client

    if _mcp_client is None:
        _mcp_client = MCPClient()

    return _mcp_client


async def check_mcp_connection() -> bool:
    """
    Check if MCP client can access documentation directory.

    Returns:
        True if directory is accessible, False otherwise

    Example:
        >>> is_healthy = await check_mcp_connection()
        >>> print(f"MCP: {'ok' if is_healthy else 'error'}")
    """
    try:
        client = get_mcp_client()
        await client.list_markdown_files()
        return True
    except Exception:
        return False
