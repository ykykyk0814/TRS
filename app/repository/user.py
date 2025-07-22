from typing import Optional
from uuid import UUID

from sqlalchemy import select

from app.core.models import User
from app.core.schemas import UserCreate, UserUpdate
from .base import BaseRepository


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """Repository for User model operations."""
    
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        async with self.db_manager.get_async_session() as session:
            query = select(User).where(User.email == email)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def get_active_users(self, skip: int = 0, limit: int = 100):
        """Get all active users."""
        return await self.get_multi(
            skip=skip, 
            limit=limit, 
            filters={"is_active": True}
        )

    async def get_verified_users(self, skip: int = 0, limit: int = 100):
        """Get all verified users."""
        return await self.get_multi(
            skip=skip, 
            limit=limit, 
            filters={"is_verified": True}
        ) 