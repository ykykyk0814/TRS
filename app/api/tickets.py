from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Depends

from app.service.ticket import TicketService
from app.dto.ticket import TicketRequestDTO, TicketUpdateDTO, TicketResponseDTO
from app.dto.common import SuccessResponseDTO
from app.api.dependencies import current_user, get_user_or_superuser
from app.core.models import User

router = APIRouter()
ticket_service = TicketService()


@router.get("/", response_model=List[TicketResponseDTO])
async def get_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user: User = Depends(current_user)
):
    """Get all tickets with pagination. Requires authentication."""
    tickets = await ticket_service.get_tickets(skip=skip, limit=limit)
    return [TicketResponseDTO.model_validate(ticket) for ticket in tickets]


@router.get("/{ticket_id}", response_model=TicketResponseDTO)
async def get_ticket(
    ticket_id: int, 
    user: User = Depends(current_user)
):
    """Get a specific ticket by ID. Requires authentication."""
    ticket = await ticket_service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Check authorization
    if ticket.user_id != user.id and not user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return TicketResponseDTO.model_validate(ticket)


@router.get("/user/{user_id}", response_model=List[TicketResponseDTO])
async def get_user_tickets(
    user_id: UUID, 
    user: User = Depends(get_user_or_superuser)
):
    """Get all tickets for a specific user. Requires authentication."""
    tickets = await ticket_service.get_user_tickets(user_id)
    return [TicketResponseDTO.model_validate(ticket) for ticket in tickets]


@router.get("/destination/{destination}", response_model=List[TicketResponseDTO])
async def get_tickets_by_destination(
    destination: str, 
    user: User = Depends(current_user)
):
    """Get tickets by destination. Requires authentication."""
    tickets = await ticket_service.get_tickets_by_destination(destination)
    return [TicketResponseDTO.model_validate(ticket) for ticket in tickets]


@router.post("/", response_model=TicketResponseDTO)
async def create_ticket(
    ticket_data: TicketRequestDTO, 
    user: User = Depends(current_user)
):
    """Create a new ticket. Requires authentication."""
    # Users can only create tickets for themselves unless they're superuser
    if ticket_data.user_id != user.id and not user.is_superuser:
        raise HTTPException(status_code=403, detail="Can only create tickets for yourself")
    
    ticket = await ticket_service.create_ticket(ticket_data.model_dump())
    return TicketResponseDTO.model_validate(ticket)


@router.put("/{ticket_id}", response_model=TicketResponseDTO)
async def update_ticket(
    ticket_id: int, 
    ticket_data: TicketUpdateDTO, 
    user: User = Depends(current_user)
):
    """Update a ticket. Requires authentication."""
    # Check if ticket exists and user has permission
    existing_ticket = await ticket_service.get_ticket(ticket_id)
    if not existing_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if existing_ticket.user_id != user.id and not user.is_superuser:
        raise HTTPException(status_code=403, detail="Can only update your own tickets")
    
    ticket = await ticket_service.update_ticket(ticket_id, ticket_data.model_dump(exclude_unset=True))
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return TicketResponseDTO.model_validate(ticket)


@router.delete("/{ticket_id}", response_model=SuccessResponseDTO)
async def delete_ticket(
    ticket_id: int, 
    user: User = Depends(current_user)
):
    """Delete a ticket. Requires authentication."""
    # Check if ticket exists and user has permission
    existing_ticket = await ticket_service.get_ticket(ticket_id)
    if not existing_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if existing_ticket.user_id != user.id and not user.is_superuser:
        raise HTTPException(status_code=403, detail="Can only delete your own tickets")
    
    success = await ticket_service.delete_ticket(ticket_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return SuccessResponseDTO(message="Ticket deleted successfully") 