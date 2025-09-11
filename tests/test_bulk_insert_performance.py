#!/usr/bin/env python3
"""
Performance test script for bulk insert operations
"""

import logging
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List

# Add the dags directory to Python path for imports
sys.path.append(os.path.dirname(__file__))

from multi_database_handler import MultiDatabaseHandler
from sqlalchemy import text

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def generate_test_data(record_count: int) -> List[Dict[str, Any]]:
    """Generate test flight ticket data"""
    test_data = []
    base_time = datetime.now() + timedelta(days=30)

    for i in range(record_count):
        record = {
            "user_id": f"user-{i % 100:03d}",
            "origin": f"ORI{i % 10:02d}",
            "destination": f"DST{i % 10:02d}",
            "departure_time": (base_time + timedelta(hours=i)).isoformat(),
            "arrival_time": (base_time + timedelta(hours=i + 2)).isoformat(),
            "seat_number": f"A{i % 30 + 1}",
            "notes": f"Test record {i}",
        }
        test_data.append(record)

    return test_data


def test_bulk_insert_performance():
    """Test bulk insert performance"""
    logger.info("=== Testing Bulk Insert Performance ===")

    # Test different batch sizes
    batch_sizes = [10, 50, 100, 500]

    for batch_size in batch_sizes:
        logger.info(f"\n--- Testing batch size: {batch_size} ---")

        # Generate test data
        test_data = generate_test_data(batch_size)

        # Initialize database handler
        db_handler = MultiDatabaseHandler()

        try:
            # Measure performance
            start_time = time.time()

            results = db_handler.bulk_insert_flight_tickets(test_data)

            end_time = time.time()
            duration = end_time - start_time

            # Calculate performance metrics
            total_inserted = sum(results.values())
            records_per_second = total_inserted / duration if duration > 0 else 0

            logger.info(f"✅ Batch size {batch_size}:")
            logger.info(f"   - Duration: {duration:.2f} seconds")
            logger.info(f"   - Total inserted: {total_inserted}")
            logger.info(f"   - Records per second: {records_per_second:.2f}")
            logger.info(f"   - Results by database: {results}")

        except Exception as e:
            logger.error(f"❌ Failed to test batch size {batch_size}: {e}")
        finally:
            db_handler.close()


def test_search_query_performance():
    """Test search query performance"""
    logger.info("\n=== Testing Search Query Performance ===")

    db_handler = MultiDatabaseHandler()

    try:
        # Test different query types
        queries = [
            ("SELECT COUNT(*) FROM flight_tickets", "Count all records"),
            (
                "SELECT * FROM flight_tickets WHERE user_id = 'user-001'",
                "Filter by user_id",
            ),
            ("SELECT * FROM flight_tickets WHERE origin = 'ORI01'", "Filter by origin"),
            (
                "SELECT * FROM flight_tickets WHERE departure_time > '2025-09-01'",
                "Filter by date",
            ),
            (
                "SELECT user_id, COUNT(*) FROM flight_tickets GROUP BY user_id",
                "Group by user",
            ),
        ]

        for query, description in queries:
            logger.info(f"\n--- Testing: {description} ---")

            start_time = time.time()

            try:
                with db_handler.engines["main_app"].connect() as connection:
                    result = connection.execute(text(query))
                    rows = result.fetchall()

                end_time = time.time()
                duration = end_time - start_time

                logger.info(f"✅ Query: {description}")
                logger.info(f"   - Duration: {duration:.4f} seconds")
                logger.info(f"   - Rows returned: {len(rows)}")

            except Exception as e:
                logger.error(f"❌ Query failed: {description} - {e}")

    except Exception as e:
        logger.error(f"❌ Failed to test search queries: {e}")
    finally:
        db_handler.close()


def analyze_current_indexes():
    """Analyze current database indexes"""
    logger.info("\n=== Analyzing Current Indexes ===")

    db_handler = MultiDatabaseHandler()

    try:
        with db_handler.engines["main_app"].connect() as connection:
            # Get current indexes
            index_query = """
            SELECT
                indexname,
                indexdef,
                schemaname,
                tablename
            FROM pg_indexes
            WHERE tablename = 'flight_tickets'
            ORDER BY indexname;
            """

            result = connection.execute(text(index_query))
            indexes = result.fetchall()

            logger.info("Current indexes on flight_tickets table:")
            for index in indexes:
                logger.info(f"   - {index[0]}: {index[1][:100]}...")

            # Check table statistics
            stats_query = """
            SELECT
                schemaname,
                tablename,
                attname,
                n_distinct,
                correlation
            FROM pg_stats
            WHERE tablename = 'flight_tickets'
            ORDER BY attname;
            """

            result = connection.execute(text(stats_query))
            stats = result.fetchall()

            logger.info("\nTable statistics:")
            for stat in stats:
                logger.info(
                    f"   - {stat[2]}: distinct={stat[3]}, correlation={stat[4]}"
                )

    except Exception as e:
        logger.error(f"❌ Failed to analyze indexes: {e}")
    finally:
        db_handler.close()


def suggest_optimizations():
    """Suggest database optimizations"""
    logger.info("\n=== Suggested Optimizations ===")

    suggestions = [
        "1. Add indexes for common search patterns:",
        "   - CREATE INDEX idx_flight_tickets_user_id ON flight_tickets(user_id);",
        "   - CREATE INDEX idx_flight_tickets_origin ON flight_tickets(origin);",
        "   - CREATE INDEX idx_flight_tickets_destination ON flight_tickets(destination);",
        "   - CREATE INDEX idx_flight_tickets_departure_time ON flight_tickets(departure_time);",
        "",
        "2. Implement batch insert optimization:",
        "   - Use executemany() for bulk inserts instead of individual inserts",
        "   - Consider using COPY command for very large datasets",
        "   - Implement connection pooling for better performance",
        "",
        "3. Add database monitoring:",
        "   - Monitor query execution times",
        "   - Track index usage statistics",
        "   - Set up alerts for slow queries",
        "",
        "4. Performance tuning:",
        "   - Adjust PostgreSQL configuration (shared_buffers, work_mem)",
        "   - Consider partitioning for large tables",
        "   - Implement read replicas for heavy read workloads",
    ]

    for suggestion in suggestions:
        logger.info(suggestion)


def main():
    """Run all performance tests"""
    logger.info("🚀 Starting Database Performance Tests")
    logger.info("=" * 50)

    try:
        test_bulk_insert_performance()
        test_search_query_performance()
        analyze_current_indexes()
        suggest_optimizations()

        logger.info("\n✅ All performance tests completed!")

    except Exception as e:
        logger.error(f"❌ Performance test suite failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
