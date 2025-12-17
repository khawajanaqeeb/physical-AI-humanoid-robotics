"""
Initial textbook ingestion script.

This script runs the complete ingestion workflow to populate Qdrant with textbook content.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the path so we can import modules
sys.path.insert(0, str(Path(__file__).parent))

from src.core.config import settings
from src.services.ingestion_service import ingestion_service


def run_ingestion():
    """
    Run the complete textbook ingestion workflow.
    """
    print("Starting textbook ingestion...")
    print(f"Using sitemap URL: {settings.textbook_sitemap_url}")
    print(f"Target collection: {settings.qdrant_collection_name}")

    try:
        # Run the ingestion
        job = ingestion_service.ingest_textbook()

        print(f"\nIngestion completed! Job ID: {job.job_id}")
        print(f"Status: {job.status}")
        print(f"Pages processed: {job.pages_processed}")
        print(f"Chunks created: {job.chunks_created}")
        print(f"Errors encountered: {len(job.errors_encountered)}")

        if job.errors_encountered:
            print("\nErrors:")
            for error in job.errors_encountered:
                print(f"  - {error.page_url}: {error.error_message}")

        return job

    except Exception as e:
        print(f"Error during ingestion: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    print("RAG Chatbot - Textbook Ingestion Script")
    print("=" * 50)

    # Check if environment variables are set
    if not settings.cohere_api_key or settings.cohere_api_key == "your-cohere-api-key-here":
        print("ERROR: COHERE_API_KEY not set in environment!")
        print("Please set your Cohere API key in the .env file.")
        sys.exit(1)

    if not settings.qdrant_url or settings.qdrant_url == "https://your-cluster.qdrant.io":
        print("ERROR: QDRANT_URL not set in environment!")
        print("Please set your Qdrant Cloud URL in the .env file.")
        sys.exit(1)

    if not settings.qdrant_api_key or settings.qdrant_api_key == "your-qdrant-api-key-here":
        print("ERROR: QDRANT_API_KEY not set in environment!")
        print("Please set your Qdrant API key in the .env file.")
        sys.exit(1)

    print("Environment variables validated successfully!")

    # Run ingestion
    job = run_ingestion()

    if job and job.status == "completed":
        print(f"\n✅ Textbook ingestion completed successfully!")
        print(f"   Processed {job.pages_processed} pages")
        print(f"   Created {job.chunks_created} chunks")
    else:
        print(f"\n❌ Textbook ingestion failed!")
        sys.exit(1)