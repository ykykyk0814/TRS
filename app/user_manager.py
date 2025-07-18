# app/user_manager.py

from uuid import UUID

from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_async_session
from .models import User

SECRET = "your-super-secret-key"


async def get_user_db(session: AsyncSession):
    yield SQLAlchemyUserDatabase(session, User)


class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    def __init__(self, user_db: SQLAlchemyUserDatabase):
        super().__init__(user_db)


async def get_user_manager():
    async for user_db in get_user_db(await get_async_session()):
        yield UserManager(user_db)
