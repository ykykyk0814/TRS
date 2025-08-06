from unittest.mock import Mock, patch

import pytest

from app.service.vector_service import VectorService


class TestVectorService:
    """Test cases for VectorService"""

    @pytest.fixture
    def mock_qdrant_client(self):
        """Mock Qdrant client"""
        with patch("app.service.vector_service.QdrantClient") as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def mock_embedding_model(self):
        """Mock sentence transformer model"""
        with patch("app.service.vector_service.SentenceTransformer") as mock_model:
            mock_instance = Mock()
            mock_instance.encode.return_value = [
                0.1,
                0.2,
                0.3,
            ] * 128  # 384-dimensional vector
            mock_model.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def vector_service(self, mock_qdrant_client, mock_embedding_model):
        """Vector service instance with mocked dependencies"""
        return VectorService(qdrant_url="http://localhost:6333")

    def test_initialization(
        self, vector_service, mock_qdrant_client, mock_embedding_model
    ):
        """Test VectorService initialization"""
        assert vector_service.client is not None
        assert vector_service.embedding_model is not None
        assert vector_service.qdrant_url == "http://localhost:6333"

    def test_create_collection_success(self, vector_service, mock_qdrant_client):
        """Test successful collection creation"""
        # Arrange
        collection_name = "test_collection"
        vector_size = 384

        # Act
        result = vector_service.create_collection(collection_name, vector_size)

        # Assert
        assert result is True
        mock_qdrant_client.create_collection.assert_called_once()
        call_args = mock_qdrant_client.create_collection.call_args
        assert call_args[1]["collection_name"] == collection_name

    def test_create_collection_failure(self, vector_service, mock_qdrant_client):
        """Test collection creation failure"""
        # Arrange
        mock_qdrant_client.create_collection.side_effect = Exception(
            "Connection failed"
        )

        # Act
        result = vector_service.create_collection("test_collection", 384)

        # Assert
        assert result is False

    def test_delete_collection_success(self, vector_service, mock_qdrant_client):
        """Test successful collection deletion"""
        # Arrange
        collection_name = "test_collection"

        # Act
        result = vector_service.delete_collection(collection_name)

        # Assert
        assert result is True
        mock_qdrant_client.delete_collection.assert_called_once_with(
            collection_name=collection_name
        )

    def test_delete_collection_failure(self, vector_service, mock_qdrant_client):
        """Test collection deletion failure"""
        # Arrange
        mock_qdrant_client.delete_collection.side_effect = Exception(
            "Collection not found"
        )

        # Act
        result = vector_service.delete_collection("test_collection")

        # Assert
        assert result is False

    def test_get_embedding(self, vector_service, mock_embedding_model):
        """Test embedding generation"""
        # Arrange
        test_text = "Test travel content"
        expected_embedding = [0.1, 0.2, 0.3] * 128

        # Act
        result = vector_service.get_embedding(test_text)

        # Assert
        assert result == expected_embedding
        mock_embedding_model.encode.assert_called_once_with(test_text)

    def test_add_travel_content_success(
        self, vector_service, mock_qdrant_client, mock_embedding_model
    ):
        """Test successful travel content addition"""
        # Arrange
        content_data = {
            "content_id": "test_001",
            "title": "Test Destination",
            "description": "A beautiful test destination",
            "content_type": "destination",
            "metadata": {"country": "Test Country"},
        }

        # Act
        result = vector_service.add_travel_content(
            collection_name="test_collection", **content_data
        )

        # Assert
        assert result is True
        mock_qdrant_client.upsert.assert_called_once()

    def test_add_travel_content_failure(self, vector_service, mock_qdrant_client):
        """Test travel content addition failure"""
        # Arrange
        mock_qdrant_client.upsert.side_effect = Exception("Upsert failed")

        # Act
        result = vector_service.add_travel_content(
            collection_name="test_collection",
            content_id="test_001",
            title="Test",
            description="Test description",
            content_type="destination",
        )

        # Assert
        assert result is False

    def test_search_travel_content_success(
        self, vector_service, mock_qdrant_client, mock_embedding_model
    ):
        """Test successful travel content search"""
        # Arrange
        query = "beautiful destinations"
        mock_search_result = [
            Mock(id="dest_001", score=0.95, payload={"title": "Bangkok"}),
            Mock(id="dest_002", score=0.85, payload={"title": "Tokyo"}),
        ]
        mock_qdrant_client.search.return_value = mock_search_result

        # Act
        result = vector_service.search_travel_content(
            collection_name="test_collection",
            query=query,
            limit=10,
            score_threshold=0.7,
        )

        # Assert
        assert len(result) == 2
        assert result[0]["id"] == "dest_001"
        assert result[0]["score"] == 0.95
        mock_qdrant_client.search.assert_called_once()

    def test_search_travel_content_with_filter(
        self, vector_service, mock_qdrant_client, mock_embedding_model
    ):
        """Test travel content search with content type filter"""
        # Arrange
        query = "cultural activities"
        mock_search_result = [
            Mock(id="activity_001", score=0.92, payload={"title": "Museum Visit"})
        ]
        mock_qdrant_client.search.return_value = mock_search_result

        # Act
        result = vector_service.search_travel_content(
            collection_name="test_collection", query=query, content_type="activity"
        )

        # Assert
        assert len(result) == 1
        assert result[0]["payload"]["title"] == "Museum Visit"
        # Verify filter was applied
        call_args = mock_qdrant_client.search.call_args
        assert call_args[1]["query_filter"] is not None

    def test_search_travel_content_empty_results(
        self, vector_service, mock_qdrant_client, mock_embedding_model
    ):
        """Test travel content search with no results"""
        # Arrange
        mock_qdrant_client.search.return_value = []

        # Act
        result = vector_service.search_travel_content(
            collection_name="test_collection", query="nonexistent content"
        )

        # Assert
        assert len(result) == 0

    def test_get_collection_info_success(self, vector_service, mock_qdrant_client):
        """Test successful collection info retrieval"""
        # Arrange
        collection_name = "test_collection"
        mock_collection_info = Mock()
        mock_collection_info.config.params.vectors.size = 384
        mock_collection_info.config.params.vectors.distance = "Cosine"
        mock_collection_info.points_count = 100
        mock_qdrant_client.get_collection.return_value = mock_collection_info

        # Act
        result = vector_service.get_collection_info(collection_name)

        # Assert
        assert result is not None
        assert result["name"] == collection_name
        assert result["vector_size"] == 384
        assert result["points_count"] == 100
        mock_qdrant_client.get_collection.assert_called_once_with(
            collection_name=collection_name
        )

    def test_get_collection_info_not_found(self, vector_service, mock_qdrant_client):
        """Test collection info retrieval for non-existent collection"""
        # Arrange
        mock_qdrant_client.get_collection.side_effect = Exception(
            "Collection not found"
        )

        # Act
        result = vector_service.get_collection_info("nonexistent")

        # Assert
        assert result is None

    def test_add_test_data_success(
        self, vector_service, mock_qdrant_client, mock_embedding_model
    ):
        """Test successful test data addition"""
        # Arrange
        collection_name = "test_collection"

        # Act
        result = vector_service.add_test_data(collection_name)

        # Assert
        assert result is True
        # Should be called 5 times (one for each test item)
        assert mock_qdrant_client.upsert.call_count == 5

    def test_add_test_data_partial_failure(
        self, vector_service, mock_qdrant_client, mock_embedding_model
    ):
        """Test test data addition with partial failure"""
        # Arrange
        # Make the third call fail
        mock_qdrant_client.upsert.side_effect = [
            None,
            None,
            Exception("Failed"),
            None,
            None,
        ]

        # Act
        result = vector_service.add_test_data("test_collection")

        # Assert
        assert result is False

    def test_health_check_success(self, vector_service, mock_qdrant_client):
        """Test successful health check"""
        # Arrange
        mock_collections = Mock()
        mock_collections.collections = [Mock(), Mock()]  # 2 collections
        mock_qdrant_client.get_collections.return_value = mock_collections

        # Act
        result = vector_service.health_check()

        # Assert
        assert result is True
        mock_qdrant_client.get_collections.assert_called_once()

    def test_health_check_failure(self, vector_service, mock_qdrant_client):
        """Test health check failure"""
        # Arrange
        mock_qdrant_client.get_collections.side_effect = Exception("Connection failed")

        # Act
        result = vector_service.health_check()

        # Assert
        assert result is False

    def test_embedding_model_initialization_failure(self, mock_qdrant_client):
        """Test embedding model initialization failure"""
        # Arrange
        with patch("app.service.vector_service.SentenceTransformer") as mock_model:
            mock_model.side_effect = Exception("Model download failed")

            # Act & Assert
            with pytest.raises(Exception, match="Model download failed"):
                VectorService()

    def test_qdrant_client_initialization_failure(self):
        """Test Qdrant client initialization failure"""
        # Arrange
        with patch("app.service.vector_service.QdrantClient") as mock_client:
            mock_client.side_effect = Exception("Connection failed")

            # Act & Assert
            with pytest.raises(Exception, match="Connection failed"):
                VectorService()


class TestVectorServiceIntegration:
    """Integration tests for VectorService (requires Qdrant running)"""

    @pytest.mark.integration
    def test_full_workflow(self):
        """Test complete workflow: create collection, add content, search"""
        # This test requires Qdrant to be running
        # It's marked as integration test and can be run separately
        pass
