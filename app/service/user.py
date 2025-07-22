from typing import List, Optional
from uuid import UUID

from app.core.models import User
from app.repository.user import UserRepository
from app.core.schemas import UserCreate, UserUpdate


class UserService:
    """Service layer for user business logic."""
    
    def __init__(self):
        self._repository = None

    @property
    def repository(self):
        """Lazy initialization of user repository."""
        if self._repository is None:
            self._repository = UserRepository()
        return self._repository

    async def get_user(self, user_id: UUID) -> Optional[User]:
        """Get a user by ID."""
        return await self.repository.get(user_id)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        return await self.repository.get_by_email(email)

    async def get_users(
        self, 
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = False
    ) -> List[User]:
        """Get users with optional filtering."""
        if active_only:
            return await self.repository.get_active_users(skip=skip, limit=limit)
        return await self.repository.get_multi(skip=skip, limit=limit)

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        return await self.repository.create(user_data)

    async def update_user(self, user_id: UUID, user_data: UserUpdate) -> Optional[User]:
        """Update an existing user."""
        return await self.repository.update(user_id, user_data)

    async def delete_user(self, user_id: UUID) -> bool:
        """Delete a user."""
        return await self.repository.delete(user_id)

    async def user_exists(self, user_id: UUID) -> bool:
        """Check if a user exists."""
        return await self.repository.exists(user_id)

    async def get_user_count(self) -> int:
        """Get total user count."""
        return await self.repository.count() 