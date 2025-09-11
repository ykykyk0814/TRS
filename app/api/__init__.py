# API layer with routers
from fastapi import APIRouter

from . import (
    auth,
    auth_metrics,
    health,
    hotels,
    preferences,
    tickets,
    tickets_with_metrics,
    vector,
    vector_with_metrics,
)

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(health.router, prefix="", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(auth_metrics.router, prefix="/auth", tags=["auth-metrics"])
api_router.include_router(hotels.router, prefix="/hotels", tags=["hotels"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
api_router.include_router(
    tickets_with_metrics.router, prefix="/tickets-metrics", tags=["tickets-metrics"]
)
api_router.include_router(
    preferences.router, prefix="/preferences", tags=["preferences"]
)
api_router.include_router(vector.router, prefix="/vector", tags=["vector"])
api_router.include_router(
    vector_with_metrics.router, prefix="/vector-metrics", tags=["vector-metrics"]
)
