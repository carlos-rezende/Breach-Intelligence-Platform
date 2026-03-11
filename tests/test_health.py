"""Testes do endpoint de health."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Testa se o endpoint /health retorna status."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "api" in data
    assert "database" in data
    assert "redis" in data
    assert "workers" in data
    assert data["api"] == "ok"
