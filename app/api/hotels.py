from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.dependencies import current_user
from app.core.models import User

router = APIRouter(prefix="/hotels", tags=["hotels"])


# Hotel-related DTOs to match template expectations
class HotelSearchRequest(BaseModel):
    """Hotel search request matching typical hotel booking interfaces"""

    destination: str = Field(..., description="Destination city/location")
    check_in: date = Field(..., description="Check-in date")
    check_out: date = Field(..., description="Check-out date")
    guests: int = Field(1, ge=1, le=10, description="Number of guests")
    rooms: int = Field(1, ge=1, le=5, description="Number of rooms")
    price_min: Optional[float] = Field(
        None, ge=0, description="Minimum price per night"
    )
    price_max: Optional[float] = Field(
        None, ge=0, description="Maximum price per night"
    )
    amenities: Optional[List[str]] = Field(None, description="Preferred amenities")


class HotelResponse(BaseModel):
    """Hotel response matching template expectations"""

    id: str = Field(..., description="Hotel ID")
    name: str = Field(..., description="Hotel name")
    description: str = Field(..., description="Hotel description")
    location: str = Field(..., description="Hotel location")
    price_per_night: float = Field(..., description="Price per night")
    rating: float = Field(ge=0, le=5, description="Hotel rating")
    image_url: str = Field(..., description="Hotel main image URL")
    amenities: List[str] = Field(default_factory=list, description="Hotel amenities")
    available_rooms: int = Field(..., description="Available rooms")


class BookingRequest(BaseModel):
    """Hotel booking request"""

    hotel_id: str = Field(..., description="Hotel ID")
    check_in: date = Field(..., description="Check-in date")
    check_out: date = Field(..., description="Check-out date")
    guests: int = Field(..., ge=1, description="Number of guests")
    rooms: int = Field(..., ge=1, description="Number of rooms")
    special_requests: Optional[str] = Field(None, description="Special requests")


class BookingResponse(BaseModel):
    """Hotel booking response"""

    booking_id: str = Field(..., description="Booking confirmation ID")
    hotel_name: str = Field(..., description="Hotel name")
    check_in: date = Field(..., description="Check-in date")
    check_out: date = Field(..., description="Check-out date")
    total_price: float = Field(..., description="Total booking price")
    status: str = Field(..., description="Booking status")
    created_at: datetime = Field(..., description="Booking creation time")


@router.post("/search", response_model=List[HotelResponse])
async def search_hotels(
    search_request: HotelSearchRequest, user: User = Depends(current_user)
):
    """
    Search for hotels based on criteria
    For now, this returns mock data that matches the template expectations
    """
    # Mock hotel data - replace with actual hotel search logic
    mock_hotels = [
        HotelResponse(
            id="hotel_1",
            name="Grand Plaza Hotel",
            description="Luxury hotel in the heart of the city with modern amenities and exceptional service.",
            location=search_request.destination,
            price_per_night=150.00,
            rating=4.5,
            image_url="https://via.placeholder.com/400x300/0066cc/ffffff?text=Grand+Plaza",
            amenities=["WiFi", "Pool", "Gym", "Restaurant", "Spa"],
            available_rooms=5,
        ),
        HotelResponse(
            id="hotel_2",
            name="Comfort Inn & Suites",
            description="Comfortable and affordable accommodation perfect for business and leisure travelers.",
            location=search_request.destination,
            price_per_night=89.00,
            rating=4.0,
            image_url="https://via.placeholder.com/400x300/009900/ffffff?text=Comfort+Inn",
            amenities=["WiFi", "Breakfast", "Parking", "Business Center"],
            available_rooms=8,
        ),
        HotelResponse(
            id="hotel_3",
            name="Boutique City Hotel",
            description="Unique boutique hotel with personalized service and stylish accommodations.",
            location=search_request.destination,
            price_per_night=200.00,
            rating=4.8,
            image_url="https://via.placeholder.com/400x300/cc6600/ffffff?text=Boutique+Hotel",
            amenities=["WiFi", "Concierge", "Restaurant", "Bar", "Room Service"],
            available_rooms=3,
        ),
    ]

    # Filter by price range if specified
    if search_request.price_min is not None:
        mock_hotels = [
            h for h in mock_hotels if h.price_per_night >= search_request.price_min
        ]
    if search_request.price_max is not None:
        mock_hotels = [
            h for h in mock_hotels if h.price_per_night <= search_request.price_max
        ]

    return mock_hotels


@router.get("/{hotel_id}", response_model=HotelResponse)
async def get_hotel_details(hotel_id: str, user: User = Depends(current_user)):
    """Get detailed information about a specific hotel"""
    # Mock hotel detail - replace with actual hotel lookup
    if hotel_id == "hotel_1":
        return HotelResponse(
            id="hotel_1",
            name="Grand Plaza Hotel",
            description="Luxury hotel in the heart of the city with modern amenities and exceptional service. Features include 24/7 concierge, valet parking, and award-winning dining.",
            location="Downtown City Center",
            price_per_night=150.00,
            rating=4.5,
            image_url="https://via.placeholder.com/400x300/0066cc/ffffff?text=Grand+Plaza",
            amenities=[
                "WiFi",
                "Pool",
                "Gym",
                "Restaurant",
                "Spa",
                "Valet Parking",
                "Concierge",
            ],
            available_rooms=5,
        )
    else:
        raise HTTPException(status_code=404, detail="Hotel not found")


@router.post("/book", response_model=BookingResponse)
async def book_hotel(
    booking_request: BookingRequest, user: User = Depends(current_user)
):
    """Book a hotel room"""
    # Mock booking - replace with actual booking logic
    import uuid

    booking_id = str(uuid.uuid4())
    nights = (booking_request.check_out - booking_request.check_in).days
    price_per_night = 150.00  # This should come from hotel data
    total_price = price_per_night * nights * booking_request.rooms

    return BookingResponse(
        booking_id=booking_id,
        hotel_name="Grand Plaza Hotel",  # This should come from hotel data
        check_in=booking_request.check_in,
        check_out=booking_request.check_out,
        total_price=total_price,
        status="confirmed",
        created_at=datetime.now(),
    )


@router.get("/bookings/user", response_model=List[BookingResponse])
async def get_user_bookings(user: User = Depends(current_user)):
    """Get all bookings for the current user"""
    # Mock user bookings - replace with actual database query
    return [
        BookingResponse(
            booking_id="booking_123",
            hotel_name="Grand Plaza Hotel",
            check_in=date(2024, 2, 15),
            check_out=date(2024, 2, 18),
            total_price=450.00,
            status="confirmed",
            created_at=datetime(2024, 1, 15, 10, 30, 0),
        )
    ]
