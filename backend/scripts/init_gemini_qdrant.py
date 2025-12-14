#!/usr/bin/env python3
"""
Qdrant collection initialization script for Gemini embeddings.

This script creates the Qdrant collection for storing Gemini embedding-001
vectors (768 dimensions) with the proper configuration.

Usage:
    python scripts/init_gemini_qdrant.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clients.qdrant_client import get_qdrant_client
from qdrant_client.models import Distance, VectorParams
from config.settings import get_settings
from config.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


async def create_gemini_collection():
    """Create Qdrant collection for Gemini embeddings."""
    settings = get_settings()
    client = get_qdrant_client()

    collection_name = settings.qdrant_collection_name
    vector_size = 768  # Gemini embedding-001 dimensions

    try:
        # Check if collection already exists
        collections = await client.get_collections()
        if collection_name in [c.name for c in collections.collections]:
            logger.info("collection_already_exists", collection=collection_name)
            print(f"\n⚠️  Collection '{collection_name}' already exists")

            # Check if it has correct dimensions
            collection_info = await client.get_collection(collection_name)
            actual_size = collection_info.config.params.vectors.size

            if actual_size != vector_size:
                print(f"\n❌ ERROR: Existing collection has {actual_size} dimensions, expected {vector_size}")
                print(f"   Please delete the collection and run this script again:")
                print(f"   - Delete via Qdrant UI or use qdrant_client.delete_collection('{collection_name}')")
                sys.exit(1)
            else:
                print(f"   ✅ Collection has correct dimensions ({vector_size})")
                return

        # Create collection
        logger.info(
            "creating_collection",
            collection=collection_name,
            vector_size=vector_size,
            distance="COSINE",
        )

        await client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )

        # Create payload indexes for faster filtering
        await client.create_payload_index(
            collection_name=collection_name,
            field_name="file_path",
            field_schema="keyword",
        )

        await client.create_payload_index(
            collection_name=collection_name,
            field_name="chapter",
            field_schema="keyword",
        )

        logger.info("collection_created", collection=collection_name)

    except Exception as e:
        logger.error("collection_creation_failed", error=str(e))
        raise


async def verify_collection():
    """Verify that the collection was created correctly."""
    settings = get_settings()
    client = get_qdrant_client()
    collection_name = settings.qdrant_collection_name

    try:
        collection_info = await client.get_collection(collection_name)

        vector_size = collection_info.config.params.vectors.size
        distance = collection_info.config.params.vectors.distance
        points_count = collection_info.points_count

        logger.info(
            "collection_verified",
            collection=collection_name,
            vector_size=vector_size,
            distance=distance,
            points=points_count
        )

        return {
            "name": collection_name,
            "vector_size": vector_size,
            "distance": distance,
            "points": points_count
        }

    except Exception as e:
        logger.error("collection_verification_failed", error=str(e))
        raise


async def main():
    """Main execution function."""
    logger.info("qdrant_gemini_initialization_started")

    try:
        print("\n🚀 Initializing Qdrant for Gemini embeddings...")
        print("=" * 60)

        # Create collection
        await create_gemini_collection()

        # Verify collection
        info = await verify_collection()

        logger.info("qdrant_initialization_completed")

        print("\n✅ Qdrant collection initialized successfully!")
        print("\nConfiguration:")
        print(f"  Collection name: {info['name']}")
        print(f"  Vector dimensions: {info['vector_size']} (Gemini embedding-001)")
        print(f"  Distance metric: {info['distance']}")
        print(f"  Current points: {info['points']}")
        print(f"  Payload indexes: file_path, chapter")
        print("\n" + "=" * 60)

    except Exception as e:
        logger.error("qdrant_initialization_failed", error=str(e))
        print(f"\n❌ Qdrant initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
