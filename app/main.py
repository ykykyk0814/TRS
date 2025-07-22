import logging
import os

from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import get_db_session_manager, init_db_session_manager
from app.api import api_router

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Read settings
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/mydb")
ENV = os.getenv("ENV", "development")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown logic"""
    try:
        init_db_session_manager(DATABASE_URL, echo=True)
        logger.info("Database session initialized successfully!")
        logger.info("Use 'alembic upgrade head' to apply database migrations.")
        yield
    except Exception as e:
        logger.error(f"Failed to initialize database session: {e}")
        raise
    finally:
        try:
            db_manager = get_db_session_manager()
            await db_manager.dispose()
            logger.info("Database connections disposed successfully!")
        except Exception as e:
            logger.error(f"Failed to dispose database connections: {e}")


# Initialize FastAPI app
app = FastAPI(
    title="Travel Recommendation API",
    description="Authentication & User Management with FastAPI-Users.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")
