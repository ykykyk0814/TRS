from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from app.core.models import Ticket
from app.repository.ticket import TicketRepository


class TicketService:
    """Service layer for ticket business logic."""
    
    def __init__(self):
        self._repository = None

    @property
    def repository(self):
        """Lazy initialization of ticket repository."""
        if self._repository is None:
            self._repository = TicketRepository()
        return self._repository

    async def get_ticket(self, ticket_id: int) -> Optional[Ticket]:
        """Get a ticket by ID."""
        return await self.repository.get(ticket_id)

    async def get_tickets(self, skip: int = 0, limit: int = 100) -> List[Ticket]:
        """Get tickets with pagination."""
        return await self.repository.get_multi(skip=skip, limit=limit)

    async def get_user_tickets(self, user_id: UUID) -> List[Ticket]:
        """Get all tickets for a specific user."""
        return await self.repository.get_by_user_id(user_id)

    async def get_tickets_by_destination(self, destination: str) -> List[Ticket]:
        """Get tickets by destination."""
        return await self.repository.get_by_destination(destination)

    async def get_tickets_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Ticket]:
        """Get tickets within a date range."""
        return await self.repository.get_by_date_range(start_date, end_date)

    async def create_ticket(self, ticket_data: Dict) -> Ticket:
        """Create a new ticket."""
        return await self.repository.create(ticket_data)

    async def update_ticket(self, ticket_id: int, ticket_data: Dict) -> Optional[Ticket]:
        """Update an existing ticket."""
        return await self.repository.update(ticket_id, ticket_data)

    async def delete_ticket(self, ticket_id: int) -> bool:
        """Delete a ticket."""
        return await self.repository.delete(ticket_id)

    async def get_ticket_count(self) -> int:
        """Get total ticket count."""
        return await self.repository.count() 