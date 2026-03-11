"""Testes do endpoint de histórico."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_history_invalid_email(client: AsyncClient):
    """Testa histórico com email inválido."""
    response = await client.get("/history/invalid")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_history_valid_email(client: AsyncClient):
    """Testa histórico com email válido (pode retornar lista vazia)."""
    response = await client.get("/history/test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "total_checks" in data
    assert "checks" in data
    assert isinstance(data["checks"], list)
