import pytest
from httpx import AsyncClient
from app.schemas.pulse import PulseItemSchema
from app.services.ai_explainer import AIExplainerService


def test_dossier_and_fallback_explanation():
    item = PulseItemSchema(
        symbol="INFY",
        name="Infosys Limited",
        sector="Information Technology",
        current_price=1800.0,
        checkpoint_price=1890.0,
        price_change=-90.0,
        price_change_pct=-4.76,
        alpha_excess_pct=-3.8,
        sector_divergence_pct=-2.6,
        volume_z_score=2.9,
        current_volume=16000000,
        avg_volume_20d=5500000,
        attention_score=85,
        attention_level="CRITICAL",
        confidence_score=94,
        is_meaningful=True,
        primary_drivers=["High Alpha Excess", "Sector Divergence", "Volume Surge"],
        summary="Infosys moved -4.76% with heavy volume.",
        breakdown={},
        related_events=[
            {
                "id": "EVT-1",
                "headline": "Guidance revised downwards",
                "source": "Reuters",
                "impact": "CRITICAL",
            }
        ],
    )

    dossier = AIExplainerService.build_facts_dossier(item, "2026-09-04T10:00:00Z")
    assert dossier["symbol"] == "INFY"
    assert dossier["attention_score"] == 85
    assert len(dossier["verified_events"]) == 1

    explanation = AIExplainerService.generate_deterministic_explanation(dossier)
    assert "headline" in explanation
    assert "executive_summary" in explanation
    assert "key_takeaways" in explanation
    assert len(explanation["key_takeaways"]) >= 2
    assert "Guidance revised downwards" in explanation["key_takeaways"][-1]
    assert explanation["source"] == "deterministic_fallback_engine"


@pytest.mark.asyncio
async def test_explain_and_digest_api(client: AsyncClient):
    # 1. Login as guest
    auth_res = await client.post("/api/v1/auth/guest")
    assert auth_res.status_code == 200
    token = auth_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get watchlists
    wl_res = await client.get("/api/v1/watchlists", headers=headers)
    watchlist_id = wl_res.json()[0]["id"]

    # 3. Request explanation for INFY
    explain_res = await client.get(
        f"/api/v1/pulse/explain/INFY?watchlist_id={watchlist_id}",
        headers=headers,
    )
    assert explain_res.status_code == 200
    exp = explain_res.json()
    assert "headline" in exp
    assert "key_takeaways" in exp

    # 4. Request 'What Did I Miss?' Digest
    digest_res = await client.get(
        f"/api/v1/pulse/digest?watchlist_id={watchlist_id}",
        headers=headers,
    )
    assert digest_res.status_code == 200
    digest = digest_res.json()
    assert "title" in digest
    assert "sections" in digest
    assert len(digest["sections"]) >= 1
