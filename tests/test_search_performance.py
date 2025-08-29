#!/usr/bin/env python3
"""
Test for search performance with indexed data
"""

import logging
import os
import sys
import time

# Add the dags directory to Python path for imports
sys.path.append(os.path.dirname(__file__))

from multi_database_handler import MultiDatabaseHandler
from sqlalchemy import text

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_search_performance():
    """Test search performance with indexed data"""
    logger.info("=== Testing Search Performance with Indexed Data ===")

    # Initialize database handler
    db_handler = MultiDatabaseHandler()

    try:
        # Test different search queries
        queries = [
            {
                "name": "Count all records",
                "query": "SELECT COUNT(*) FROM flight_tickets",
            },
            {
                "name": "Filter by user_id",
                "query": "SELECT COUNT(*) FROM flight_tickets WHERE user_id = 'user-000000'",
            },
            {
                "name": "Filter by origin",
                "query": "SELECT COUNT(*) FROM flight_tickets WHERE origin = 'ORI00'",
            },
            {
                "name": "Filter by destination",
                "query": "SELECT COUNT(*) FROM flight_tickets WHERE destination = 'DST00'",
            },
            {
                "name": "Filter by date range",
                "query": "SELECT COUNT(*) FROM flight_tickets WHERE departure_time > '2025-09-05'",
            },
            {
                "name": "Complex query with multiple filters",
                "query": "SELECT COUNT(*) FROM flight_tickets WHERE origin = 'ORI00' AND destination = 'DST00' AND departure_time > '2025-09-05'",
            },
            {
                "name": "Group by user",
                "query": "SELECT user_id, COUNT(*) FROM flight_tickets GROUP BY user_id LIMIT 10",
            },
            {
                "name": "Order by departure time",
                "query": "SELECT user_id, origin, destination, departure_time FROM flight_tickets ORDER BY departure_time DESC LIMIT 10",
            },
        ]

        for query_info in queries:
            logger.info(f"\n--- Testing: {query_info['name']} ---")

            # Test on both databases
            for db_name in ["airflow", "main_app"]:
                try:
                    start_time = time.time()

                    # Execute query
                    with db_handler.engines[db_name].connect() as connection:
                        result = connection.execute(text(query_info["query"]))
                        rows = result.fetchall()

                    end_time = time.time()
                    duration = end_time - start_time

                    logger.info(f"✅ {db_name}:")
                    logger.info(f"   - Duration: {duration:.4f} seconds")
                    logger.info(f"   - Rows returned: {len(rows)}")

                except Exception as e:
                    logger.error(f"❌ {db_name} failed: {e}")

    except Exception as e:
        logger.error(f"❌ Search performance test failed: {e}")
    finally:
        db_handler.close()


if __name__ == "__main__":
    test_search_performance()
