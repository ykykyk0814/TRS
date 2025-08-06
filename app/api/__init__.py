# API layer with routers
from fastapi import APIRouter

from . import auth, health, preferences, tickets, vector

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(health.router, prefix="", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
api_router.include_router(
    preferences.router, prefix="/preferences", tags=["preferences"]
)
api_router.include_router(vector.router, prefix="/vector", tags=["vector"])
