from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TicketRequestDTO(BaseModel):
    """Request DTO for creating/updating tickets."""

    user_id: UUID = Field(..., description="ID of the user who owns the ticket")
    origin: str = Field(
        ..., min_length=1, max_length=100, description="Origin location"
    )
    destination: str = Field(
        ..., min_length=1, max_length=100, description="Destination location"
    )
    departure_time: datetime = Field(..., description="Departure date and time")
    arrival_time: datetime = Field(..., description="Arrival date and time")
    seat_number: Optional[str] = Field(None, max_length=10, description="Seat number")
    notes: Optional[str] = Field(None, description="Additional notes")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "origin": "New York",
                "destination": "Los Angeles",
                "departure_time": "2024-01-15T10:30:00",
                "arrival_time": "2024-01-15T13:45:00",
                "seat_number": "12A",
                "notes": "Window seat requested",
            }
        }


class TicketUpdateDTO(BaseModel):
    """Request DTO for updating tickets (all fields optional)."""

    origin: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Origin location"
    )
    destination: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Destination location"
    )
    departure_time: Optional[datetime] = Field(
        None, description="Departure date and time"
    )
    arrival_time: Optional[datetime] = Field(None, description="Arrival date and time")
    seat_number: Optional[str] = Field(None, max_length=10, description="Seat number")
    notes: Optional[str] = Field(None, description="Additional notes")

    class Config:
        json_schema_extra = {
            "example": {"seat_number": "15B", "notes": "Changed to aisle seat"}
        }


class TicketResponseDTO(BaseModel):
    """Response DTO for ticket data."""

    id: int = Field(..., description="Ticket ID")
    user_id: UUID = Field(..., description="ID of the user who owns the ticket")
    origin: str = Field(..., description="Origin location")
    destination: str = Field(..., description="Destination location")
    departure_time: datetime = Field(..., description="Departure date and time")
    arrival_time: datetime = Field(..., description="Arrival date and time")
    seat_number: Optional[str] = Field(None, description="Seat number")
    notes: Optional[str] = Field(None, description="Additional notes")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "origin": "New York",
                "destination": "Los Angeles",
                "departure_time": "2024-01-15T10:30:00",
                "arrival_time": "2024-01-15T13:45:00",
                "seat_number": "12A",
                "notes": "Window seat requested",
            }
        }
