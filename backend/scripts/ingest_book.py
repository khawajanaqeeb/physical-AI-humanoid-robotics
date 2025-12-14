#!/usr/bin/env python3
"""
Book Ingestion Script for Gemini RAG

Ingests Docusaurus markdown content into the RAG system.
Parses markdown files, chunks content, generates Gemini embeddings,
and stores in Qdrant + Postgres.

Usage:
    python scripts/ingest_book.py --docs-path /path/to/docs
    python scripts/ingest_book.py --docs-path /path/to/docs --force  # Re-index all
    python scripts/ingest_book.py --file docs/chapter-01/intro.md   # Single file
"""

import asyncio
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any
import re
from uuid import uuid4

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import asyncpg
from qdrant_client.models import PointStruct

from services.embedding import get_embedding_service
from services.chunking import get_chunking_service
from clients.qdrant_client import get_qdrant_client
from config.settings import get_settings
from config.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


def parse_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
    """
    Parse YAML frontmatter from markdown content.

    Args:
        content: Markdown content with optional frontmatter

    Returns:
        Tuple of (frontmatter_dict, content_without_frontmatter)
    """
    frontmatter = {}
    body = content

    # Check for frontmatter (between --- markers)
    frontmatter_pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
    match = frontmatter_pattern.match(content)

    if match:
        frontmatter_text = match.group(1)
        body = content[match.end():]

        # Parse YAML-like frontmatter (simple key: value pairs)
        for line in frontmatter_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip().strip('"\'')

    return frontmatter, body


def extract_source_url(file_path: Path, docs_root: Path, base_url: str) -> str:
    """
    Generate the public URL for a Docusaurus page.

    Args:
        file_path: Path to the markdown file
        docs_root: Root docs directory
        base_url: Base URL for the deployed site

    Returns:
        Public URL to the page
    """
    # Get relative path from docs root
    relative_path = file_path.relative_to(docs_root)

    # Convert to URL path
    url_path = str(relative_path).replace('\\', '/')

    # Remove file extension
    url_path = url_path.replace('.md', '').replace('.mdx', '')

    # Build full URL
    return f"{base_url}/{url_path}"


