"""Testes de autenticação."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient):
    """Testa registro e login."""
    response = await client.post(
        "/auth/register",
        json={"email": "newuser@test.com", "password": "securepass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@test.com"
    assert "id" in data

    response = await client.post(
        "/auth/login",
        json={"email": "newuser@test.com", "password": "securepass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Testa registro com email duplicado."""
    await client.post(
        "/auth/register",
        json={"email": "dup@test.com", "password": "securepass123"},
    )
    response = await client.post(
        "/auth/register",
        json={"email": "dup@test.com", "password": "otherpass456"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Testa login com credenciais inválidas."""
    response = await client.post(
        "/auth/login",
        json={"email": "nonexistent@test.com", "password": "wrongpass"},
    )
    assert response.status_code == 401
