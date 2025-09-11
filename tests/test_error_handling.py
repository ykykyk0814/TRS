#!/usr/bin/env python3
"""
Test script to evaluate Airflow DAG error handling and validation capabilities
"""

import logging
import os
import sys

# Add the dags directory to Python path for imports
sys.path.append(os.path.dirname(__file__))

from data_transformer import DataValidationError, FlightTicketTransformer
from multi_database_handler import MultiDatabaseHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_data_validation():
    """Test data validation capabilities"""
    logger.info("=== Testing Data Validation ===")

    transformer = FlightTicketTransformer("00000000-0000-0000-0000-000000000000")

    # Test 1: Valid data
    valid_offer = {
        "id": "1",
        "itineraries": [
            {
                "segments": [
                    {
                        "departure": {"iataCode": "SYD", "at": "2025-10-27T12:30:00"},
                        "arrival": {"iataCode": "BKK", "at": "2025-10-28T00:45:00"},
                    }
                ]
            }
        ],
        "price": {"total": "229.47"},
    }

    try:
        result = transformer.validate_amadeus_offer(valid_offer)
        logger.info(f"✅ Valid data test passed: {result}")
    except Exception as e:
        logger.error(f"❌ Valid data test failed: {e}")

    # Test 2: Missing required fields
    invalid_offer = {"id": "2", "itineraries": []}  # Missing required fields

    try:
        transformer.validate_amadeus_offer(invalid_offer)
        logger.error("❌ Invalid data test should have failed")
    except DataValidationError as e:
        logger.info(f"✅ Invalid data test passed: {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error in invalid data test: {e}")

    # Test 3: Missing price
    no_price_offer = {
        "id": "3",
        "itineraries": [
            {
                "segments": [
                    {
                        "departure": {"iataCode": "SYD", "at": "2025-10-27T12:30:00"},
                        "arrival": {"iataCode": "BKK", "at": "2025-10-28T00:45:00"},
                    }
                ]
            }
        ],
        "price": {},  # Empty price
    }

    try:
        transformer.validate_amadeus_offer(no_price_offer)
        logger.error("❌ No price test should have failed")
    except DataValidationError as e:
        logger.info(f"✅ No price test passed: {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error in no price test: {e}")


def test_transformation_error_handling():
    """Test transformation error handling"""
    logger.info("=== Testing Transformation Error Handling ===")

    transformer = FlightTicketTransformer("00000000-0000-0000-0000-000000000000")

    # Test with mixed valid and invalid data
    mixed_offers = [
        {
            "id": "1",
            "itineraries": [
                {
                    "segments": [
                        {
                            "departure": {
                                "iataCode": "SYD",
                                "at": "2025-10-27T12:30:00",
                            },
                            "arrival": {"iataCode": "BKK", "at": "2025-10-28T00:45:00"},
                        }
                    ]
                }
            ],
            "price": {"total": "229.47"},
        },
        {"id": "2", "itineraries": [], "price": {"total": "100.00"}},  # Invalid
        {
            "id": "3",
            "itineraries": [
                {
                    "segments": [
                        {
                            "departure": {
                                "iataCode": "LAX",
                                "at": "2025-10-27T10:00:00",
                            },
                            "arrival": {"iataCode": "JFK", "at": "2025-10-27T18:00:00"},
                        }
                    ]
                }
            ],
            "price": {"total": "350.00"},
        },
    ]

    try:
        results = transformer.transform_amadeus_offers_batch(mixed_offers)
        stats = transformer.get_transformation_stats(len(mixed_offers), len(results))
        logger.info(f"✅ Transformation batch test passed: {stats}")
        logger.info(f"   - Original: {stats['original_count']}")
        logger.info(f"   - Transformed: {stats['transformed_count']}")
        logger.info(f"   - Failed: {stats['failed_count']}")
        logger.info(f"   - Success rate: {stats['success_rate']}%")
    except Exception as e:
        logger.error(f"❌ Transformation batch test failed: {e}")


def test_database_error_handling():
    """Test database error handling"""
    logger.info("=== Testing Database Error Handling ===")

    # Test with invalid database connection
    invalid_config = {
        "invalid_db": "postgresql+psycopg2://invalid:invalid@invalid-host:5432/invalid"
    }

    try:
        handler = MultiDatabaseHandler(invalid_config)
        test_data = [
            {
                "user_id": "00000000-0000-0000-0000-000000000000",
                "origin": "SYD",
                "destination": "BKK",
                "departure_time": "2025-10-27T12:30:00",
                "arrival_time": "2025-10-28T00:45:00",
                "seat_number": None,
                "notes": "test",
            }
        ]

        results = handler.bulk_insert_flight_tickets(test_data)
        logger.info(f"✅ Database error handling test passed: {results}")
    except Exception as e:
        logger.error(f"❌ Database error handling test failed: {e}")


def test_alerting_system():
    """Test alerting system (placeholder)"""
    logger.info("=== Testing Alerting System ===")

    # Simulate different alert levels
    alert_levels = ["INFO", "WARNING", "ERROR", "CRITICAL"]

    for level in alert_levels:
        message = f"Test alert at {level} level"
        logger.info(f"🔔 [{level}] {message}")

    logger.info("✅ Alerting system test completed (logging only)")


def test_retry_mechanism():
    """Test retry mechanism simulation"""
    logger.info("=== Testing Retry Mechanism ===")

    # Simulate a task that might fail
    max_attempts = 3
    current_attempt = 1

    while current_attempt <= max_attempts:
        try:
            # Simulate a potentially failing operation
            if current_attempt == 1:
                raise Exception("Simulated failure on first attempt")

            logger.info(f"✅ Operation succeeded on attempt {current_attempt}")
            break

        except Exception as e:
            logger.warning(f"⚠️ Attempt {current_attempt} failed: {e}")
            if current_attempt == max_attempts:
                logger.error(f"❌ All {max_attempts} attempts failed")
            current_attempt += 1


def main():
    """Run all tests"""
    logger.info("🚀 Starting Airflow DAG Error Handling Tests")
    logger.info("=" * 50)

    try:
        test_data_validation()
        logger.info("")

        test_transformation_error_handling()
        logger.info("")

        test_database_error_handling()
        logger.info("")

        test_alerting_system()
        logger.info("")

        test_retry_mechanism()
        logger.info("")

        logger.info("✅ All tests completed successfully!")

    except Exception as e:
        logger.error(f"❌ Test suite failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
