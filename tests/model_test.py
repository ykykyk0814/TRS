from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.models import Preference, Ticket, User


@pytest.mark.asyncio
async def test_user_creation(db_test_session):
    user = User(id=uuid4(), email="test@example.com", hashed_password="hashed")
    db_test_session.add(user)
    await db_test_session.commit()

    result = await db_test_session.get(User, user.id)
    assert result.email == "test@example.com"


@pytest.mark.asyncio
async def test_user_preference(db_test_session):
    user = User(id=uuid4(), email="pref@example.com", hashed_password="hashed")
    db_test_session.add(user)
    await db_test_session.flush()

    pref = Preference(user_id=user.id, prefers_email=False, prefers_sms=True)
    db_test_session.add(pref)
    await db_test_session.commit()

    result = await db_test_session.execute(
        select(User).options(selectinload(User.preference)).where(User.id == user.id)
    )
    loaded = result.scalar_one()
    assert loaded.preference.prefers_sms is True


@pytest.mark.asyncio
async def test_user_ticket(db_test_session):
    user = User(id=uuid4(), email="ticket@example.com", hashed_password="hashed")
    db_test_session.add(user)
    await db_test_session.flush()

    ticket = Ticket(
        user_id=user.id,
        origin="NYC",
        destination="LAX",
        departure_time=datetime.utcnow(),
        arrival_time=datetime.utcnow(),
    )
    db_test_session.add(ticket)
    await db_test_session.commit()

    result = await db_test_session.execute(
        select(User).options(selectinload(User.tickets)).where(User.id == user.id)
    )
    loaded = result.scalar_one()
    assert len(loaded.tickets) == 1
