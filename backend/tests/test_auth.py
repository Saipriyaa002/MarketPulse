import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient):
    # Register
    reg_data = {
        "email": "trader@groww.in",
        "password": "strongpassword123",
        "full_name": "Groww Trader",
    }
    reg_res = await client.post("/api/v1/auth/register", json=reg_data)
    assert reg_res.status_code == 201
    token_data = reg_res.json()
    assert "access_token" in token_data
    assert token_data["user"]["email"] == "trader@groww.in"

    # Login
    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": "trader@groww.in", "password": "strongpassword123"},
    )
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()

    # Get /me with token
    token = login_res.json()["access_token"]
    me_res = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "trader@groww.in"


@pytest.mark.asyncio
async def test_guest_login(client: AsyncClient):
    res = await client.post("/api/v1/auth/guest")
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["is_guest"] is True
    assert "@marketpulse.demo" in data["user"]["email"]
