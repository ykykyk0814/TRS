"""
Prometheus middleware for FastAPI
"""
import logging
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .metrics import api_metrics

logger = logging.getLogger(__name__)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to track HTTP requests and responses"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip metrics endpoint to avoid recursion
        if request.url.path == "/metrics":
            return await call_next(request)

        # Track active connections
        api_metrics["http_active_connections"].inc()

        # Get request info
        method = request.method
        endpoint = self._get_endpoint_name(request.url.path)

        # Track request size
        request_size = 0
        if hasattr(request, "_body"):
            request_size = len(request._body)

        start_time = time.time()

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Track metrics
            api_metrics["http_requests_total"].labels(
                method=method, endpoint=endpoint, status_code=str(response.status_code)
            ).inc()

            api_metrics["http_request_duration_seconds"].labels(
                method=method, endpoint=endpoint
            ).observe(duration)

            api_metrics["http_request_size_bytes"].labels(
                method=method, endpoint=endpoint
            ).observe(request_size)

            # Track response size if available
            if hasattr(response, "body"):
                response_size = len(response.body)
                api_metrics["http_response_size_bytes"].labels(
                    method=method, endpoint=endpoint
                ).observe(response_size)

            # Track errors
            if response.status_code >= 400:
                error_type = self._get_error_type(response.status_code)
                api_metrics["http_errors_total"].labels(
                    method=method, endpoint=endpoint, error_type=error_type
                ).inc()

            return response

        except Exception:
            # Track errors
            duration = time.time() - start_time

            api_metrics["http_requests_total"].labels(
                method=method, endpoint=endpoint, status_code="500"
            ).inc()

            api_metrics["http_errors_total"].labels(
                method=method, endpoint=endpoint, error_type="internal_error"
            ).inc()

            api_metrics["http_request_duration_seconds"].labels(
                method=method, endpoint=endpoint
            ).observe(duration)

            raise

        finally:
            # Decrement active connections
            api_metrics["http_active_connections"].dec()

    def _get_endpoint_name(self, path: str) -> str:
        """Extract endpoint name from path"""
        # Remove query parameters
        path = path.split("?")[0]

        # Replace path parameters with placeholders
        if "/api/auth/users/" in path and path.count("/") > 4:
            return "/api/auth/users/{user_id}"
        elif "/api/tickets/" in path and path.count("/") > 3:
            return "/api/tickets/{ticket_id}"
        elif "/api/preferences/" in path and path.count("/") > 3:
            return "/api/preferences/{preference_id}"
        elif "/api/vector/" in path:
            # Extract vector endpoint
            parts = path.split("/")
            if len(parts) >= 4:
                return f"/api/vector/{parts[3]}"

        return path

    def _get_error_type(self, status_code: int) -> str:
        """Get error type from status code"""
        if 400 <= status_code < 500:
            return "client_error"
        elif 500 <= status_code < 600:
            return "server_error"
        else:
            return "unknown_error"
