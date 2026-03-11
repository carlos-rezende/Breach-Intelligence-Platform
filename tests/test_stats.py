"""Testes do endpoint de estatísticas."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_stats_endpoint(client: AsyncClient):
    """Testa se o endpoint /stats retorna dados corretos."""
    response = await client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_checks" in data
    assert "emails_analyzed" in data
    assert "breaches_detected" in data
    assert "checks_by_provider" in data
    assert isinstance(data["total_checks"], int)
    assert isinstance(data["checks_by_provider"], list)
