#!/usr/bin/env python3
"""
Simple test for bulk insert with unique data
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

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def generate_unique_test_data(record_count: int) -> List[Dict[str, Any]]:
    """Generate unique test flight ticket data"""
    test_data = []
    base_time = datetime.now() + timedelta(days=30)

    for i in range(record_count):
        # Ensure each record is unique
        record = {
            "user_id": f"user-{i:03d}",
            "origin": f"ORI{i % 10:02d}",
            "destination": f"DST{i % 10:02d}",
            "departure_time": (base_time + timedelta(hours=i)).isoformat(),
            "arrival_time": (base_time + timedelta(hours=i + 2)).isoformat(),
            "seat_number": f"A{i % 30 + 1}",
            "notes": f"Test record {i}",
        }
        test_data.append(record)

    return test_data


def test_simple_bulk_insert():
    """Test bulk insert with unique data"""
    logger.info("=== Testing Simple Bulk Insert ===")

    # Generate unique test data
    test_data = generate_unique_test_data(10)

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

        logger.info("✅ Simple bulk insert test:")
        logger.info(f"   - Duration: {duration:.2f} seconds")
        logger.info(f"   - Total inserted: {total_inserted}")
        logger.info(f"   - Records per second: {records_per_second:.2f}")
        logger.info(f"   - Results by database: {results}")

        if total_inserted > 0:
            logger.info("✅ Bulk insert is working!")
        else:
            logger.error("❌ Bulk insert failed!")

    except Exception as e:
        logger.error(f"❌ Simple bulk insert test failed: {e}")
    finally:
        db_handler.close()


if __name__ == "__main__":
    test_simple_bulk_insert()
