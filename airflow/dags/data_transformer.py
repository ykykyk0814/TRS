import logging
from typing import Any, Dict, List, Optional


class DataValidationError(Exception):
    """Raised when data validation fails"""

    pass


class FlightTicketTransformer:
    """Handles transformation of Amadeus API responses to internal ticket schema"""

    def __init__(self, default_user_id: str):
        """Initialize the transformer

        Args:
            default_user_id: Default user ID for system operations
        """
        self.default_user_id = default_user_id

    def validate_amadeus_offer(self, offer: Dict[str, Any]) -> bool:
        """Validate Amadeus flight offer data quality

        Args:
            offer: Amadeus flight offer dictionary

        Returns:
            bool: True if valid, False otherwise

        Raises:
            DataValidationError: If validation fails
        """
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

    def extract_flight_legs(
        self, offer: Dict[str, Any]
    ) -> tuple[Optional[Dict], Optional[Dict]]:
        """Extract first and last flight legs from Amadeus offer

        Args:
            offer: Amadeus flight offer dictionary

        Returns:
            tuple: (first_leg, last_leg) or (None, None) if extraction fails
        """
        itineraries = offer.get("itineraries", [])
        if not itineraries:
            return None, None

        # Extract first leg from first itinerary
        first_itinerary = itineraries[0]
        segments = first_itinerary.get("segments", [])
        if not segments:
            return None, None
        first_leg = segments[0]

        # Extract last leg from last itinerary
        last_itinerary = itineraries[-1]
        segments = last_itinerary.get("segments", [])
        if not segments:
            return None, None
        last_leg = segments[-1]

        return first_leg, last_leg

    def transform_amadeus_offer_to_ticket(
        self, offer: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Transform a single Amadeus offer to internal ticket schema

        Args:
            offer: Amadeus flight offer dictionary

        Returns:
            Dict: Transformed ticket record or None if transformation fails
        """
        try:
            # Validate the offer first
            self.validate_amadeus_offer(offer)

            # Extract flight legs
            first_leg, last_leg = self.extract_flight_legs(offer)
            if not first_leg or not last_leg:
                logging.warning(
                    f"Failed to extract flight legs from offer {offer.get('id', 'unknown')}"
                )
                return None

            # Transform to internal schema
            record = {
                "user_id": self.default_user_id,
                "origin": first_leg["departure"]["iataCode"],
                "destination": last_leg["arrival"]["iataCode"],
                "departure_time": first_leg["departure"]["at"],
                "arrival_time": last_leg["arrival"]["at"],
                "seat_number": None,  # Amadeus does not provide seat info in offers
                "notes": offer.get("id"),
            }

            logging.debug(
                f"Successfully transformed offer {offer.get('id')} to ticket record"
            )
            return record

        except DataValidationError as e:
            logging.warning(
                f"Data validation failed for offer {offer.get('id', 'unknown')}: {e}"
            )
            return None
        except Exception as e:
            logging.error(f"Error transforming offer {offer.get('id', 'unknown')}: {e}")
            return None

    def transform_amadeus_offers_batch(
        self, offers: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Transform a batch of Amadeus offers to internal ticket schema

        Args:
            offers: List of Amadeus flight offer dictionaries

        Returns:
            List[Dict]: List of transformed ticket records
        """
        if not offers:
            logging.warning("No offers to transform")
            return []

        transformed_records = []
        successful_transformations = 0

        for offer in offers:
            try:
                record = self.transform_amadeus_offer_to_ticket(offer)
                if record:
                    transformed_records.append(record)
                    successful_transformations += 1
            except Exception as e:
                logging.error(f"Error transforming offer: {offer}\n{e}")
                continue

        logging.info(
            f"Successfully transformed {successful_transformations} out of {len(offers)} offers"
        )
        return transformed_records

    def get_transformation_stats(
        self, original_count: int, transformed_count: int
    ) -> Dict[str, Any]:
        """Get transformation statistics

        Args:
            original_count: Number of original offers
            transformed_count: Number of successfully transformed records

        Returns:
            Dict: Statistics about the transformation process
        """
        failed_count = original_count - transformed_count
        success_rate = (
            (transformed_count / original_count * 100) if original_count > 0 else 0
        )

        return {
            "original_count": original_count,
            "transformed_count": transformed_count,
            "failed_count": failed_count,
            "success_rate": round(success_rate, 2),
        }
