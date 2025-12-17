"""
Script to delete and recreate the Qdrant collection with correct dimensions.
"""

import sys
from pathlib import Path

# Add the backend directory to the path so we can import modules
sys.path.insert(0, str(Path(__file__).parent))

from src.core.config import settings
from src.services.qdrant_service import qdrant_service
from src.core.logging_config import get_logger

logger = get_logger(__name__)

def reset_collection():
    """Delete and recreate the Qdrant collection with correct dimensions."""
    print(f"Resetting collection: {settings.qdrant_collection_name}")

    try:
        # Delete the existing collection
        print(f"Deleting collection '{settings.qdrant_collection_name}'...")
        qdrant_service.client.delete_collection(settings.qdrant_collection_name)
        print("Collection deleted successfully.")

    except Exception as e:
        print(f"Collection might not exist yet or error occurred during deletion: {e}")
        print("Continuing to create collection...")

    # Recreate the collection with correct dimensions
    print(f"Creating collection '{settings.qdrant_collection_name}' with 1024 dimensions...")
    qdrant_service.create_collection()
    print("Collection created successfully with correct dimensions!")

    # Verify the collection
    collection_info = qdrant_service.client.get_collection(settings.qdrant_collection_name)
    print(f"Collection info: {collection_info.config.params}")
    print(f"Vector dimension: {collection_info.config.params.vectors.size}")

    print("\n✅ Collection reset completed successfully!")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    reset_collection()