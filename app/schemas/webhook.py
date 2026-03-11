"""Schemas para Webhooks."""

from datetime import datetime

from pydantic import BaseModel, Field


class WebhookCreate(BaseModel):
    """Request para criar webhook."""

    url: str = Field(..., description="URL que receberá as notificações")


class WebhookResponse(BaseModel):
    """Resposta do webhook (secret mostrado apenas na criação)."""

    id: int
    url: str
    secret: str | None = Field(None, description="Secret para validar requisições - guarde em local seguro")
    created_at: datetime


class WebhookListItem(BaseModel):
    """Item da lista (sem secret)."""

    id: int
    url: str
    created_at: datetime
