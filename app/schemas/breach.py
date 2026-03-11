"""Schemas para verificação de vazamentos."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class BreachCheckRequest(BaseModel):
    """Request para verificação de email."""

    email: EmailStr = Field(..., description="Email a verificar")


class BreachInfo(BaseModel):
    """Informação de um vazamento."""

    name: str = Field(..., description="Nome do serviço comprometido")
    year: int | None = Field(None, description="Ano do vazamento")


class BreachCheckResponse(BaseModel):
    """Resposta da verificação."""

    email: str = Field(..., description="Email verificado")
    breached: bool = Field(..., description="Se foi encontrado em vazamentos")
    breach_count: int = Field(..., description="Quantidade de vazamentos")
    breaches: list[BreachInfo] = Field(default_factory=list)
    risk_score: str = Field(..., description="Score: safe, low, medium, high")
    checked_at: datetime = Field(..., description="Data/hora da verificação")


class BreachHistoryItem(BaseModel):
    """Item do histórico."""

    id: int
    email: str
    breach_count: int
    providers_used: str | None
    risk_score: str
    created_at: datetime
    breaches: list[BreachInfo] = Field(default_factory=list)


class HistoryResponse(BaseModel):
    """Resposta do histórico."""

    email: str
    total_checks: int
    checks: list[BreachHistoryItem]
