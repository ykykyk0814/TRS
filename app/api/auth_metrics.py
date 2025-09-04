"""
Custom auth endpoints with metrics tracking
"""
import logging

from fastapi import APIRouter, HTTPException

from app.core.schemas import UserCreate
from app.monitoring.metrics import business_metrics

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register-with-metrics")
async def register_with_metrics(user_data: UserCreate):
    """Register user with metrics tracking"""
    try:
        # This would normally call the actual registration logic
        # For now, we'll just track the metric
        business_metrics["user_registrations_total"].inc()
        logger.info(f"User registration tracked: {user_data.email}")

        return {"message": "Registration tracked", "email": user_data.email}
    except Exception as e:
        logger.error(f"Error tracking registration: {e}")
        raise HTTPException(status_code=500, detail="Registration tracking failed")


@router.post("/login-with-metrics")
async def login_with_metrics(login_data: dict):
    """Login with metrics tracking"""
    try:
        # Track login attempt
        login_method = login_data.get("method", "jwt")
        business_metrics["user_logins_total"].labels(login_method=login_method).inc()
        logger.info(f"User login tracked: {login_method}")

        return {"message": "Login tracked", "method": login_method}
    except Exception as e:
        logger.error(f"Error tracking login: {e}")
        raise HTTPException(status_code=500, detail="Login tracking failed")


@router.get("/metrics/summary")
async def get_auth_metrics_summary():
    """Get authentication metrics summary"""
    try:
        # This would normally query the actual metrics
        # For now, return a placeholder
        return {
            "registrations_total": "N/A - Use /metrics endpoint",
            "logins_total": "N/A - Use /metrics endpoint",
            "message": "Use /metrics endpoint for detailed metrics",
        }
    except Exception as e:
        logger.error(f"Error getting auth metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get auth metrics")
