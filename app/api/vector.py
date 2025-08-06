from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.service.vector_service import VectorService

router = APIRouter(prefix="/vector", tags=["vector"])


# Pydantic models for request/response
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
    content_type: Optional[str] = None


class CollectionRequest(BaseModel):
    collection_name: str
    vector_size: int = 384


class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total_found: int
    query: str


class HealthResponse(BaseModel):
    status: str
    message: str
    collections_count: int


def get_vector_service() -> VectorService:
    """Dependency to get vector service instance"""
    return VectorService()


@router.post("/collections", response_model=Dict[str, Any])
async def create_collection(
    request: CollectionRequest,
    vector_service: VectorService = Depends(get_vector_service),
):
    """Create a new collection in Qdrant"""
    try:
        success = vector_service.create_collection(
            collection_name=request.collection_name, vector_size=request.vector_size
        )
        if success:
            return {
                "message": f"Collection '{request.collection_name}' created successfully",
                "collection_name": request.collection_name,
                "vector_size": request.vector_size,
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create collection")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating collection: {str(e)}"
        )


@router.delete("/collections/{collection_name}")
async def delete_collection(
    collection_name: str, vector_service: VectorService = Depends(get_vector_service)
):
    """Delete a collection from Qdrant"""
    try:
        success = vector_service.delete_collection(collection_name=collection_name)
        if success:
            return {"message": f"Collection '{collection_name}' deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete collection")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error deleting collection: {str(e)}"
        )


@router.get("/collections/{collection_name}")
async def get_collection_info(
    collection_name: str, vector_service: VectorService = Depends(get_vector_service)
):
    """Get information about a collection"""
    try:
        info = vector_service.get_collection_info(collection_name=collection_name)
        if info:
            return info
        else:
            raise HTTPException(
                status_code=404, detail=f"Collection '{collection_name}' not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting collection info: {str(e)}"
        )


@router.post("/content")
async def add_travel_content(
    request: TravelContentRequest,
    collection_name: str = "travel_content",
    vector_service: VectorService = Depends(get_vector_service),
):
    """Add travel content to the vector database"""
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
            return {
                "message": f"Travel content '{request.content_id}' added successfully",
                "content_id": request.content_id,
                "collection_name": collection_name,
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to add travel content")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error adding travel content: {str(e)}"
        )


@router.post("/search", response_model=SearchResponse)
async def search_travel_content(
    request: SearchRequest,
    collection_name: str = "travel_content",
    vector_service: VectorService = Depends(get_vector_service),
):
    """Search for travel content using vector similarity"""
    try:
        results = vector_service.search_travel_content(
            collection_name=collection_name,
            query=request.query,
            limit=request.limit,
            score_threshold=request.score_threshold,
            content_type=request.content_type,
        )
        return SearchResponse(
            results=results, total_found=len(results), query=request.query
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error searching travel content: {str(e)}"
        )


@router.post("/test-data")
async def add_test_data(
    collection_name: str = "travel_content",
    vector_service: VectorService = Depends(get_vector_service),
):
    """Add test travel data to the collection"""
    try:
        success = vector_service.add_test_data(collection_name=collection_name)
        if success:
            return {
                "message": f"Test data added successfully to collection '{collection_name}'",
                "collection_name": collection_name,
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to add test data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding test data: {str(e)}")


@router.get("/health", response_model=HealthResponse)
async def health_check(vector_service: VectorService = Depends(get_vector_service)):
    """Check if Qdrant is operational"""
    try:
        is_healthy = vector_service.health_check()
        if is_healthy:
            # Get collections count
            collections = vector_service.client.get_collections()
            return HealthResponse(
                status="healthy",
                message="Qdrant is operational",
                collections_count=len(collections.collections),
            )
        else:
            raise HTTPException(status_code=503, detail="Qdrant is not operational")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")


@router.get("/embedding/{text}")
async def get_embedding(
    text: str, vector_service: VectorService = Depends(get_vector_service)
):
    """Get embedding for a text (for testing purposes)"""
    try:
        embedding = vector_service.get_embedding(text)
        return {
            "text": text,
            "embedding_size": len(embedding),
            "embedding": embedding[:10] + ["..."]
            if len(embedding) > 10
            else embedding,  # Show first 10 values
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating embedding: {str(e)}"
        )
