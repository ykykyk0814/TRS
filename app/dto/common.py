from pydantic import BaseModel, Field


class SuccessResponseDTO(BaseModel):
    """Standard success response DTO."""

    message: str = Field(..., description="Success message")

    class Config:
        json_schema_extra = {"example": {"message": "Operation completed successfully"}}


class PaginationQueryDTO(BaseModel):
    """Standard pagination query parameters."""

    skip: int = Field(0, ge=0, description="Number of items to skip")
    limit: int = Field(
        100, ge=1, le=1000, description="Maximum number of items to return"
    )

    class Config:
        json_schema_extra = {"example": {"skip": 0, "limit": 100}}
