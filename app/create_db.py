# create_db.py

from app.db import engine
from app.models import Base


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


import asyncio

asyncio.run(init_models())
