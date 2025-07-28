import logging
import os
from typing import Any, Dict, List

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


class DatabaseError(Exception):
    """Raised when database operations fail"""

    pass


class FlightTicketDatabaseHandler:
    """Handles all database operations for flight tickets"""

    def __init__(self, connection_string: str = None):
        """Initialize the database handler

        Args:
            connection_string: Database connection string. If None, uses default Airflow DB.
        """
        self.connection_string = connection_string or os.getenv(
            "AIRFLOW_DB_CONN",
            "postgresql+psycopg2://airflow:airflow@airflow-postgres:5432/airflow",
        )
        self.engine = None
        self._initialize_engine()

    def _initialize_engine(self):
        """Initialize the SQLAlchemy engine"""
        try:
            self.engine = create_engine(self.connection_string)
            logging.info("Database engine initialized successfully")
        except Exception as e:
            error_msg = f"Failed to initialize database engine: {e}"
            logging.error(error_msg)
            raise DatabaseError(error_msg)

    def create_flight_tickets_table(self, connection):
        """Create the flight_tickets table if it doesn't exist

        Args:
            connection: SQLAlchemy connection object
        """
        create_table_query = """
        CREATE TABLE IF NOT EXISTS flight_tickets (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL,
            origin VARCHAR(3) NOT NULL,
            destination VARCHAR(3) NOT NULL,
            departure_time TIMESTAMP NOT NULL,
            arrival_time TIMESTAMP NOT NULL,
            seat_number VARCHAR(10),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        try:
            connection.execute(text(create_table_query))
            logging.info("Flight tickets table created/verified successfully")
        except SQLAlchemyError as e:
            error_msg = f"Failed to create flight_tickets table: {e}"
            logging.error(error_msg)
            raise DatabaseError(error_msg)

    def insert_flight_ticket(self, connection, record: Dict[str, Any]):
        """Insert a single flight ticket record

        Args:
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
            logging.info(f"Successfully inserted/updated record: {record}")
        except SQLAlchemyError as e:
            error_msg = f"Failed to insert record {record}: {e}"
            logging.error(error_msg)
            raise DatabaseError(error_msg)

    def bulk_insert_flight_tickets(self, records: List[Dict[str, Any]]) -> int:
        """Bulk insert flight ticket records

        Args:
            records: List of dictionaries containing ticket data

        Returns:
            int: Number of records successfully processed

        Raises:
            DatabaseError: If bulk insertion fails
        """
        if not records:
            logging.warning("No records to insert")
            return 0

        successful_inserts = 0

        try:
            with self.engine.begin() as conn:
                # Create table if it doesn't exist
                self.create_flight_tickets_table(conn)

                # Insert each record
                for record in records:
                    try:
                        self.insert_flight_ticket(conn, record)
                        successful_inserts += 1
                    except DatabaseError as e:
                        logging.error(f"Skipping failed record: {e}")
                        # Continue with other records instead of failing completely
                        continue

                logging.info(
                    f"Successfully processed {successful_inserts} out of {len(records)} records"
                )
                return successful_inserts

        except Exception as e:
            error_msg = f"Bulk insertion failed: {e}"
            logging.error(error_msg)
            raise DatabaseError(error_msg)

    def get_flight_tickets_count(self) -> int:
        """Get the total number of flight tickets in the database

        Returns:
            int: Number of tickets
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM flight_tickets"))
                count = result.scalar()
                logging.info(f"Total flight tickets in database: {count}")
                return count
        except SQLAlchemyError as e:
            error_msg = f"Failed to get ticket count: {e}"
            logging.error(error_msg)
            raise DatabaseError(error_msg)

    def close(self):
        """Close the database engine"""
        if self.engine:
            self.engine.dispose()
            logging.info("Database engine closed")
