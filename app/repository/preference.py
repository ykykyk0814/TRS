from typing import Optional
from uuid import UUID

from sqlalchemy import select

from app.core.models import Preference
from .base import BaseRepository


class PreferenceRepository(BaseRepository[Preference, dict, dict]):
    """Repository for Preference model operations."""
    
    def __init__(self):
        super().__init__(Preference)

    async def get_by_user_id(self, user_id: UUID) -> Optional[Preference]:
        """Get preference for a specific user."""
        async with self.db_manager.get_async_session() as session:
            query = select(Preference).where(Preference.user_id == user_id)
            result = await session.execute(query)
            return result.scalar_one_or_none() 