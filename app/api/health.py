from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "message": "Travel Recommendation API is running"}


@router.get("/info")
async def api_info():
    """API information endpoint."""
    return {
        "message": "Travel Recommendation System API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
