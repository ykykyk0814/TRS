#!/usr/bin/env python3
"""
Script to recreate the database with the correct schema.
WARNING: This will delete all existing data!
"""

import asyncio
import os
import logging
from app.db import recreate_tables
from app.models import User  # Import to register the model

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    try:
        # Delete the existing database file
        db_path = "./test.db"
        if os.path.exists(db_path):
            os.remove(db_path)
            logger.info(f"Deleted existing database: {db_path}")

        # Recreate all tables with the correct schema
        await recreate_tables()
        logger.info("Database recreated successfully with correct schema!")

        # Verify the schema
        import sqlite3

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()

        logger.info("Users table columns:")
        for col in columns:
            logger.info(f"  {col[1]} ({col[2]})")

        conn.close()

    except Exception as e:
        logger.error(f"Error recreating database: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
