"""
Tickets API endpoints with metrics tracking
"""
import logging
import time
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import current_user
from app.core.models import User
from app.dto.common import SuccessResponseDTO
from app.dto.ticket import TicketRequestDTO, TicketResponseDTO, TicketUpdateDTO
from app.monitoring.metrics import (
    business_metrics,
    database_metrics,
    track_database_operation,
)
from app.service.ticket import TicketService

logger = logging.getLogger(__name__)
router = APIRouter()
ticket_service = TicketService()


@router.get("/", response_model=List[TicketResponseDTO])
@track_database_operation("select", "tickets")
async def get_tickets_with_metrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user: User = Depends(current_user),
):
    """Get all tickets with pagination and metrics tracking"""
    start_time = time.time()

    try:
        tickets = await ticket_service.get_tickets(skip=skip, limit=limit)

        # Track successful query
        database_metrics["db_queries_total"].labels(
            operation="select", table="tickets", status="success"
        ).inc()

        return [TicketResponseDTO.model_validate(ticket) for ticket in tickets]

    except Exception as e:
        database_metrics["db_queries_total"].labels(
            operation="select", table="tickets", status="error"
        ).inc()
        raise HTTPException(
            status_code=500, detail=f"Error retrieving tickets: {str(e)}"
        )
    finally:
        duration = time.time() - start_time
        database_metrics["db_query_duration_seconds"].labels(
            operation="select", table="tickets"
        ).observe(duration)


@router.get("/{ticket_id}", response_model=TicketResponseDTO)
@track_database_operation("select", "tickets")
async def get_ticket_with_metrics(ticket_id: int, user: User = Depends(current_user)):
    """Get a specific ticket by ID with metrics tracking"""
    try:
        ticket = await ticket_service.get_ticket(ticket_id)

        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")

        database_metrics["db_queries_total"].labels(
            operation="select", table="tickets", status="success"
        ).inc()

        return TicketResponseDTO.model_validate(ticket)

    except HTTPException:
        raise
    except Exception as e:
        database_metrics["db_queries_total"].labels(
            operation="select", table="tickets", status="error"
        ).inc()
        raise HTTPException(
            status_code=500, detail=f"Error retrieving ticket: {str(e)}"
        )


@router.get("/destination/{destination}", response_model=List[TicketResponseDTO])
@track_database_operation("select", "tickets")
async def get_tickets_by_destination_with_metrics(
    destination: str, user: User = Depends(current_user)
):
    """Get tickets by destination with metrics tracking"""
    try:
        tickets = await ticket_service.get_tickets_by_destination(destination)

        # Track search by destination
        business_metrics["travel_searches_total"].labels(
            search_type="destination", destination=destination
        ).inc()

        database_metrics["db_queries_total"].labels(
            operation="select", table="tickets", status="success"
        ).inc()

        return [TicketResponseDTO.model_validate(ticket) for ticket in tickets]

    except Exception as e:
        database_metrics["db_queries_total"].labels(
            operation="select", table="tickets", status="error"
        ).inc()
        raise HTTPException(
            status_code=500, detail=f"Error retrieving tickets: {str(e)}"
        )


@router.post("/", response_model=TicketResponseDTO)
@track_database_operation("insert", "tickets")
async def create_ticket_with_metrics(
    ticket_data: TicketRequestDTO, user: User = Depends(current_user)
):
    """Create a new ticket with metrics tracking"""
    start_time = time.time()

    try:
        ticket = await ticket_service.create_ticket(ticket_data, user.id)

        # Track ticket booking
        business_metrics["ticket_bookings_total"].labels(
            origin=ticket_data.origin, destination=ticket_data.destination
        ).inc()

        database_metrics["db_queries_total"].labels(
            operation="insert", table="tickets", status="success"
        ).inc()

        return TicketResponseDTO.model_validate(ticket)

    except Exception as e:
        database_metrics["db_queries_total"].labels(
            operation="insert", table="tickets", status="error"
        ).inc()
        raise HTTPException(status_code=500, detail=f"Error creating ticket: {str(e)}")
    finally:
        duration = time.time() - start_time
        database_metrics["db_query_duration_seconds"].labels(
            operation="insert", table="tickets"
        ).observe(duration)


@router.put("/{ticket_id}", response_model=TicketResponseDTO)
@track_database_operation("update", "tickets")
async def update_ticket_with_metrics(
    ticket_id: int, ticket_data: TicketUpdateDTO, user: User = Depends(current_user)
):
    """Update a ticket with metrics tracking"""
    try:
        ticket = await ticket_service.update_ticket(ticket_id, ticket_data, user.id)

        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")

        database_metrics["db_queries_total"].labels(
            operation="update", table="tickets", status="success"
        ).inc()

        return TicketResponseDTO.model_validate(ticket)

    except HTTPException:
        raise
    except Exception as e:
        database_metrics["db_queries_total"].labels(
            operation="update", table="tickets", status="error"
        ).inc()
        raise HTTPException(status_code=500, detail=f"Error updating ticket: {str(e)}")


@router.delete("/{ticket_id}", response_model=SuccessResponseDTO)
@track_database_operation("delete", "tickets")
async def delete_ticket_with_metrics(
    ticket_id: int, user: User = Depends(current_user)
):
    """Delete a ticket with metrics tracking"""
    try:
        success = await ticket_service.delete_ticket(ticket_id, user.id)

        if not success:
            raise HTTPException(status_code=404, detail="Ticket not found")

        database_metrics["db_queries_total"].labels(
            operation="delete", table="tickets", status="success"
        ).inc()

        return SuccessResponseDTO(message="Ticket deleted successfully")

    except HTTPException:
        raise
    except Exception as e:
        database_metrics["db_queries_total"].labels(
            operation="delete", table="tickets", status="error"
        ).inc()
        raise HTTPException(status_code=500, detail=f"Error deleting ticket: {str(e)}")


@router.get("/metrics/summary")
async def get_tickets_metrics_summary():
    """Get tickets metrics summary"""
    try:
        return {
            "message": "Tickets metrics are available at /metrics endpoint",
            "tracked_operations": [
                "get_tickets",
                "get_ticket",
                "get_tickets_by_destination",
                "create_ticket",
                "update_ticket",
                "delete_ticket",
            ],
            "business_metrics": ["travel_searches_total", "ticket_bookings_total"],
            "database_metrics": ["db_queries_total", "db_query_duration_seconds"],
        }
    except Exception as e:
        logger.error(f"Error getting tickets metrics summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics summary")
