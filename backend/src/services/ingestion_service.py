"""
Ingestion service for crawling and indexing textbook content.

Orchestrates sitemap parsing, page crawling, chunking, embedding, and vector storage.
"""

import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from src.core.config import settings
from src.core.exceptions import IngestionError
from src.core.logging_config import get_logger
from src.models.chunk import DocumentChunk
from src.models.ingestion_job import IngestionJob, JobStatus
from src.services.chunking_service import chunking_service
from src.services.cohere_service import cohere_service
from src.services.qdrant_service import qdrant_service
from src.utils.text_processing import clean_text, extract_heading_context

logger = get_logger(__name__)


class IngestionService:
    """
    Service for ingesting textbook content into the vector database.

    Workflow:
    1. Fetch sitemap URLs
    2. Crawl each page
    3. Extract and clean content
    4. Chunk text semantically
    5. Generate embeddings with Cohere
    6. Upsert to Qdrant
    """

    # HTTP configuration
    REQUEST_TIMEOUT = 30  # seconds
    USER_AGENT = "RAG-Chatbot-Ingestion/1.0"

    def __init__(self):
        """Initialize ingestion service."""
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT})

        logger.info("IngestionService initialized")

    def fetch_sitemap(self, sitemap_url: Optional[str] = None) -> List[str]:
        """
        Fetch and parse sitemap.xml to get list of page URLs.

        Args:
            sitemap_url: Sitemap URL (defaults to settings.textbook_sitemap_url)

        Returns:
            List of page URLs from sitemap

        Raises:
            IngestionError: If sitemap fetch or parse fails
        """
        url = sitemap_url or settings.textbook_sitemap_url

        try:
            logger.info(f"Fetching sitemap from {url}")

            response = self.session.get(url, timeout=self.REQUEST_TIMEOUT)
            response.raise_for_status()

            # Parse XML sitemap
            root = ET.fromstring(response.content)

            # Extract URLs (handle namespace)
            namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            urls = [
                loc.text
                for loc in root.findall(".//ns:loc", namespace)
                if loc.text
            ]

            # Fallback: try without namespace
            if not urls:
                urls = [loc.text for loc in root.findall(".//loc") if loc.text]

            # Fix URLs: replace placeholder domain with actual deployed domain
            # The sitemap may contain placeholder URLs that need to be corrected
            fixed_urls = []
            for original_url in urls:
                fixed_url = original_url.replace(
                    "your-textbook-site.example.com",  # Placeholder domain in sitemap
                    "physical-ai-humanoid-robotics-e3c7.vercel.app"  # Actual deployed domain
                )
                fixed_urls.append(fixed_url)

            logger.info(
                f"Fetched {len(urls)} URLs from sitemap (fixed {len([u for u in urls if 'your-textbook-site.example.com' in u])} placeholder URLs)",
                extra={"url_count": len(urls)},
            )

            return fixed_urls

        except requests.RequestException as e:
            logger.error(f"Failed to fetch sitemap: {e}", exc_info=True)
            raise IngestionError(
                message=f"Failed to fetch sitemap from {url}",
                details={"error": str(e), "url": url},
            )
        except ET.ParseError as e:
            logger.error(f"Failed to parse sitemap XML: {e}", exc_info=True)
            raise IngestionError(
                message="Failed to parse sitemap XML",
                details={"error": str(e), "url": url},
            )

    def crawl_page(self, page_url: str) -> Optional[Dict[str, Any]]:
        """
        Crawl a single page and extract content.

        Args:
            page_url: URL of page to crawl

        Returns:
            dict with 'url', 'title', 'content', 'heading' or None if failed

        Raises:
            IngestionError: If page fetch or parse fails
        """
        try:
            logger.debug(f"Crawling page: {page_url}")

            response = self.session.get(page_url, timeout=self.REQUEST_TIMEOUT)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "lxml")

            # Extract title
            title_tag = soup.find("title")
            title = title_tag.get_text(strip=True) if title_tag else "Untitled"

            # Extract main content (try multiple selectors for Docusaurus)
            content_element = (
                soup.find("article")
                or soup.find("main")
                or soup.find("div", class_="markdown")
                or soup.find("div", {"role": "main"})
            )

            if not content_element:
                raise IngestionError(
                    message="No main content found in page",
                    details={
                        "url": page_url,
                        "reason": "No <article>, <main>, or .markdown element found",
                    },
                )

            # Extract text content
            content_text = content_element.get_text(separator="\n", strip=True)

            # Clean content
            cleaned_content = clean_text(
                content_text,
                remove_nav=True,
                remove_footer=True,
                remove_code=False,  # Keep code for technical content
            )

            # Extract heading context
            heading = extract_heading_context(cleaned_content)

            logger.debug(
                f"Crawled page: {page_url}",
                extra={
                    "title": title,
                    "content_length": len(cleaned_content),
                    "heading": heading,
                },
            )

            return {
                "url": page_url,
                "title": title,
                "content": cleaned_content,
                "heading": heading,
            }

        except requests.RequestException as e:
            logger.error(f"HTTP error crawling {page_url}: {e}", exc_info=True)
            raise IngestionError(
                message=f"Failed to fetch page: {page_url}",
                details={"error": str(e), "url": page_url, "error_type": "HTTPError"},
            )
        except Exception as e:
            logger.error(f"Parse error crawling {page_url}: {e}", exc_info=True)
            raise IngestionError(
                message=f"Failed to parse page: {page_url}",
                details={"error": str(e), "url": page_url, "error_type": "ParseError"},
            )

    def ingest_textbook(self, sitemap_url: Optional[str] = None) -> IngestionJob:
        """
        Orchestrate complete textbook ingestion workflow.

        Steps:
        1. Fetch sitemap URLs
        2. Crawl each page
        3. Chunk content
        4. Generate embeddings with Cohere
        5. Upsert to Qdrant

        Args:
            sitemap_url: Optional sitemap URL (defaults to config)

        Returns:
            IngestionJob with results and metrics

        Raises:
            IngestionError: If critical ingestion step fails
        """
        job = IngestionJob(status=JobStatus.RUNNING)

        try:
            logger.info(
                f"Starting ingestion job {job.job_id}",
                extra={"job_id": str(job.job_id)},
            )

            # Step 1: Fetch sitemap
            try:
                page_urls = self.fetch_sitemap(sitemap_url)
            except IngestionError as e:
                job.mark_failed(f"Sitemap fetch failed: {e.message}")
                return job

            # Step 2: Process each page
            for page_url in page_urls:
                try:
                    # Crawl page
                    page_data = self.crawl_page(page_url)

                    if not page_data or not page_data.get("content"):
                        job.add_error(
                            page_url=page_url,
                            error_type="EmptyContent",
                            error_message="No content extracted from page",
                        )
                        continue

                    # Chunk content
                    chunks_text = chunking_service.chunk_text(
                        text=page_data["content"],
                        preserve_heading=page_data.get("heading"),
                    )

                    if not chunks_text:
                        job.add_error(
                            page_url=page_url,
                            error_type="ChunkingFailed",
                            error_message="No chunks generated from content",
                        )
                        continue

                    # Generate embeddings
                    try:
                        embeddings = cohere_service.embed(
                            texts=chunks_text,
                            input_type="search_document",
                        )
                    except Exception as e:
                        job.add_error(
                            page_url=page_url,
                            error_type="EmbeddingError",
                            error_message=f"Cohere embedding failed: {str(e)}",
                        )
                        continue

                    # Create DocumentChunk objects
                    chunks = []
                    for idx, (chunk_text, embedding) in enumerate(
                        zip(chunks_text, embeddings)
                    ):
                        chunk = DocumentChunk(
                            content_text=chunk_text,
                            embedding_vector=embedding,
                            page_url=page_data["url"],
                            page_title=page_data["title"],
                            section_heading=page_data.get("heading"),
                            chunk_index=idx,
                            character_count=len(chunk_text),
                        )
                        chunks.append(chunk)

                    # Upsert to Qdrant
                    try:
                        vectors = [c.embedding_vector for c in chunks]
                        payloads = [c.to_qdrant_payload() for c in chunks]
                        ids = [c.chunk_id for c in chunks]

                        qdrant_service.upsert_vectors(
                            vectors=vectors,
                            payloads=payloads,
                            ids=ids,
                        )

                        job.chunks_created += len(chunks)
                        job.pages_processed += 1

                        logger.info(
                            f"Processed page {page_url}: {len(chunks)} chunks",
                            extra={
                                "page_url": page_url,
                                "chunk_count": len(chunks),
                            },
                        )

                    except Exception as e:
                        job.add_error(
                            page_url=page_url,
                            error_type="QdrantError",
                            error_message=f"Vector upsert failed: {str(e)}",
                        )
                        continue

                except IngestionError as e:
                    # Log error and continue with next page
                    job.add_error(
                        page_url=page_url,
                        error_type=e.details.get("error_type", "IngestionError"),
                        error_message=e.message,
                    )
                    logger.warning(f"Failed to process {page_url}: {e.message}")
                    continue

                except Exception as e:
                    # Unexpected error - log and continue
                    job.add_error(
                        page_url=page_url,
                        error_type="UnexpectedError",
                        error_message=str(e),
                    )
                    logger.error(
                        f"Unexpected error processing {page_url}: {e}",
                        exc_info=True,
                    )
                    continue

            # Mark job as completed
            job.mark_completed()

            logger.info(
                f"Ingestion job {job.job_id} completed",
                extra={
                    "job_id": str(job.job_id),
                    "pages_processed": job.pages_processed,
                    "chunks_created": job.chunks_created,
                    "errors": len(job.errors_encountered),
                },
            )

            return job

        except Exception as e:
            logger.error(f"Critical ingestion error: {e}", exc_info=True)
            job.mark_failed(f"Critical error: {str(e)}")
            return job


# Global service instance
ingestion_service = IngestionService()
