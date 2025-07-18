import pytest
from httpx import AsyncClient
from app.main import app

# Test user data
test_email = "testuser@example.com"
test_password = "password123"


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_register():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/auth/register", json={
            "email": test_email,
            "password": test_password,
            "is_active": True,
            "is_superuser": False,
            "is_verified": False
        })
    # allow 400 if user already exists
    assert response.status_code in [201, 400]


@pytest.mark.asyncio
async def test_login():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/auth/jwt/login", data={
            "username": test_email,
            "password": test_password
        })
    assert response.status_code == 200
    json_resp = response.json()
    assert "access_token" in json_resp
    assert "token_type" in json_resp
    global access_token
    access_token = json_resp["access_token"]


@pytest.mark.asyncio
async def test_get_current_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await ac.get("/users/me", headers=headers)
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["email"] == test_email


@pytest.mark.asyncio
async def test_logout():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await ac.post("/auth/jwt/logout", headers=headers)
    assert response.status_code == 204
