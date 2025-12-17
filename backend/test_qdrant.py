#!/usr/bin/env python3
"""
Test script to verify Qdrant collection and search functionality
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.config import settings
from src.services.qdrant_service import qdrant_service
from src.services.cohere_service import cohere_service

def test_collection_info():
    """Test the collection information"""
    print("[INFO] Testing Qdrant collection information...")
    print(f"Using collection: {settings.qdrant_collection_name}")
    print(f"Qdrant URL: {settings.qdrant_url}")

    try:
        # Get collection info
        collections = qdrant_service.client.get_collections().collections
        print(f"Available collections: {[c.name for c in collections]}")

        # Check if our collection exists
        collection_names = [c.name for c in collections]
        if settings.qdrant_collection_name in collection_names:
            print(f"[SUCCESS] Collection '{settings.qdrant_collection_name}' exists!")

            # Get collection info
            collection_info = qdrant_service.client.get_collection(settings.qdrant_collection_name)
            print(f"Collection points count: {collection_info.points_count}")
            print(f"Collection vectors count: {collection_info.vectors_count}")
        else:
            print(f"[ERROR] Collection '{settings.qdrant_collection_name}' does not exist!")

    except Exception as e:
        print(f"[ERROR] Error getting collection info: {e}")

def test_search():
    """Test search functionality"""
    print("\n[INFO] Testing search functionality...")

    try:
        # Create a test query embedding
        test_query = "humanoid robotics"
        print(f"Query: '{test_query}'")

        query_embedding = cohere_service.embed([test_query], input_type="search_query")
        query_vector = query_embedding[0]  # Get the first (and only) embedding

        print(f"Query vector length: {len(query_vector)}")

        # Perform search
        results = qdrant_service.search(
            query_vector=query_vector,
            limit=5,
            score_threshold=0.0  # Lower threshold to get results
        )

        print(f"Search returned {len(results)} results")

        for i, result in enumerate(results):
            print(f"Result {i+1}:")
            print(f"  ID: {result['id']}")
            print(f"  Score: {result['score']}")
            print(f"  Payload keys: {list(result['payload'].keys())}")
            if 'text' in result['payload']:
                print(f"  Text preview: {result['payload']['text'][:100]}...")
            print()

    except Exception as e:
        print(f"[ERROR] Error during search test: {e}")
        import traceback
        traceback.print_exc()

def test_direct_client():
    """Test using Qdrant client directly"""
    print("\n[INFO] Testing direct Qdrant client query...")

    try:
        # Get all points in the collection to verify data exists
        points = list(qdrant_service.client.scroll(
            collection_name=settings.qdrant_collection_name,
            limit=5
        ))

        print(f"Scroll returned {len(points[0])} points out of total collection")

        if points[0]:
            first_point = points[0][0]
            print(f"First point ID: {first_point.id}")
            print(f"First point payload keys: {list(first_point.payload.keys())}")
            if 'text' in first_point.payload:
                print(f"First point text preview: {first_point.payload['text'][:100]}...")

    except Exception as e:
        print(f"[ERROR] Error during direct client test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Qdrant Test Script")
    print("=" * 50)

    test_collection_info()
    test_search()
    test_direct_client()

    print("\n✅ Test completed!")