async def ingest_file(
    file_path: Path,
    docs_root: Path,
    base_url: str,
    db_conn: asyncpg.Connection,
    force: bool = False
) -> int:
    """
    Ingest a single markdown file.

    Args:
        file_path: Path to the markdown file
        docs_root: Root docs directory
        base_url: Base URL for the site
        db_conn: Database connection
        force: Force re-indexing even if file hasn't changed

    Returns:
        Number of chunks created
    """
    logger.info("ingesting_file", file_path=str(file_path))

    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.strip():
            logger.warning("empty_file_skipped", file_path=str(file_path))
            return 0

        # Parse frontmatter
        frontmatter, body = parse_frontmatter(content)

        # Generate source URL
        source_url = extract_source_url(file_path, docs_root, base_url)

        # Get relative file path for storage
        relative_path = file_path.relative_to(docs_root.parent)
        file_path_str = str(relative_path).replace('\\', '/')

        # Check if file was already indexed (unless force=True)
        if not force:
            existing = await db_conn.fetchval(
                "SELECT COUNT(*) FROM chunks WHERE file_path = $1",
                file_path_str
            )
            if existing > 0:
                logger.info("file_already_indexed", file_path=file_path_str, chunks=existing)
                return 0

        # Delete existing chunks for this file if force=True
        if force:
            deleted = await db_conn.execute(
                "DELETE FROM chunks WHERE file_path = $1",
                file_path_str
            )
            logger.info("existing_chunks_deleted", file_path=file_path_str)

        # Chunk the content
        chunking_service = get_chunking_service()
        chunks = chunking_service.chunk_content(
            content=body,
            file_path=file_path_str,
            frontmatter=frontmatter
        )

        if not chunks:
            logger.warning("no_chunks_created", file_path=file_path_str)
            return 0

        logger.info("chunks_created", file_path=file_path_str, count=len(chunks))

        # Generate embeddings for all chunks
        embedding_service = get_embedding_service()
        chunk_texts = [chunk.text for chunk in chunks]

        embeddings = await embedding_service.embed_batch(
            texts=chunk_texts,
            task_type="retrieval_document",
            batch_size=10,
            delay_between_batches=1.0
        )

        logger.info("embeddings_generated", count=len(embeddings))

        # Prepare data for Qdrant and Postgres
        qdrant_client = get_qdrant_client()
        settings = get_settings()
        points = []

        for chunk, embedding in zip(chunks, embeddings):
            point_id = str(uuid4())

            # Prepare Qdrant point
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "chunk_id": point_id,
                    "chunk_text": chunk.text,
                    "file_path": chunk.file_path,
                    "chapter": chunk.chapter,
                    "section": chunk.section,
                    "heading_path": chunk.heading_path,
                    "source_url": source_url,
                    "chunk_index": chunk.chunk_index,
                    "total_chunks": chunk.total_chunks
                }
            )
            points.append(point)

            # Insert into Postgres
            await db_conn.execute(
                """
                INSERT INTO chunks (
                    chunk_text, file_path, chapter, section, heading_path,
                    source_url, chunk_index, total_chunks, qdrant_point_id
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                chunk.text,
                chunk.file_path,
                chunk.chapter,
                chunk.section,
                chunk.heading_path,
                source_url,
                chunk.chunk_index,
                chunk.total_chunks,
                point_id
            )

        # Upsert to Qdrant
        await qdrant_client.upsert(
            collection_name=settings.qdrant_collection_name,
            points=points
        )

        logger.info(
            "file_ingested_successfully",
            file_path=file_path_str,
            chunks=len(chunks)
        )

        return len(chunks)

    except Exception as e:
        logger.error(
            "file_ingestion_failed",
            file_path=str(file_path),
            error=str(e)
        )
        raise


async def ingest_directory(
    docs_path: Path,
    base_url: str,
    force: bool = False
) -> Dict[str, int]:
    """
    Ingest all markdown files in a directory.

    Args:
        docs_path: Path to docs directory
        base_url: Base URL for the site
        force: Force re-indexing

    Returns:
        Dict with ingestion statistics
    """
    logger.info("ingestion_started", docs_path=str(docs_path), force=force)

    # Find all markdown files
    md_files = list(docs_path.glob('**/*.md')) + list(docs_path.glob('**/*.mdx'))

    if not md_files:
        logger.warning("no_markdown_files_found", docs_path=str(docs_path))
        return {"files_processed": 0, "total_chunks": 0, "errors": 0}

    logger.info("markdown_files_found", count=len(md_files))

    # Connect to database
    settings = get_settings()
    db_url = settings.database_url.replace("postgresql+asyncpg://", "")
    db_conn = await asyncpg.connect(f"postgresql://{db_url}")

    stats = {
        "files_processed": 0,
        "files_skipped": 0,
        "total_chunks": 0,
        "errors": 0,
        "error_files": []
    }

    # Process each file
    for md_file in md_files:
        try:
            chunks_created = await ingest_file(
                file_path=md_file,
                docs_root=docs_path,
                base_url=base_url,
                db_conn=db_conn,
                force=force
            )

            if chunks_created > 0:
                stats["files_processed"] += 1
                stats["total_chunks"] += chunks_created
            else:
                stats["files_skipped"] += 1

        except Exception as e:
            stats["errors"] += 1
            stats["error_files"].append(str(md_file))
            logger.error(
                "file_processing_error",
                file=str(md_file),
                error=str(e)
            )
            # Continue with next file

    await db_conn.close()

    logger.info("ingestion_completed", **stats)

    return stats


async def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Ingest Docusaurus markdown content into Gemini RAG system"
    )
    parser.add_argument(
        "--docs-path",
        type=str,
        required=True,
        help="Path to Docusaurus docs directory"
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default="https://book.example.com",
        help="Base URL for deployed book (default: https://book.example.com)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-indexing of all files (delete and re-create chunks)"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Ingest a single file instead of entire directory"
    )

    args = parser.parse_args()

    print("\n🚀 Starting book ingestion for Gemini RAG...")
    print("=" * 60)

    docs_path = Path(args.docs_path)
    if not docs_path.exists():
        print(f"\n❌ Error: Path does not exist: {docs_path}")
        sys.exit(1)

    try:
        if args.file:
            # Ingest single file
            file_path = Path(args.file)
            if not file_path.exists():
                print(f"\n❌ Error: File does not exist: {file_path}")
                sys.exit(1)

            settings = get_settings()
            db_url = settings.database_url.replace("postgresql+asyncpg://", "")
            db_conn = await asyncpg.connect(f"postgresql://{db_url}")

            chunks = await ingest_file(
                file_path=file_path,
                docs_root=docs_path,
                base_url=args.base_url,
                db_conn=db_conn,
                force=args.force
            )

            await db_conn.close()

            print(f"\n✅ File ingested successfully!")
            print(f"   Chunks created: {chunks}")

        else:
            # Ingest entire directory
            stats = await ingest_directory(
                docs_path=docs_path,
                base_url=args.base_url,
                force=args.force
            )

            print("\n✅ Ingestion completed!")
            print("\nStatistics:")
            print(f"  Files processed: {stats['files_processed']}")
            print(f"  Files skipped: {stats['files_skipped']}")
            print(f"  Total chunks: {stats['total_chunks']}")
            print(f"  Errors: {stats['errors']}")

            if stats['error_files']:
                print("\n❌ Files with errors:")
                for error_file in stats['error_files']:
                    print(f"  - {error_file}")

        print("\n" + "=" * 60)

    except Exception as e:
        logger.error("ingestion_failed", error=str(e))
        print(f"\n❌ Ingestion failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
