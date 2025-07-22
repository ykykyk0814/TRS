from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import current_user, get_user_or_superuser
from app.core.models import User
from app.dto.common import SuccessResponseDTO
from app.dto.preference import (
    PreferenceRequestDTO,
    PreferenceResponseDTO,
    PreferenceUpdateDTO,
)
from app.service.preference import PreferenceService

router = APIRouter()
preference_service = PreferenceService()


@router.get("/{preference_id}", response_model=PreferenceResponseDTO)
async def get_preference(preference_id: int, user: User = Depends(current_user)):
    """Get a specific preference by ID. Requires authentication."""
    preference = await preference_service.get_preference(preference_id)
    if not preference:
        raise HTTPException(status_code=404, detail="Preference not found")

    # Users can only see their own preferences unless they're superuser
    if preference.user_id != user.id and not user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied")

    return PreferenceResponseDTO.model_validate(preference)


@router.get("/user/{user_id}", response_model=PreferenceResponseDTO)
async def get_user_preference(user_id: UUID, user: User = Depends(current_user)):
    """Get preference for a specific user. Requires authentication."""
    # Users can only see their own preferences unless they're superuser
    if user_id != user.id and not user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied")

    preference = await preference_service.get_user_preference(user_id)
    if not preference:
        raise HTTPException(status_code=404, detail="User preference not found")

    return PreferenceResponseDTO.model_validate(preference)


@router.post("/", response_model=PreferenceResponseDTO)
async def create_preference(
    preference_data: PreferenceRequestDTO, user: User = Depends(current_user)
):
    """Create a new preference. Requires authentication."""
    # Users can only create preferences for themselves unless they're superuser
    if preference_data.user_id != user.id and not user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Can only create preferences for yourself"
        )

    preference = await preference_service.create_preference(
        preference_data.model_dump()
    )
    return PreferenceResponseDTO.model_validate(preference)


@router.put("/{preference_id}", response_model=PreferenceResponseDTO)
async def update_preference(
    preference_id: int,
    preference_data: PreferenceUpdateDTO,
    user: User = Depends(current_user),
):
    """Update a preference. Requires authentication."""
    # Check if preference exists and user has permission
    existing_preference = await preference_service.get_preference(preference_id)
    if not existing_preference:
        raise HTTPException(status_code=404, detail="Preference not found")

    if existing_preference.user_id != user.id and not user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Can only update your own preferences"
        )

    preference = await preference_service.update_preference(
        preference_id, preference_data.model_dump(exclude_unset=True)
    )
    if not preference:
        raise HTTPException(status_code=404, detail="Preference not found")

    return PreferenceResponseDTO.model_validate(preference)


@router.put("/user/{user_id}", response_model=PreferenceResponseDTO)
async def create_or_update_user_preference(
    user_id: UUID,
    preference_data: PreferenceUpdateDTO,
    user: User = Depends(get_user_or_superuser),
):
    """Create or update preference for a user. Requires authentication."""
    preference = await preference_service.create_or_update_user_preference(
        user_id, preference_data.model_dump(exclude_unset=True)
    )
    return PreferenceResponseDTO.model_validate(preference)


@router.delete("/{preference_id}", response_model=SuccessResponseDTO)
async def delete_preference(preference_id: int, user: User = Depends(current_user)):
    """Delete a preference. Requires authentication."""
    # Check if preference exists and user has permission
    existing_preference = await preference_service.get_preference(preference_id)
    if not existing_preference:
        raise HTTPException(status_code=404, detail="Preference not found")

    if existing_preference.user_id != user.id and not user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Can only delete your own preferences"
        )

    success = await preference_service.delete_preference(preference_id)
    if not success:
        raise HTTPException(status_code=404, detail="Preference not found")

    return SuccessResponseDTO(message="Preference deleted successfully")
