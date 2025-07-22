from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select

from app.core.models import Ticket
from .base import BaseRepository


class TicketRepository(BaseRepository[Ticket, dict, dict]):
    """Repository for Ticket model operations."""
    
    def __init__(self):
        super().__init__(Ticket)

    async def get_by_user_id(self, user_id: UUID) -> List[Ticket]:
        """Get all tickets for a specific user."""
        async with self.db_manager.get_async_session() as session:
            query = select(Ticket).where(Ticket.user_id == user_id)
            result = await session.execute(query)
            return result.scalars().all()

    async def get_by_destination(self, destination: str) -> List[Ticket]:
        """Get all tickets to a specific destination."""
        async with self.db_manager.get_async_session() as session:
            query = select(Ticket).where(Ticket.destination == destination)
            result = await session.execute(query)
            return result.scalars().all()

    async def get_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Ticket]:
        """Get tickets within a date range."""
        async with self.db_manager.get_async_session() as session:
            query = select(Ticket).where(
                Ticket.departure_time >= start_date,
                Ticket.departure_time <= end_date
            )
            result = await session.execute(query)
            return result.scalars().all() 