from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PreferenceRequestDTO(BaseModel):
    """Request DTO for creating preferences."""
    user_id: UUID = Field(..., description="ID of the user")
    prefers_email: bool = Field(True, description="Whether user prefers email notifications")
    prefers_sms: bool = Field(False, description="Whether user prefers SMS notifications")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "prefers_email": True,
                "prefers_sms": False
            }
        }


class PreferenceUpdateDTO(BaseModel):
    """Request DTO for updating preferences (all fields optional except user constraints)."""
    prefers_email: Optional[bool] = Field(None, description="Whether user prefers email notifications")
    prefers_sms: Optional[bool] = Field(None, description="Whether user prefers SMS notifications")

    class Config:
        json_schema_extra = {
            "example": {
                "prefers_email": False,
                "prefers_sms": True
            }
        }


class PreferenceResponseDTO(BaseModel):
    """Response DTO for preference data."""
    id: int = Field(..., description="Preference ID")
    user_id: UUID = Field(..., description="ID of the user")
    prefers_email: bool = Field(..., description="Whether user prefers email notifications")
    prefers_sms: bool = Field(..., description="Whether user prefers SMS notifications")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "prefers_email": True,
                "prefers_sms": False
            }
        } 