import logging
import os
from datetime import datetime, timedelta

import pendulum
import requests
import sqlalchemy
from airflow.decorators import dag, task
from sqlalchemy import create_engine

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


class DatabaseError(Exception):
    """Raised when database operations fail"""

    pass


def log_and_raise(msg, exc=None, error_type=Exception):
    logging.error(msg)
    if exc:
        logging.error(str(exc))
    raise error_type(msg) if not exc else exc


def validate_flight_data(offer):
    """Validate flight offer data quality"""
    required_fields = ["id", "itineraries", "price"]
    for field in required_fields:
        if field not in offer:
            raise DataValidationError(f"Missing required field: {field}")

    # Validate itineraries
    itineraries = offer.get("itineraries", [])
    if not itineraries:
        raise DataValidationError("No itineraries found in offer")

    # Validate segments
    for itinerary in itineraries:
        segments = itinerary.get("segments", [])
        if not segments:
            raise DataValidationError("No segments found in itinerary")

        for segment in segments:
            # Validate airport codes
            departure = segment.get("departure", {})
            arrival = segment.get("arrival", {})

            if not departure.get("iataCode") or not arrival.get("iataCode"):
                raise DataValidationError("Invalid airport codes in segment")

            # Validate timestamps
            if not departure.get("at") or not arrival.get("at"):
                raise DataValidationError("Missing departure/arrival times")

    # Validate price
    price = offer.get("price", {})
    if not price.get("total"):
        raise DataValidationError("Missing price information")

    return True


def send_alert(message, level="ERROR"):
    """Send alert for failed runs (placeholder for actual implementation)"""
    logging.error(f"[ALERT {level}] {message}")
    # TODO: Implement actual alerting (email, Slack, etc.)
    # Example: send_slack_notification(message) or send_email_alert(message)


# Amadeus API config
AMADEUS_CLIENT_ID = "fkJvYXyIa5OYqfK1ueh4HMaTdriW9g8z"
AMADEUS_CLIENT_SECRET = "MAmbtUdvrUQe00Zq"
AMADEUS_TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
AMADEUS_FLIGHT_OFFERS_URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"

# Postgres config - use Airflow's database for now
POSTGRES_CONN_STR = os.getenv(
    "AIRFLOW_DB_CONN",
    "postgresql+psycopg2://airflow:airflow@airflow-postgres:5432/airflow",
)
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

            # Validate each offer
            validated_data = []
            for offer in data:
                try:
                    validate_flight_data(offer)
                    validated_data.append(offer)
                except DataValidationError as e:
                    logging.warning(
                        f"Data validation failed for offer {offer.get('id', 'unknown')}: {e}"
                    )
                    send_alert(f"Data validation failed: {e}", "WARNING")
                    continue

            logging.info(f"Validated {len(validated_data)} out of {len(data)} offers.")
            return validated_data
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
            transformed = []
            for offer in raw_data:
                try:
                    # Map Amadeus offer to Ticket schema fields
                    itineraries = offer.get("itineraries", [])
                    if not itineraries:
                        continue
                    first_leg = (
                        itineraries[0]["segments"][0]
                        if itineraries[0]["segments"]
                        else None
                    )
                    last_leg = (
                        itineraries[-1]["segments"][-1]
                        if itineraries[-1]["segments"]
                        else None
                    )
                    if not first_leg or not last_leg:
                        continue
                    record = {
                        "user_id": DEFAULT_USER_ID,
                        "origin": first_leg["departure"]["iataCode"],
                        "destination": last_leg["arrival"]["iataCode"],
                        "departure_time": first_leg["departure"]["at"],
                        "arrival_time": last_leg["arrival"]["at"],
                        "seat_number": None,  # Amadeus does not provide seat info in offers
                        "notes": offer.get("id"),
                    }
                    transformed.append(record)
                except Exception as e:
                    logging.error(f"Error transforming offer: {offer}\n{e}")
            logging.info(f"Transformed {len(transformed)} offers.")
            return transformed
        except Exception as e:
            error_msg = f"Exception in transform_ticket_data: {str(e)}"
            send_alert(error_msg, "ERROR")
            log_and_raise(error_msg, e)

    @task()
    def load_to_postgres(transformed_data):
        logging.info("[load_to_postgres] Starting task...")
        try:
            if not transformed_data:
                logging.warning("No data to load to Postgres.")
                return
            engine = create_engine(POSTGRES_CONN_STR)
            with engine.begin() as conn:
                for record in transformed_data:
                    try:
                        # Create tickets table if it doesn't exist
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
                        conn.execute(sqlalchemy.text(create_table_query))

                        # Insert ticket data into the flight_tickets table
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
                        conn.execute(sqlalchemy.text(insert_query), record)
                        logging.info(f"Inserted/updated record: {record}")
                    except Exception as e:
                        error_msg = f"Error inserting record: {record}\n{e}"
                        logging.error(error_msg)
                        send_alert(error_msg, "ERROR")
                        raise DatabaseError(f"Database insertion failed: {e}")

            logging.info(
                f"Successfully loaded {len(transformed_data)} records to Postgres."
            )
        except Exception as e:
            error_msg = f"Exception in load_to_postgres: {str(e)}"
            send_alert(error_msg, "ERROR")
            log_and_raise(error_msg, e)

    # DAG flow
    raw = fetch_ticket_data()
    transformed = transform_ticket_data(raw)
    load_to_postgres(transformed)


dag_inst = ticket_data_ingestion()
