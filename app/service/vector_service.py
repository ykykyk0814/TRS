import logging
from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class VectorService:
    """Service for managing vector operations with Qdrant"""

    def __init__(self, qdrant_url: str = "http://localhost:6333"):
        """Initialize the vector service

        Args:
            qdrant_url: Qdrant server URL
        """
        self.qdrant_url = qdrant_url
        self.client = None
        self.embedding_model = None
        self._initialize_client()
        self._initialize_embedding_model()

    def _initialize_client(self):
        """Initialize Qdrant client"""
        try:
            self.client = QdrantClient(url=self.qdrant_url)
            logger.info(f"Connected to Qdrant at {self.qdrant_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            raise

    def _initialize_embedding_model(self):
        """Initialize the sentence transformer model"""
        try:
            # Using a lightweight model for travel content
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Embedding model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            raise

    def create_collection(self, collection_name: str, vector_size: int = 384) -> bool:
        """Create a new collection in Qdrant

        Args:
            collection_name: Name of the collection
            vector_size: Size of the vector embeddings

        Returns:
            bool: True if collection created successfully
        """
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
            logger.info(f"Collection '{collection_name}' created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create collection '{collection_name}': {e}")
            return False

    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection from Qdrant

        Args:
            collection_name: Name of the collection to delete

        Returns:
            bool: True if collection deleted successfully
        """
        try:
            self.client.delete_collection(collection_name=collection_name)
            logger.info(f"Collection '{collection_name}' deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection '{collection_name}': {e}")
            return False

    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for a text

        Args:
            text: Text to embed

        Returns:
            List[float]: Vector embedding
        """
        try:
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    def add_travel_content(
        self,
        collection_name: str,
        content_id: str,
        title: str,
        description: str,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Add travel content to the vector database

        Args:
            collection_name: Name of the collection
            content_id: Unique identifier for the content
            title: Title of the travel content
            description: Description or full text
            content_type: Type of content (destination, activity, etc.)
            metadata: Additional metadata

        Returns:
            bool: True if content added successfully
        """
        try:
            # Combine title and description for embedding
            text_for_embedding = f"{title} {description}"
            embedding = self.get_embedding(text_for_embedding)

            # Prepare metadata
            payload = {
                "content_id": content_id,
                "title": title,
                "description": description,
                "content_type": content_type,
                "text_length": len(text_for_embedding),
            }

            if metadata:
                payload.update(metadata)

            # Create point
            point = PointStruct(id=content_id, vector=embedding, payload=payload)

            # Add to collection
            self.client.upsert(collection_name=collection_name, points=[point])

            logger.info(
                f"Added travel content '{content_id}' to collection '{collection_name}'"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to add travel content '{content_id}': {e}")
            return False

    def search_travel_content(
        self,
        collection_name: str,
        query: str,
        limit: int = 10,
        score_threshold: float = 0.7,
        content_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search for travel content using vector similarity

        Args:
            collection_name: Name of the collection to search
            query: Search query
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            content_type: Filter by content type

        Returns:
            List[Dict]: Search results with scores
        """
        try:
            # Generate embedding for query
            query_embedding = self.get_embedding(query)

            # Build filter if content_type specified
            search_filter = None
            if content_type:
                search_filter = Filter(
                    must=[
                        FieldCondition(
                            key="content_type", match=MatchValue(value=content_type)
                        )
                    ]
                )

            # Search
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=search_filter,
            )

            # Format results
            results = []
            for hit in search_result:
                result = {"id": hit.id, "score": hit.score, "payload": hit.payload}
                results.append(result)

            logger.info(f"Found {len(results)} results for query '{query}'")
            return results

        except Exception as e:
            logger.error(f"Failed to search travel content: {e}")
            return []

    def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a collection

        Args:
            collection_name: Name of the collection

        Returns:
            Dict: Collection information
        """
        try:
            info = self.client.get_collection(collection_name=collection_name)
            return {
                "name": collection_name,
                "vector_size": info.config.params.vectors.size,
                "distance": info.config.params.vectors.distance,
                "points_count": info.points_count,
            }
        except Exception as e:
            logger.error(f"Failed to get collection info for '{collection_name}': {e}")
            return None

    def add_test_data(self, collection_name: str = "travel_content") -> bool:
        """Add test travel data to the collection

        Args:
            collection_name: Name of the collection

        Returns:
            bool: True if test data added successfully
        """
        test_data = [
            {
                "content_id": "dest_001",
                "title": "Bangkok, Thailand",
                "description": "Vibrant capital city with rich culture, street food, and historic temples. Perfect for budget travelers and food lovers.",
                "content_type": "destination",
                "metadata": {
                    "country": "Thailand",
                    "region": "Southeast Asia",
                    "budget_level": "budget",
                },
            },
            {
                "content_id": "dest_002",
                "title": "Tokyo, Japan",
                "description": "Modern metropolis blending technology with traditional culture. Excellent for luxury travel and unique experiences.",
                "content_type": "destination",
                "metadata": {
                    "country": "Japan",
                    "region": "East Asia",
                    "budget_level": "luxury",
                },
            },
            {
                "content_id": "dest_003",
                "title": "Paris, France",
                "description": "Romantic city of lights with world-class museums, cuisine, and iconic landmarks like the Eiffel Tower.",
                "content_type": "destination",
                "metadata": {
                    "country": "France",
                    "region": "Europe",
                    "budget_level": "mid-range",
                },
            },
            {
                "content_id": "activity_001",
                "title": "Street Food Tour",
                "description": "Explore local cuisine through guided street food tours in various cities. Taste authentic dishes and learn about local culture.",
                "content_type": "activity",
                "metadata": {
                    "category": "food",
                    "duration": "2-4 hours",
                    "group_size": "small",
                },
            },
            {
                "content_id": "activity_002",
                "title": "Museum Visits",
                "description": "Cultural exploration through world-renowned museums and galleries. Perfect for art and history enthusiasts.",
                "content_type": "activity",
                "metadata": {
                    "category": "culture",
                    "duration": "2-6 hours",
                    "group_size": "individual",
                },
            },
        ]

        try:
            for item in test_data:
                success = self.add_travel_content(
                    collection_name=collection_name,
                    content_id=item["content_id"],
                    title=item["title"],
                    description=item["description"],
                    content_type=item["content_type"],
                    metadata=item["metadata"],
                )
                if not success:
                    logger.error(f"Failed to add test item {item['content_id']}")
                    return False

            logger.info(
                f"Successfully added {len(test_data)} test items to collection '{collection_name}'"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to add test data: {e}")
            return False

    def health_check(self) -> bool:
        """Check if Qdrant is operational

        Returns:
            bool: True if Qdrant is healthy
        """
        try:
            # Try to get collections info
            collections = self.client.get_collections()
            logger.info(
                f"Qdrant health check passed. Found {len(collections.collections)} collections"
            )
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False
