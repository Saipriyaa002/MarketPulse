import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_checkpoints_and_pulse_flow(client: AsyncClient):
    # 1. Login as guest
    auth_res = await client.post("/api/v1/auth/guest")
    assert auth_res.status_code == 200
    token = auth_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get user watchlists
    wl_res = await client.get("/api/v1/watchlists", headers=headers)
    assert wl_res.status_code == 200
    watchlists = wl_res.json()
    assert len(watchlists) > 0
    watchlist_id = watchlists[0]["id"]

    # 3. Fetch initial pulse (baseline checkpoint will be auto-created)
    pulse_res = await client.get(
        f"/api/v1/pulse/since-last-seen?watchlist_id={watchlist_id}",
        headers=headers,
    )
    assert pulse_res.status_code == 200
    pulse = pulse_res.json()
    assert pulse["watchlist_id"] == watchlist_id
    assert "executive_summary" in pulse
    assert len(pulse["items"]) > 0
    assert pulse["items"][0]["attention_score"] >= 0

    # 4. Check active checkpoint details
    cp_res = await client.get(
        f"/api/v1/checkpoints/current?watchlist_id={watchlist_id}",
        headers=headers,
    )
    assert cp_res.status_code == 200
    cp = cp_res.json()
    assert cp["watchlist_id"] == watchlist_id
    assert "snapshot_data" in cp

    # 5. Advance checkpoint
    adv_res = await client.post(
        "/api/v1/checkpoints/advance",
        headers=headers,
        json={"watchlist_id": watchlist_id, "trigger_event": "manual_ack"},
    )
    assert adv_res.status_code == 200
    assert adv_res.json()["trigger_event"] == "manual_ack"

    # 6. Test Demo Time Leap simulation
    leap_res = await client.post(
        "/api/v1/pulse/simulate-time-leap",
        headers=headers,
        json={"watchlist_id": watchlist_id, "hours_ago": 4.0, "simulate_volatility": True},
    )
    assert leap_res.status_code == 200
    leap_pulse = leap_res.json()
    assert leap_pulse["meaningful_count"] >= 1
    # Check that items are ranked by attention score descending
    scores = [item["attention_score"] for item in leap_pulse["items"]]
    assert scores == sorted(scores, reverse=True)

    # 7. Test 'Catch Me Up' immediately after Time Leap
    # Advancing checkpoint must establish current moment as baseline and clear past deltas
    catchup_adv = await client.post(
        "/api/v1/checkpoints/advance",
        headers=headers,
        json={"watchlist_id": watchlist_id, "trigger_event": "manual_ack"},
    )
    assert catchup_adv.status_code == 200

    catchup_pulse_res = await client.get(
        f"/api/v1/pulse/since-last-seen?watchlist_id={watchlist_id}",
        headers=headers,
    )
    assert catchup_pulse_res.status_code == 200
    catchup_pulse = catchup_pulse_res.json()
    assert catchup_pulse["meaningful_count"] == 0
    assert "caught up" in catchup_pulse["executive_summary"].lower()
    for item in catchup_pulse["items"]:
        assert item["price_change_pct"] == 0.0
        assert item["alpha_excess_pct"] == 0.0
        assert item["sector_divergence_pct"] == 0.0
