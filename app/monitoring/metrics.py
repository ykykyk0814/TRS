"""
Prometheus metrics for the Travel Recommendation System
"""
import logging
import time
from functools import wraps

from fastapi.responses import Response as FastAPIResponse
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

logger = logging.getLogger(__name__)

# Create a custom registry for our metrics
REGISTRY = CollectorRegistry()

# API Performance Metrics
api_metrics = {
    # Request counters by endpoint and method
    "http_requests_total": Counter(
        "http_requests_total",
        "Total number of HTTP requests",
        ["method", "endpoint", "status_code"],
        registry=REGISTRY,
    ),
    # Request duration histogram
    "http_request_duration_seconds": Histogram(
        "http_request_duration_seconds",
        "HTTP request duration in seconds",
        ["method", "endpoint"],
        buckets=[
            0.01,
            0.025,
            0.05,
            0.075,
            0.1,
            0.25,
            0.5,
            0.75,
            1.0,
            2.5,
            5.0,
            7.5,
            10.0,
        ],
        registry=REGISTRY,
    ),
    # Request size histogram
    "http_request_size_bytes": Histogram(
        "http_request_size_bytes",
        "HTTP request size in bytes",
        ["method", "endpoint"],
        buckets=[100, 1000, 10000, 100000, 1000000],
        registry=REGISTRY,
    ),
    # Response size histogram
    "http_response_size_bytes": Histogram(
        "http_response_size_bytes",
        "HTTP response size in bytes",
        ["method", "endpoint"],
        buckets=[100, 1000, 10000, 100000, 1000000],
        registry=REGISTRY,
    ),
    # Active connections gauge
    "http_active_connections": Gauge(
        "http_active_connections",
        "Number of active HTTP connections",
        registry=REGISTRY,
    ),
    # Error rate counter
    "http_errors_total": Counter(
        "http_errors_total",
        "Total number of HTTP errors",
        ["method", "endpoint", "error_type"],
        registry=REGISTRY,
    ),
}

# Business Metrics
business_metrics = {
    # User registration counter
    "user_registrations_total": Counter(
        "user_registrations_total",
        "Total number of user registrations",
        registry=REGISTRY,
    ),
    # User login counter
    "user_logins_total": Counter(
        "user_logins_total",
        "Total number of user logins",
        ["login_method"],
        registry=REGISTRY,
    ),
    # Travel searches counter
    "travel_searches_total": Counter(
        "travel_searches_total",
        "Total number of travel searches",
        ["search_type", "destination"],
        registry=REGISTRY,
    ),
    # Ticket bookings counter
    "ticket_bookings_total": Counter(
        "ticket_bookings_total",
        "Total number of ticket bookings",
        ["origin", "destination"],
        registry=REGISTRY,
    ),
    # Preferences created counter
    "preferences_created_total": Counter(
        "preferences_created_total",
        "Total number of preferences created",
        ["preference_type"],
        registry=REGISTRY,
    ),
    # Vector searches counter
    "vector_searches_total": Counter(
        "vector_searches_total",
        "Total number of vector searches",
        ["collection_name"],
        registry=REGISTRY,
    ),
    # Vector content added counter
    "vector_content_added_total": Counter(
        "vector_content_added_total",
        "Total number of vector content items added",
        ["collection_name"],
        registry=REGISTRY,
    ),
    # Active users gauge
    "active_users": Gauge(
        "active_users",
        "Number of active users",
        registry=REGISTRY,
    ),
    # Search latency histogram
    "search_duration_seconds": Histogram(
        "search_duration_seconds",
        "Search operation duration in seconds",
        ["search_type"],
        buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
        registry=REGISTRY,
    ),
}

