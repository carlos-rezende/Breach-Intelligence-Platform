"""Testes de verificação de senha."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_password_check_pwned(client: AsyncClient):
    """Testa senha conhecidamente vazada (password123)."""
    response = await client.post(
        "/password-check",
        json={"password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "pwned" in data
    assert "count" in data
    assert "checked_at" in data
    assert data["pwned"] is True
    assert data["count"] > 0


@pytest.mark.asyncio
async def test_password_check_empty(client: AsyncClient):
    """Testa senha vazia (deve falhar validação)."""
    response = await client.post(
        "/password-check",
        json={"password": ""},
    )
    assert response.status_code == 422
