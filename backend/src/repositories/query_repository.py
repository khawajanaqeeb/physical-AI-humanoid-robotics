"""
Query repository for database operations.

This module handles storing and retrieving queries from the database.
"""

from uuid import UUID
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.models import Query
from src.config.logging import get_logger

logger = get_logger(__name__)


class QueryRepository:
    """Repository for query database operations."""

    async def save_query(self, query: Query) -> UUID:
        """
        Save a query to the database.

        Args:
            query: Query object to save

        Returns:
            UUID of the saved query

        Example:
            >>> repo = QueryRepository()
            >>> query_id = await repo.save_query(query)
        """
        async with get_db_session() as session:
            try:
                # Convert Query model to database insert
                insert_query = text("""
                    INSERT INTO queries (
                        query_id,
                        query_text,
                        user_session_id,
                        selected_text,
                        retrieved_chunk_ids,
                        answer_text,
                        citations,
                        similarity_scores,
                        retrieval_time_ms,
                        answer_time_ms,
                        citation_time_ms,
                        total_time_ms,
                        timestamp
                    ) VALUES (
                        :query_id,
                        :query_text,
                        :user_session_id,
                        :selected_text,
                        :retrieved_chunk_ids,
                        :answer_text,
                        :citations,
                        :similarity_scores,
                        :retrieval_time_ms,
                        :answer_time_ms,
                        :citation_time_ms,
                        :total_time_ms,
                        :timestamp
                    )
                    RETURNING query_id
                """)

                # Convert citations to JSONB format
                citations_json = [c.model_dump() for c in query.citations]

                result = await session.execute(
                    insert_query,
                    {
                        "query_id": query.query_id,
                        "query_text": query.query_text,
                        "user_session_id": query.user_session_id,
                        "selected_text": query.selected_text,
                        "retrieved_chunk_ids": query.retrieved_chunk_ids,
                        "answer_text": query.answer_text,
                        "citations": citations_json,
                        "similarity_scores": query.similarity_scores,
                        "retrieval_time_ms": query.retrieval_time_ms,
                        "answer_time_ms": query.answer_time_ms,
                        "citation_time_ms": query.citation_time_ms,
                        "total_time_ms": query.total_time_ms,
                        "timestamp": query.timestamp,
                    }
                )

                await session.commit()

                query_id = result.scalar_one()

                logger.info(
                    "query_saved",
                    query_id=str(query_id),
                    session_id=str(query.user_session_id),
                )

                return query_id

            except Exception as e:
                await session.rollback()
                logger.error(
                    "query_save_failed",
                    error=str(e),
                    error_type=type(e).__name__,
                )
                raise

    async def get_query_by_id(self, query_id: UUID) -> Optional[dict]:
        """
        Retrieve a query by ID.

        Args:
            query_id: Query UUID

        Returns:
            Query dictionary or None if not found

        Example:
            >>> repo = QueryRepository()
            >>> query = await repo.get_query_by_id(UUID("..."))
        """
        async with get_db_session() as session:
            try:
                select_query = text("""
                    SELECT *
                    FROM queries
                    WHERE query_id = :query_id
                """)

                result = await session.execute(
                    select_query,
                    {"query_id": query_id}
                )

                row = result.fetchone()

                if row:
                    logger.debug("query_retrieved", query_id=str(query_id))
                    return dict(row._mapping)
                else:
                    logger.warning("query_not_found", query_id=str(query_id))
                    return None

            except Exception as e:
                logger.error(
                    "query_retrieval_failed",
                    query_id=str(query_id),
                    error=str(e),
                )
                raise

    async def get_session_queries(self, session_id: UUID, limit: int = 10) -> list[dict]:
        """
        Get recent queries for a session.

        Args:
            session_id: Session UUID
            limit: Maximum number of queries to return

        Returns:
            List of query dictionaries

        Example:
            >>> repo = QueryRepository()
            >>> queries = await repo.get_session_queries(UUID("..."))
        """
        async with get_db_session() as session:
            try:
                select_query = text("""
                    SELECT *
                    FROM queries
                    WHERE user_session_id = :session_id
                    ORDER BY timestamp DESC
                    LIMIT :limit
                """)

                result = await session.execute(
                    select_query,
                    {"session_id": session_id, "limit": limit}
                )

                rows = result.fetchall()

                logger.debug(
                    "session_queries_retrieved",
                    session_id=str(session_id),
                    count=len(rows),
                )

                return [dict(row._mapping) for row in rows]

            except Exception as e:
                logger.error(
                    "session_queries_retrieval_failed",
                    session_id=str(session_id),
                    error=str(e),
                )
                raise


# Singleton instance
_query_repository: Optional[QueryRepository] = None


def get_query_repository() -> QueryRepository:
    """
    Get or create the Query Repository instance.

    Returns:
        QueryRepository singleton instance
    """
    global _query_repository

    if _query_repository is None:
        _query_repository = QueryRepository()

    return _query_repository