# Database Metrics
database_metrics = {
    # Database connection pool size
    "db_connections_active": Gauge(
        "db_connections_active",
        "Number of active database connections",
        registry=REGISTRY,
    ),
    # Database query duration
    "db_query_duration_seconds": Histogram(
        "db_query_duration_seconds",
        "Database query duration in seconds",
        ["operation", "table"],
        buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
        registry=REGISTRY,
    ),
    # Database query counter
    "db_queries_total": Counter(
        "db_queries_total",
        "Total number of database queries",
        ["operation", "table", "status"],
        registry=REGISTRY,
    ),
    # Database transaction counter
    "db_transactions_total": Counter(
        "db_transactions_total",
        "Total number of database transactions",
        ["status"],
        registry=REGISTRY,
    ),
}

# Vector Database Metrics
vector_metrics = {
    # Vector database operations
    "vector_operations_total": Counter(
        "vector_operations_total",
        "Total number of vector database operations",
        ["operation", "collection", "status"],
        registry=REGISTRY,
    ),
    # Vector operation duration
    "vector_operation_duration_seconds": Histogram(
        "vector_operation_duration_seconds",
        "Vector operation duration in seconds",
        ["operation", "collection"],
        buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
        registry=REGISTRY,
    ),
    # Vector collection size
    "vector_collection_size": Gauge(
        "vector_collection_size",
        "Number of vectors in collection",
        ["collection_name"],
        registry=REGISTRY,
    ),
    # Vector search latency
    "vector_search_duration_seconds": Histogram(
        "vector_search_duration_seconds",
        "Vector search duration in seconds",
        ["collection_name"],
        buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
        registry=REGISTRY,
    ),
}

# System Metrics
system_metrics = {
    # Application uptime
    "app_uptime_seconds": Gauge(
        "app_uptime_seconds",
        "Application uptime in seconds",
        registry=REGISTRY,
    ),
    # Memory usage
    "app_memory_usage_bytes": Gauge(
        "app_memory_usage_bytes",
        "Application memory usage in bytes",
        registry=REGISTRY,
    ),
    # CPU usage
    "app_cpu_usage_percent": Gauge(
        "app_cpu_usage_percent",
        "Application CPU usage percentage",
        registry=REGISTRY,
    ),
}


def setup_metrics():
    """Initialize and setup all metrics"""
    logger.info("Setting up Prometheus metrics")
    return REGISTRY


def get_metrics_response() -> FastAPIResponse:
    """Generate Prometheus metrics response"""
    try:
        data = generate_latest(REGISTRY)
        return FastAPIResponse(content=data, media_type=CONTENT_TYPE_LATEST)
    except Exception as e:
        logger.error(f"Error generating metrics: {e}")
        return FastAPIResponse(content="", status_code=500)


def track_request_duration(func):
    """Decorator to track request duration"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            # Extract endpoint from function name or path
            endpoint = getattr(func, "__name__", "unknown")
            api_metrics["http_request_duration_seconds"].labels(
                method="GET", endpoint=endpoint
            ).observe(duration)

    return wrapper


def track_database_operation(operation: str, table: str):
    """Decorator to track database operations"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                database_metrics["db_queries_total"].labels(
                    operation=operation, table=table, status="success"
                ).inc()
                return result
            except Exception as e:
                database_metrics["db_queries_total"].labels(
                    operation=operation, table=table, status="error"
                ).inc()
                raise e
            finally:
                duration = time.time() - start_time
                database_metrics["db_query_duration_seconds"].labels(
                    operation=operation, table=table
                ).observe(duration)

        return wrapper

    return decorator


def track_vector_operation(operation: str, collection: str):
    """Decorator to track vector operations"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                vector_metrics["vector_operations_total"].labels(
                    operation=operation, collection=collection, status="success"
                ).inc()
                return result
            except Exception as e:
                vector_metrics["vector_operations_total"].labels(
                    operation=operation, collection=collection, status="error"
                ).inc()
                raise e
            finally:
                duration = time.time() - start_time
                vector_metrics["vector_operation_duration_seconds"].labels(
                    operation=operation, collection=collection
                ).observe(duration)

        return wrapper

    return decorator


# Initialize metrics
setup_metrics()
