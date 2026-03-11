"""Schemas para API Keys."""

from datetime import datetime

from pydantic import BaseModel, Field


class ApiKeyCreate(BaseModel):
    """Request para criar API key."""

    name: str = Field(..., min_length=1, max_length=100, description="Nome da API key")


class ApiKeyResponse(BaseModel):
    """Resposta com a API key (mostrada apenas na criação)."""

    id: int
    name: str
    key: str = Field(..., description="API key - guarde em local seguro, não será exibida novamente")
    created_at: datetime


class ApiKeyListItem(BaseModel):
    """Item da lista de API keys (sem a chave)."""

    id: int
    name: str
    created_at: datetime
