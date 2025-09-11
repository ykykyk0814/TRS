import logging
import os
import sys
from datetime import datetime, timedelta

import pendulum
import requests
from airflow.decorators import dag, task

# Add the dags directory to Python path for imports
sys.path.append(os.path.dirname(__file__))

from data_transformer import FlightTicketTransformer
from multi_database_handler import MultiDatabaseHandler

# DAG config
DAG_ID = "ticket_data_ingestion"
SCHEDULE_INTERVAL = "@hourly"  # TODO: adjust as needed
START_DATE = pendulum.now("UTC").subtract(days=1)
CATCHUP = False


# Custom exception classes
class DataValidationError(Exception):
    """Raised when data validation fails"""

    pass


class AmadeusAPIError(Exception):
    """Raised when Amadeus API calls fail"""

    pass


# DatabaseError is now imported from database_handler module


def log_and_raise(msg, exc=None, error_type=Exception):
    logging.error(msg)
    if exc:
        logging.error(str(exc))
    raise error_type(msg) if not exc else exc


# Data validation is now handled by FlightTicketTransformer class


def send_alert(message, level="ERROR"):
    """Send alert for failed runs (placeholder for actual implementation)"""
    logging.error(f"[ALERT {level}] {message}")
    # TODO: Implement actual alerting (email, Slack, etc.)
    # Example: send_slack_notification(message) or send_email_alert(message)


# Amadeus API config - load from environment variables
AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")
AMADEUS_TOKEN_URL = os.getenv(
    "AMADEUS_TOKEN_URL", "https://test.api.amadeus.com/v1/security/oauth2/token"
)
AMADEUS_FLIGHT_OFFERS_URL = os.getenv(
    "AMADEUS_FLIGHT_OFFERS_URL",
    "https://test.api.amadeus.com/v2/shopping/flight-offers",
)

# Default user ID for system operations
DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000000"  # TODO: Replace with a real system user UUID if needed


@dag(
    dag_id=DAG_ID,
    schedule=SCHEDULE_INTERVAL,
    start_date=START_DATE,
    catchup=CATCHUP,
    tags=["ticket", "amadeus", "ingestion"],
    default_args={"retries": 1, "retry_delay": timedelta(minutes=5)},
)
def ticket_data_ingestion():
    @task()
    def fetch_ticket_data():
        logging.info("[fetch_ticket_data] Starting task...")

        # Validate required environment variables
        if not AMADEUS_CLIENT_ID or not AMADEUS_CLIENT_SECRET:
            error_msg = "Missing required Amadeus API credentials. Please set AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET environment variables."
            send_alert(error_msg, "CRITICAL")
            log_and_raise(error_msg, error_type=AmadeusAPIError)

        try:
            # Get OAuth2 token
            logging.info("Requesting Amadeus OAuth2 token...")
            token_resp = requests.post(
                AMADEUS_TOKEN_URL,
                data={
                    "grant_type": "client_credentials",
                    "client_id": AMADEUS_CLIENT_ID,
                    "client_secret": AMADEUS_CLIENT_SECRET,
                },
                timeout=10,
            )
            logging.info(
                f"Token response: {token_resp.status_code} {token_resp.text[:200]}"
            )
            if token_resp.status_code != 200:
                error_msg = f"Failed to get Amadeus token: {token_resp.text}"
                send_alert(error_msg, "CRITICAL")
                log_and_raise(error_msg, error_type=AmadeusAPIError)
            access_token = token_resp.json().get("access_token")
            if not access_token:
                error_msg = "No access_token in Amadeus token response"
                send_alert(error_msg, "CRITICAL")
                log_and_raise(error_msg, error_type=AmadeusAPIError)
            # Call Amadeus Flight Offers Search API with sample params
            # Use a future date (3 months from now) to avoid "date in past" errors
            future_date = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")
            params = {
                "originLocationCode": "SYD",
                "destinationLocationCode": "BKK",
                "departureDate": future_date,
                "adults": 1,
                "max": 2,
            }
            offers_url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
            logging.info(
                f"Requesting Amadeus Flight Offers Search with params: {params}"
            )
            headers = {"Authorization": f"Bearer {access_token}"}
            resp = requests.get(offers_url, params=params, headers=headers, timeout=15)
            logging.info(
                f"Flight Offers Search response: {resp.status_code} {resp.text[:500]}"
            )
            if resp.status_code != 200:
                error_msg = f"Failed to fetch flight offers: {resp.text}"
                send_alert(error_msg, "ERROR")
                log_and_raise(error_msg, error_type=AmadeusAPIError)
            data = resp.json().get("data", [])
            logging.info(f"Fetched {len(data)} flight offers from Amadeus.")

            logging.info(f"Fetched {len(data)} flight offers from Amadeus.")
            return data
        except Exception as e:
            error_msg = f"Exception in fetch_ticket_data: {str(e)}"
            send_alert(error_msg, "ERROR")
            log_and_raise(error_msg, e)

    @task()
    def transform_ticket_data(raw_data):
        logging.info("[transform_ticket_data] Starting task...")

        try:
            if not raw_data:
                logging.warning("No raw data to transform.")
                return []

            # Initialize transformer
            transformer = FlightTicketTransformer(DEFAULT_USER_ID)

            # Transform all offers
            transformed_records = transformer.transform_amadeus_offers_batch(raw_data)

            # Get transformation statistics
            stats = transformer.get_transformation_stats(
                len(raw_data), len(transformed_records)
            )
            logging.info(f"Transformation stats: {stats}")

            return transformed_records

        except Exception as e:
            error_msg = f"Exception in transform_ticket_data: {str(e)}"
            send_alert(error_msg, "ERROR")
            log_and_raise(error_msg, e)

    @task()
    def load_to_postgres(transformed_data):
        logging.info("[load_to_postgres] Starting task...")

        # Initialize database handler
        db_handler = None
        try:
            if not transformed_data:
                logging.warning("No data to load to Postgres.")
                return

            # Initialize multi-database handler
            db_handler = MultiDatabaseHandler()

            # Bulk insert all records into all databases
            results = db_handler.bulk_insert_flight_tickets(transformed_data)

            # Log results for each database
            for db_name, count in results.items():
                logging.info(
                    f"Successfully loaded {count} records to {db_name} database."
                )

            total_inserted = sum(results.values())
            logging.info(
                f"Total records processed: {total_inserted} across {len(results)} databases."
            )

        except Exception as e:
            error_msg = f"Exception in load_to_postgres: {str(e)}"
            send_alert(error_msg, "ERROR")
            log_and_raise(error_msg, e)
        finally:
            # Clean up database handler
            if db_handler:
                db_handler.close()

    # DAG flow
    raw = fetch_ticket_data()
    transformed = transform_ticket_data(raw)
    load_to_postgres(transformed)


dag_inst = ticket_data_ingestion()
