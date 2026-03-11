"""Testes de verificação de vazamentos."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_breach_check_demo_email(client: AsyncClient):
    """Testa verificação com email de demo."""
    response = await client.post(
        "/breach-check",
        json={"email": "admin@demo.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@demo.com"
    assert data["breached"] is True
    assert data["breach_count"] >= 3
    assert "breaches" in data
    assert data["risk_score"] in ("safe", "low", "medium", "high")
    assert "checked_at" in data


@pytest.mark.asyncio
async def test_breach_check_invalid_email(client: AsyncClient):
    """Testa validação de email inválido."""
    response = await client.post(
        "/breach-check",
        json={"email": "invalid"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_breach_check_unknown_email(client: AsyncClient):
    """Testa email sem vazamentos (mock LeakCheck para evitar chamadas externas)."""
    from unittest.mock import AsyncMock, patch

    from app.providers.base_provider import BreachResult

    with patch(
        "app.providers.leakcheck_provider.LeakCheckProvider.check_email",
        new_callable=AsyncMock,
        return_value=BreachResult(provider="leakcheck", breaches=[], success=True),
    ):
        response = await client.post(
            "/breach-check",
            json={"email": "unknown@example.com"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["breached"] is False
    assert data["breach_count"] == 0
