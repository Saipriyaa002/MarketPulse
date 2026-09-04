import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_watchlist_crud_operations(client: AsyncClient):
    # 1. Login as guest
    guest_res = await client.post("/api/v1/auth/guest")
    assert guest_res.status_code == 200
    token = guest_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. List initial seeded watchlists
    list_res = await client.get("/api/v1/watchlists", headers=headers)
    assert list_res.status_code == 200
    watchlists = list_res.json()
    assert len(watchlists) >= 1
    assert watchlists[0]["name"] == "Main Watchlist"
    initial_id = watchlists[0]["id"]

    # 3. Create a secondary custom watchlist
    create_res = await client.post(
        "/api/v1/watchlists",
        headers=headers,
        json={
            "name": "Auto & Mobility",
            "description": "Auto OEMs and auto component makers",
            "is_default": False,
            "symbols": ["TATAMOTORS", "MARUTI"],
        },
    )
    assert create_res.status_code == 201
    custom_wl = create_res.json()
    assert custom_wl["name"] == "Auto & Mobility"
    assert len(custom_wl["items"]) == 2

    # 4. Add item to secondary watchlist
    add_item_res = await client.post(
        f"/api/v1/watchlists/{custom_wl['id']}/items",
        headers=headers,
        json={"symbol": "BHARTIARTL", "custom_tag": "Hedge"},
    )
    assert add_item_res.status_code == 201
    assert add_item_res.json()["symbol"] == "BHARTIARTL"
    assert add_item_res.json()["quote"] is not None

    # 5. Remove item from watchlist
    del_item_res = await client.delete(
        f"/api/v1/watchlists/{custom_wl['id']}/items/MARUTI",
        headers=headers,
    )
    assert del_item_res.status_code == 204

    # 6. Delete custom watchlist
    del_wl_res = await client.delete(
        f"/api/v1/watchlists/{custom_wl['id']}",
        headers=headers,
    )
    assert del_wl_res.status_code == 204
