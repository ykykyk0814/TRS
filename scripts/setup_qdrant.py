#!/usr/bin/env python3
"""
Setup script for Qdrant vector database
"""

import logging
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.service.vector_service import VectorService

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_qdrant():
    """Setup Qdrant with collections and test data"""
    try:
        logger.info("Starting Qdrant setup...")

        # Initialize vector service
        vector_service = VectorService()

        # Check if Qdrant is operational
        if not vector_service.health_check():
            logger.error("Qdrant is not operational. Please start Qdrant first.")
            return False

        logger.info("Qdrant is operational. Proceeding with setup...")

        # Create travel content collection
        collection_name = "travel_content"
        vector_size = 384  # Size for all-MiniLM-L6-v2 model

        logger.info(f"Creating collection '{collection_name}'...")
        if vector_service.create_collection(collection_name, vector_size):
            logger.info(f"Collection '{collection_name}' created successfully")
        else:
            logger.warning(f"Collection '{collection_name}' might already exist")

        # Add test data
        logger.info("Adding test data...")
        if vector_service.add_test_data(collection_name):
            logger.info("Test data added successfully")
        else:
            logger.error("Failed to add test data")
            return False

        # Verify setup
        collection_info = vector_service.get_collection_info(collection_name)
        if collection_info:
            logger.info(f"Collection info: {collection_info}")
        else:
            logger.error("Failed to get collection info")
            return False

        # Test search functionality
        logger.info("Testing search functionality...")
        search_results = vector_service.search_travel_content(
            collection_name=collection_name, query="beautiful destinations", limit=5
        )
        logger.info(f"Search test returned {len(search_results)} results")

        logger.info("Qdrant setup completed successfully!")
        return True

    except Exception as e:
        logger.error(f"Setup failed: {e}")
        return False


def main():
    """Main function"""
    print("🚀 Qdrant Vector Database Setup")
    print("=" * 40)

    success = setup_qdrant()

    if success:
        print("\n✅ Setup completed successfully!")
        print("\nYou can now:")
        print("- Access Qdrant at http://localhost:6333")
        print("- Use the vector API endpoints")
        print("- Search travel content with semantic similarity")
    else:
        print("\n❌ Setup failed!")
        print("\nPlease check:")
        print("- Qdrant is running (docker-compose up)")
        print("- Network connectivity")
        print("- Logs for detailed error information")
        sys.exit(1)


if __name__ == "__main__":
    main()
