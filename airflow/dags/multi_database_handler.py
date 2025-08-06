import logging
import os
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


class DatabaseError(Exception):
    """Raised when database operations fail"""

    pass


class MultiDatabaseHandler:
    """Handles database operations for multiple databases"""

    def __init__(self, database_configs: Dict[str, str] = None):
        """Initialize the multi-database handler

        Args:
            database_configs: Dictionary of database name to connection string mapping
        """
        if database_configs is None:
            # Default configurations for both databases
            database_configs = {
                "airflow": os.getenv(
                    "AIRFLOW_DB_CONN",
                    "postgresql+psycopg2://airflow:airflow@airflow-postgres:5432/airflow",
                ),
                "main_app": os.getenv(
                    "MAIN_APP_DB_CONN",
                    "postgresql+psycopg2://postgres:postgres@travel-recommendation-db-1:5432/travel_recommendation",
                ),
            }

        self.database_configs = database_configs
        self.engines = {}
        self._initialize_engines()

    def _initialize_engines(self):
        """Initialize SQLAlchemy engines for all databases"""
        for db_name, connection_string in self.database_configs.items():
            try:
                self.engines[db_name] = create_engine(connection_string)
                logging.info(f"Database engine initialized successfully for {db_name}")
            except Exception as e:
                error_msg = f"Failed to initialize database engine for {db_name}: {e}"
                logging.error(error_msg)
                # Don't raise here, just log the error and continue with other databases

    def create_flight_tickets_table(self, db_name: str, connection):
        """Create the flight_tickets table if it doesn't exist

        Args:
            db_name: Name of the database
            connection: SQLAlchemy connection object
        """
        create_table_query = """
        CREATE TABLE IF NOT EXISTS flight_tickets (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL,
            origin VARCHAR(5) NOT NULL,
            destination VARCHAR(5) NOT NULL,
            departure_time TIMESTAMP NOT NULL,
            arrival_time TIMESTAMP NOT NULL,
            seat_number VARCHAR(10),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

        # Add unique constraint if it doesn't exist
        add_constraint_query = """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'flight_tickets_user_origin_dest_departure_key'
            ) THEN
                ALTER TABLE flight_tickets
                ADD CONSTRAINT flight_tickets_user_origin_dest_departure_key
                UNIQUE(user_id, origin, destination, departure_time);
            END IF;
        END $$;
        """

        try:
            connection.execute(text(create_table_query))
            connection.execute(text(add_constraint_query))
            logging.info(
                f"Flight tickets table created/verified successfully in {db_name}"
            )

            # Create performance indexes
            self._create_performance_indexes(db_name, connection)

        except SQLAlchemyError as e:
            error_msg = f"Failed to create flight_tickets table in {db_name}: {e}"
            logging.error(error_msg)
            raise DatabaseError(error_msg)

    def _create_performance_indexes(self, db_name: str, connection):
        """Create performance indexes for search queries"""
        indexes = [
            (
                "idx_flight_tickets_user_id",
                "CREATE INDEX IF NOT EXISTS idx_flight_tickets_user_id ON flight_tickets(user_id)",
            ),
            (
                "idx_flight_tickets_origin",
                "CREATE INDEX IF NOT EXISTS idx_flight_tickets_origin ON flight_tickets(origin)",
            ),
            (
                "idx_flight_tickets_destination",
                "CREATE INDEX IF NOT EXISTS idx_flight_tickets_destination ON flight_tickets(destination)",
            ),
            (
                "idx_flight_tickets_departure_time",
                "CREATE INDEX IF NOT EXISTS idx_flight_tickets_departure_time ON flight_tickets(departure_time)",
            ),
            (
                "idx_flight_tickets_created_at",
                "CREATE INDEX IF NOT EXISTS idx_flight_tickets_created_at ON flight_tickets(created_at)",
            ),
        ]

        for index_name, index_query in indexes:
            try:
                connection.execute(text(index_query))
                logging.info(f"Created/verified index {index_name} in {db_name}")
            except SQLAlchemyError as e:
                logging.warning(
                    f"Failed to create index {index_name} in {db_name}: {e}"
                )
                # Continue with other indexes

    def insert_flight_ticket(self, db_name: str, connection, record: Dict[str, Any]):
        """Insert a single flight ticket record

        Args:
            db_name: Name of the database
            connection: SQLAlchemy connection object
            record: Dictionary containing ticket data

        Raises:
            DatabaseError: If insertion fails
        """
        insert_query = """
        INSERT INTO flight_tickets (user_id, origin, destination, departure_time, arrival_time, seat_number, notes)
        VALUES (:user_id, :origin, :destination, :departure_time, :arrival_time, :seat_number, :notes)
        ON CONFLICT (user_id, origin, destination, departure_time)
        DO UPDATE SET
            arrival_time = EXCLUDED.arrival_time,
            seat_number = EXCLUDED.seat_number,
            notes = EXCLUDED.notes,
            updated_at = CURRENT_TIMESTAMP
        """
        try:
            connection.execute(text(insert_query), record)
            logging.info(f"Successfully inserted/updated record in {db_name}: {record}")
        except SQLAlchemyError as e:
            error_msg = f"Failed to insert record in {db_name} {record}: {e}"
            logging.error(error_msg)
            raise DatabaseError(error_msg)

    def bulk_insert_flight_tickets(
        self, records: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Bulk insert flight ticket records into all databases using optimized batch operations

        Args:
            records: List of dictionaries containing ticket data

        Returns:
            Dictionary with database name as key and number of successful inserts as value
        """
        results = {}

        for db_name, engine in self.engines.items():
            if engine is None:
                logging.warning(f"Skipping {db_name} - engine not initialized")
                results[db_name] = 0
                continue

            successful_inserts = 0
            try:
                with engine.begin() as connection:
                    # Create table if it doesn't exist
                    self.create_flight_tickets_table(db_name, connection)

                    # Use executemany for bulk insert with conflict resolution
                    # Note: This query is used in the _bulk_insert_with_batching method

                    try:
                        # Use a more efficient bulk insert approach
                        successful_inserts = self._bulk_insert_with_batching(
                            db_name, connection, records
                        )

                        logging.info(
                            f"Successfully bulk inserted {successful_inserts} records in {db_name}"
                        )

                    except SQLAlchemyError as e:
                        # Fallback to individual inserts if bulk insert fails
                        logging.warning(
                            f"Bulk insert failed for {db_name}, falling back to individual inserts: {e}"
                        )
                        successful_inserts = self._fallback_individual_inserts(
                            db_name, connection, records
                        )

                    results[db_name] = successful_inserts

                    # Monitor performance
                    if successful_inserts > 0:
                        self.monitor_bulk_insert_performance(
                            db_name, successful_inserts, 0.1
                        )  # Estimate duration

            except Exception as e:
                error_msg = f"Failed to bulk insert records in {db_name}: {e}"
                logging.error(error_msg)
                results[db_name] = 0

        return results

    def _fallback_individual_inserts(
        self, db_name: str, connection, records: List[Dict[str, Any]]
    ) -> int:
        """Fallback method for individual inserts when bulk insert fails"""
        successful_inserts = 0

        for record in records:
            try:
                self.insert_flight_ticket(db_name, connection, record)
                successful_inserts += 1
            except DatabaseError as e:
                logging.error(f"Failed to insert record in {db_name}: {e}")
                # Continue with other records

        return successful_inserts

    def _bulk_insert_with_batching(
        self, db_name: str, connection, records: List[Dict[str, Any]]
    ) -> int:
        """Bulk insert using batched approach for better performance"""
        if not records:
            return 0

        successful_inserts = 0
        batch_size = 100  # Process in batches of 100

        for i in range(0, len(records), batch_size):
            batch = records[i : i + batch_size]

            try:
                # Use a simpler insert without ON CONFLICT for better performance
                # We'll handle conflicts differently
                batch_insert_query = """
                INSERT INTO flight_tickets (user_id, origin, destination, departure_time, arrival_time, seat_number, notes)
                VALUES (:user_id, :origin, :destination, :departure_time, :arrival_time, :seat_number, :notes)
                """

                # Execute batch insert
                connection.execute(text(batch_insert_query), batch)
                successful_inserts += len(batch)

                logging.info(
                    f"Successfully inserted batch of {len(batch)} records in {db_name}"
                )

            except SQLAlchemyError as e:
                # If batch insert fails, try individual inserts for this batch
                logging.warning(
                    f"Batch insert failed for {db_name}, trying individual inserts: {e}"
                )

                for record in batch:
                    try:
                        # Use the individual insert method which handles conflicts
                        self.insert_flight_ticket(db_name, connection, record)
                        successful_inserts += 1
                    except DatabaseError as e:
                        logging.error(f"Failed to insert record in {db_name}: {e}")
                        # Continue with other records

        return successful_inserts

    def get_flight_tickets_count(self, db_name: str) -> int:
        """Get the count of flight tickets in a specific database

        Args:
            db_name: Name of the database

        Returns:
            Number of flight tickets
        """
        if db_name not in self.engines or self.engines[db_name] is None:
            return 0

        try:
            with self.engines[db_name].connect() as connection:
                result = connection.execute(text("SELECT COUNT(*) FROM flight_tickets"))
                return result.scalar()
        except Exception as e:
            logging.error(f"Failed to get flight tickets count from {db_name}: {e}")
            return 0

    def get_database_performance_stats(self, db_name: str) -> Dict[str, Any]:
        """Get database performance statistics

        Args:
            db_name: Name of the database

        Returns:
            Dictionary containing performance statistics
        """
        if db_name not in self.engines or self.engines[db_name] is None:
            return {}

        try:
            with self.engines[db_name].connect() as connection:
                # Get table size
                size_query = """
                SELECT
                    pg_size_pretty(pg_total_relation_size('flight_tickets')) as table_size,
                    pg_total_relation_size('flight_tickets') as size_bytes
                FROM information_schema.tables
                WHERE table_name = 'flight_tickets'
                """

                # Get index usage statistics
                index_query = """
                SELECT
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan as index_scans,
                    idx_tup_read as tuples_read,
                    idx_tup_fetch as tuples_fetched
                FROM pg_stat_user_indexes
                WHERE tablename = 'flight_tickets'
                ORDER BY idx_scan DESC
                """

                # Get slow query information
                slow_query = """
                SELECT
                    query,
                    calls,
                    total_time,
                    mean_time,
                    rows
                FROM pg_stat_statements
                WHERE query LIKE '%flight_tickets%'
                ORDER BY mean_time DESC
                LIMIT 5
                """

                size_result = connection.execute(text(size_query))
                index_result = connection.execute(text(index_query))

                size_stats = size_result.fetchone()
                index_stats = index_result.fetchall()

                stats = {
                    "table_size": size_stats[0] if size_stats else "Unknown",
                    "size_bytes": size_stats[1] if size_stats else 0,
                    "index_usage": [
                        {
                            "index_name": row[2],
                            "scans": row[3],
                            "tuples_read": row[4],
                            "tuples_fetched": row[5],
                        }
                        for row in index_stats
                    ],
                }

                # Try to get slow query stats (might not be available)
                try:
                    slow_result = connection.execute(text(slow_query))
                    slow_stats = slow_result.fetchall()
                    stats["slow_queries"] = [
                        {
                            "query": row[0][:100] + "..."
                            if len(row[0]) > 100
                            else row[0],
                            "calls": row[1],
                            "total_time": row[2],
                            "mean_time": row[3],
                            "rows": row[4],
                        }
                        for row in slow_stats
                    ]
                except Exception:
                    stats["slow_queries"] = []

                return stats

        except Exception as e:
            logging.error(f"Failed to get performance stats from {db_name}: {e}")
            return {}

    def monitor_bulk_insert_performance(
        self, db_name: str, record_count: int, duration: float
    ) -> Dict[str, Any]:
        """Monitor and log bulk insert performance metrics

        Args:
            db_name: Name of the database
            record_count: Number of records inserted
            duration: Time taken for the operation

        Returns:
            Dictionary containing performance metrics
        """
        records_per_second = record_count / duration if duration > 0 else 0
        throughput_mb = (
            (record_count * 200) / (1024 * 1024) / duration if duration > 0 else 0
        )  # Estimate 200 bytes per record

        metrics = {
            "database": db_name,
            "records_inserted": record_count,
            "duration_seconds": duration,
            "records_per_second": records_per_second,
            "throughput_mbps": throughput_mb,
            "timestamp": datetime.now().isoformat(),
        }

        # Log performance metrics
        logging.info(f"Performance metrics for {db_name}:")
        logging.info(f"  - Records inserted: {record_count}")
        logging.info(f"  - Duration: {duration:.2f} seconds")
        logging.info(f"  - Throughput: {records_per_second:.2f} records/second")
        logging.info(f"  - Data rate: {throughput_mb:.2f} MB/s")

        return metrics

    def close(self):
        """Close all database engines"""
        for db_name, engine in self.engines.items():
            if engine:
                try:
                    engine.dispose()
                    logging.info(f"Closed database engine for {db_name}")
                except Exception as e:
                    logging.error(f"Failed to close database engine for {db_name}: {e}")
