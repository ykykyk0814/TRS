# tests/conftest.py
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.db import Base

DATABASE_URL = (
    "postgresql+asyncpg://postgres:password@localhost:5432/travel_recommendation"
)


@pytest_asyncio.fixture()
async def db_test_session():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    TestSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    async with TestSessionLocal() as session:
        yield session
    await engine.dispose()
