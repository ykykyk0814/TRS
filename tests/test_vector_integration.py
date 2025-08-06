#!/usr/bin/env python3
"""
Integration tests for Vector Database functionality
Requires Qdrant to be running
"""

import pytest
import requests

# Test configuration
BASE_URL = "http://localhost:8000"
VECTOR_BASE_URL = f"{BASE_URL}/api/vector"


class TestVectorAPI:
    """Integration tests for Vector API endpoints"""

    def test_health_check(self):
        """Test vector health check endpoint"""
        response = requests.get(f"{VECTOR_BASE_URL}/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "collections_count" in data

    def test_create_collection(self):
        """Test collection creation"""
        collection_data = {"collection_name": "test_collection", "vector_size": 384}

        response = requests.post(f"{VECTOR_BASE_URL}/collections", json=collection_data)
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "test_collection" in data["message"]

    def test_get_collection_info(self):
        """Test getting collection information"""
        response = requests.get(f"{VECTOR_BASE_URL}/collections/travel_content")
        assert response.status_code == 200

        data = response.json()
        assert "name" in data
        assert "vector_size" in data
        assert "points_count" in data

    def test_add_travel_content(self):
        """Test adding travel content"""
        content_data = {
            "content_id": "test_dest_001",
            "title": "Test Destination",
            "description": "A beautiful test destination for integration testing",
            "content_type": "destination",
            "metadata": {
                "country": "Test Country",
                "region": "Test Region",
                "budget_level": "mid-range",
            },
        }

        response = requests.post(f"{VECTOR_BASE_URL}/content", json=content_data)
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "test_dest_001" in data["message"]

    def test_search_travel_content(self):
        """Test searching travel content"""
        search_data = {
            "query": "beautiful destinations",
            "limit": 5,
            "score_threshold": 0.5,
        }

        response = requests.post(f"{VECTOR_BASE_URL}/search", json=search_data)
        assert response.status_code == 200

        data = response.json()
        assert "results" in data
        assert "total_found" in data
        assert "query" in data
        assert isinstance(data["results"], list)

    def test_search_with_filter(self):
        """Test searching with content type filter"""
        search_data = {
            "query": "cultural activities",
            "limit": 3,
            "score_threshold": 0.5,
            "content_type": "activity",
        }

        response = requests.post(f"{VECTOR_BASE_URL}/search", json=search_data)
        assert response.status_code == 200

        data = response.json()
        assert "results" in data
        # All results should be activities
        for result in data["results"]:
            assert result["payload"]["content_type"] == "activity"

    def test_add_test_data(self):
        """Test adding test data"""
        response = requests.post(f"{VECTOR_BASE_URL}/test-data")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "Test data added successfully" in data["message"]

    def test_get_embedding(self):
        """Test embedding generation endpoint"""
        test_text = "beautiful travel destination"
        response = requests.get(f"{VECTOR_BASE_URL}/embedding/{test_text}")
        assert response.status_code == 200

        data = response.json()
        assert "text" in data
        assert "embedding_size" in data
        assert "embedding" in data
        assert data["embedding_size"] == 384  # all-MiniLM-L6-v2 size


class TestVectorServiceDirect:
    """Direct service tests (requires Qdrant running)"""

    def test_vector_service_initialization(self):
        """Test VectorService initialization"""
        from app.service.vector_service import VectorService

        service = VectorService()
        assert service.client is not None
        assert service.embedding_model is not None

    def test_health_check(self):
        """Test direct health check"""
        from app.service.vector_service import VectorService

        service = VectorService()
        assert service.health_check() is True

    def test_collection_operations(self):
        """Test collection creation and deletion"""
        from app.service.vector_service import VectorService

        service = VectorService()
        collection_name = "test_collection_integration"

        # Create collection
        assert service.create_collection(collection_name, 384) is True

        # Get collection info
        info = service.get_collection_info(collection_name)
        assert info is not None
        assert info["name"] == collection_name

        # Delete collection
        assert service.delete_collection(collection_name) is True

    def test_content_operations(self):
        """Test content addition and search"""
        from app.service.vector_service import VectorService

        service = VectorService()
        collection_name = "test_content_collection"

        # Create collection
        service.create_collection(collection_name, 384)

        # Add content
        success = service.add_travel_content(
            collection_name=collection_name,
            content_id="test_content_001",
            title="Integration Test Destination",
            description="A destination for integration testing",
            content_type="destination",
            metadata={"test": True},
        )
        assert success is True

        # Search content
        results = service.search_travel_content(
            collection_name=collection_name, query="integration test", limit=5
        )
        assert len(results) > 0
        assert results[0]["payload"]["content_id"] == "test_content_001"

        # Cleanup
        service.delete_collection(collection_name)


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v"])
