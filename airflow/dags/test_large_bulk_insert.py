#!/usr/bin/env python3
"""
Test for large bulk insert performance
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


def generate_large_test_data(record_count: int) -> List[Dict[str, Any]]:
    """Generate large test flight ticket data"""
    test_data = []
    base_time = datetime.now() + timedelta(days=30)

    for i in range(record_count):
        # Ensure each record is unique
        record = {
            "user_id": f"user-{i:06d}",
            "origin": f"ORI{i % 100:02d}",
            "destination": f"DST{i % 100:02d}",
            "departure_time": (base_time + timedelta(hours=i)).isoformat(),
            "arrival_time": (base_time + timedelta(hours=i + 2)).isoformat(),
            "seat_number": f"A{i % 30 + 1}",
            "notes": f"Test record {i}",
        }
        test_data.append(record)

    return test_data


def test_large_bulk_insert():
    """Test large bulk insert performance"""
    logger.info("=== Testing Large Bulk Insert Performance ===")

    # Test different batch sizes
    batch_sizes = [100, 500, 1000]

    for batch_size in batch_sizes:
        logger.info(f"\n--- Testing batch size: {batch_size} ---")

        # Generate test data
        test_data = generate_large_test_data(batch_size)

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
            logger.info(f"   - Duration: {duration:.3f} seconds")
            logger.info(f"   - Total inserted: {total_inserted}")
            logger.info(f"   - Records per second: {records_per_second:.2f}")
            logger.info(f"   - Results by database: {results}")

            if total_inserted > 0:
                logger.info(f"✅ Bulk insert working for {batch_size} records!")
            else:
                logger.error(f"❌ Bulk insert failed for {batch_size} records!")

        except Exception as e:
            logger.error(f"❌ Large bulk insert test failed for {batch_size}: {e}")
        finally:
            db_handler.close()


if __name__ == "__main__":
    test_large_bulk_insert()
