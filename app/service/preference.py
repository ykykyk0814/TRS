from typing import Dict, Optional
from uuid import UUID

from app.core.models import Preference
from app.repository.preference import PreferenceRepository


class PreferenceService:
    """Service layer for preference business logic."""
    
    def __init__(self):
        self._repository = None

    @property
    def repository(self):
        """Lazy initialization of preference repository."""
        if self._repository is None:
            self._repository = PreferenceRepository()
        return self._repository

    async def get_preference(self, preference_id: int) -> Optional[Preference]:
        """Get a preference by ID."""
        return await self.repository.get(preference_id)

    async def get_user_preference(self, user_id: UUID) -> Optional[Preference]:
        """Get preference for a specific user."""
        return await self.repository.get_by_user_id(user_id)

    async def create_preference(self, preference_data: Dict) -> Preference:
        """Create a new preference."""
        return await self.repository.create(preference_data)

    async def update_preference(self, preference_id: int, preference_data: Dict) -> Optional[Preference]:
        """Update an existing preference."""
        return await self.repository.update(preference_id, preference_data)

    async def delete_preference(self, preference_id: int) -> bool:
        """Delete a preference."""
        return await self.repository.delete(preference_id)

    async def create_or_update_user_preference(
        self, 
        user_id: UUID, 
        preference_data: Dict
    ) -> Preference:
        """Create or update preference for a user."""
        existing = await self.get_user_preference(user_id)
        if existing:
            return await self.update_preference(existing.id, preference_data)
        else:
            preference_data["user_id"] = user_id
            return await self.create_preference(preference_data) 