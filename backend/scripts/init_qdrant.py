#!/usr/bin/env python3
"""
Qdrant collection initialization script.

This script creates the Qdrant collection for storing text embeddings
with the proper configuration.

Usage:
    python scripts/init_qdrant.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clients.qdrant_client import create_collection, get_qdrant_client
from config.settings import get_settings
from config.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


async def main():
    """Main execution function."""
    logger.info("qdrant_initialization_started")

    try:
        settings = get_settings()

        # Create collection
        logger.info(
            "creating_collection",
            collection=settings.qdrant_collection_name,
            vector_size=3072,
            distance="COSINE",
        )

        await create_collection(
            collection_name=settings.qdrant_collection_name,
            vector_size=3072,  # text-embedding-3-large dimensions
        )

        # Verify collection exists
        client = get_qdrant_client()
        collections = await client.get_collections()

        collection_exists = any(
            c.name == settings.qdrant_collection_name
            for c in collections.collections
        )

        if collection_exists:
            logger.info("collection_verified", collection=settings.qdrant_collection_name)
            print(f"\n✅ Qdrant collection '{settings.qdrant_collection_name}' created successfully!")
            print("\nConfiguration:")
            print(f"  - Vector dimensions: 3072 (text-embedding-3-large)")
            print(f"  - Distance metric: COSINE")
            print(f"  - Payload indexes: file_path, section_anchor")
        else:
            raise RuntimeError("Collection was not created")

        logger.info("qdrant_initialization_completed")

    except Exception as e:
        logger.error("qdrant_initialization_failed", error=str(e))
        print(f"\n❌ Qdrant initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
