#!/usr/bin/env python3
"""
Database initialization script.

This script runs all SQL migrations to set up the database schema.
Run this before starting the application for the first time.

Usage:
    python scripts/init_database.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import asyncpg
from config.settings import get_settings
from config.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


async def run_migrations():
    """Run all SQL migration files in order."""
    settings = get_settings()

    # Extract connection parameters from DATABASE_URL
    # Format: postgresql+asyncpg://user:password@host/database
    db_url = settings.database_url.replace("postgresql+asyncpg://", "")

    logger.info("connecting_to_database")

    try:
        # Connect directly with asyncpg
        conn = await asyncpg.connect(f"postgresql://{db_url}")

        logger.info("database_connected")

        # Get migration files in order
        migrations_dir = Path(__file__).parent.parent / "migrations"
        migration_files = sorted(migrations_dir.glob("*.sql"))

        if not migration_files:
            logger.warning("no_migrations_found", dir=str(migrations_dir))
            return

        logger.info("running_migrations", count=len(migration_files))

        # Run each migration
        for migration_file in migration_files:
            logger.info("running_migration", file=migration_file.name)

            with open(migration_file, "r") as f:
                sql = f.read()

            await conn.execute(sql)

            logger.info("migration_completed", file=migration_file.name)

        logger.info("all_migrations_completed", count=len(migration_files))

        await conn.close()
        logger.info("database_connection_closed")

    except Exception as e:
        logger.error("migration_failed", error=str(e), error_type=type(e).__name__)
        raise


async def verify_tables():
    """Verify that all expected tables exist."""
    settings = get_settings()
    db_url = settings.database_url.replace("postgresql+asyncpg://", "")

    conn = await asyncpg.connect(f"postgresql://{db_url}")

    # Expected tables
    expected_tables = ["queries", "feedback", "sync_jobs"]

    logger.info("verifying_tables")

    for table in expected_tables:
        result = await conn.fetchval(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = $1
            )
            """,
            table,
        )

        if result:
            logger.info("table_exists", table=table)
        else:
            logger.error("table_missing", table=table)
            raise RuntimeError(f"Table '{table}' was not created")

    await conn.close()

    logger.info("table_verification_passed", count=len(expected_tables))


async def main():
    """Main execution function."""
    logger.info("database_initialization_started")

    try:
        # Run migrations
        await run_migrations()

        # Verify tables
        await verify_tables()

        logger.info("database_initialization_completed")
        print("\n✅ Database initialization completed successfully!")
        print("The following tables have been created:")
        print("  - queries")
        print("  - feedback")
        print("  - sync_jobs")

    except Exception as e:
        logger.error("database_initialization_failed", error=str(e))
        print(f"\n❌ Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
