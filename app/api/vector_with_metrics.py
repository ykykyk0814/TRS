"""
Vector API endpoints with enhanced metrics tracking
"""
import logging
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.monitoring.metrics import (
    business_metrics,
    track_vector_operation,
    vector_metrics,
)
from app.service.vector_service import VectorService, get_vector_service

logger = logging.getLogger(__name__)
router = APIRouter()


class TravelContentRequest(BaseModel):
    content_id: str
    title: str
    description: str
    content_type: str
    metadata: Optional[Dict[str, Any]] = None


class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    score_threshold: float = 0.7


class SearchResult(BaseModel):
    content_id: str
    title: str
    description: str
    content_type: str
    score: float
    metadata: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_found: int
    query: str
    collection_name: str


@router.get("/collections/{collection_name}")
@track_vector_operation("get_collection_info", "travel_content")
async def get_collection_info_with_metrics(
    collection_name: str, vector_service: VectorService = Depends(get_vector_service)
):
    """Get collection information with metrics tracking"""
    try:
        info = vector_service.get_collection_info(collection_name)

        # Track collection access
        vector_metrics["vector_operations_total"].labels(
            operation="get_collection_info",
            collection=collection_name,
            status="success",
        ).inc()

        return info
    except Exception as e:
        vector_metrics["vector_operations_total"].labels(
            operation="get_collection_info", collection=collection_name, status="error"
        ).inc()
        raise HTTPException(
            status_code=500, detail=f"Error getting collection info: {str(e)}"
        )


@router.post("/content")
@track_vector_operation("add_content", "travel_content")
async def add_travel_content_with_metrics(
    request: TravelContentRequest,
    collection_name: str = "travel_content",
    vector_service: VectorService = Depends(get_vector_service),
):
    """Add travel content with metrics tracking"""
    start_time = time.time()

    try:
        success = vector_service.add_travel_content(
            collection_name=collection_name,
            content_id=request.content_id,
            title=request.title,
            description=request.description,
            content_type=request.content_type,
            metadata=request.metadata,
        )

        if success:
            # Track successful content addition
            business_metrics["vector_content_added_total"].labels(
                collection_name=collection_name
            ).inc()

            vector_metrics["vector_operations_total"].labels(
                operation="add_content", collection=collection_name, status="success"
            ).inc()

            # Update collection size metric
            try:
                info = vector_service.get_collection_info(collection_name)
                if "points_count" in info:
                    vector_metrics["vector_collection_size"].labels(
                        collection_name=collection_name
                    ).set(info["points_count"])
            except Exception:
                pass  # Don't fail if we can't update the size metric

            return {
                "message": f"Travel content '{request.content_id}' added successfully",
                "content_id": request.content_id,
                "collection_name": collection_name,
            }
        else:
            vector_metrics["vector_operations_total"].labels(
                operation="add_content", collection=collection_name, status="error"
            ).inc()
            raise HTTPException(status_code=500, detail="Failed to add travel content")

    except Exception as e:
        vector_metrics["vector_operations_total"].labels(
            operation="add_content", collection=collection_name, status="error"
        ).inc()
        raise HTTPException(
            status_code=500, detail=f"Error adding travel content: {str(e)}"
        )
    finally:
        # Track operation duration
        duration = time.time() - start_time
        vector_metrics["vector_operation_duration_seconds"].labels(
            operation="add_content", collection=collection_name
        ).observe(duration)


@router.post("/search", response_model=SearchResponse)
@track_vector_operation("search", "travel_content")
async def search_travel_content_with_metrics(
    request: SearchRequest,
    collection_name: str = "travel_content",
    vector_service: VectorService = Depends(get_vector_service),
):
    """Search travel content with metrics tracking"""
    start_time = time.time()

    try:
        # Track search attempt
        business_metrics["travel_searches_total"].labels(
            search_type="vector", destination="unknown"  # Could be extracted from query
        ).inc()

        business_metrics["vector_searches_total"].labels(
            collection_name=collection_name
        ).inc()

        results = vector_service.search_travel_content(
            collection_name=collection_name,
            query=request.query,
            limit=request.limit,
            score_threshold=request.score_threshold,
        )

        # Convert results to response format
        search_results = []
        for result in results:
            search_results.append(
                SearchResult(
                    content_id=result.get("content_id", ""),
                    title=result.get("title", ""),
                    description=result.get("description", ""),
                    content_type=result.get("content_type", ""),
                    score=result.get("score", 0.0),
                    metadata=result.get("metadata", {}),
                )
            )

        vector_metrics["vector_operations_total"].labels(
            operation="search", collection=collection_name, status="success"
        ).inc()

        return SearchResponse(
            results=search_results,
            total_found=len(search_results),
            query=request.query,
            collection_name=collection_name,
        )

    except Exception as e:
        vector_metrics["vector_operations_total"].labels(
            operation="search", collection=collection_name, status="error"
        ).inc()
        raise HTTPException(
            status_code=500, detail=f"Error searching travel content: {str(e)}"
        )
    finally:
        # Track search duration
        duration = time.time() - start_time
        business_metrics["search_duration_seconds"].labels(
            search_type="vector"
        ).observe(duration)

        vector_metrics["vector_search_duration_seconds"].labels(
            collection_name=collection_name
        ).observe(duration)


@router.post("/test-data")
@track_vector_operation("add_test_data", "travel_content")
async def add_test_data_with_metrics(
    collection_name: str = "travel_content",
    vector_service: VectorService = Depends(get_vector_service),
):
    """Add test data with metrics tracking"""
    try:
        success = vector_service.add_test_data(collection_name)

        if success:
            vector_metrics["vector_operations_total"].labels(
                operation="add_test_data", collection=collection_name, status="success"
            ).inc()

            return {"message": f"Test data added successfully to {collection_name}"}
        else:
            vector_metrics["vector_operations_total"].labels(
                operation="add_test_data", collection=collection_name, status="error"
            ).inc()
            raise HTTPException(status_code=500, detail="Failed to add test data")

    except Exception as e:
        vector_metrics["vector_operations_total"].labels(
            operation="add_test_data", collection=collection_name, status="error"
        ).inc()
        raise HTTPException(status_code=500, detail=f"Error adding test data: {str(e)}")


@router.get("/health")
async def health_check_with_metrics(
    vector_service: VectorService = Depends(get_vector_service),
):
    """Health check with metrics tracking"""
    try:
        health_status = vector_service.health_check()

        vector_metrics["vector_operations_total"].labels(
            operation="health_check", collection="all", status="success"
        ).inc()

        return health_status
    except Exception as e:
        vector_metrics["vector_operations_total"].labels(
            operation="health_check", collection="all", status="error"
        ).inc()
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")


@router.get("/metrics/summary")
async def get_vector_metrics_summary():
    """Get vector metrics summary"""
    try:
        return {
            "message": "Vector metrics are available at /metrics endpoint",
            "tracked_operations": [
                "get_collection_info",
                "add_content",
                "search",
                "add_test_data",
                "health_check",
            ],
            "business_metrics": [
                "travel_searches_total",
                "vector_content_added_total",
                "vector_searches_total",
            ],
        }
    except Exception as e:
        logger.error(f"Error getting vector metrics summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics summary")
