# db.py

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Create session factory
async_session_maker = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


# Base class for models
class Base(DeclarativeBase):
    pass


# Dependency to get async database session
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Function to create all database tables
async def create_tables():
    """Create all database tables defined in models"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Function to drop all database tables (use with caution!)
async def drop_tables():
    """Drop all database tables - use with caution!"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Function to recreate all tables (drop and create)
async def recreate_tables():
    """Drop all tables and recreate them - use with caution!"""
    await drop_tables()
    await create_tables()


# Engine cleanup function for application shutdown
async def close_engine():
    """Close the database engine"""
    await engine.dispose()
