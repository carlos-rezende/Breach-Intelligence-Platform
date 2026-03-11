"""Schemas para verificação de senha."""

from datetime import datetime

from pydantic import BaseModel, Field


class PasswordCheckRequest(BaseModel):
    """Request para verificação de senha."""

    password: str = Field(..., min_length=1, description="Senha a verificar")


class PasswordCheckResponse(BaseModel):
    """Resposta da verificação de senha."""

    pwned: bool = Field(..., description="Se a senha foi encontrada em vazamentos")
    count: int = Field(..., description="Quantas vezes a senha apareceu em vazamentos")
    checked_at: datetime = Field(..., description="Data/hora da verificação")


class PasswordCheckHistoryItem(BaseModel):
    """Item do histórico (sem dados da senha)."""

    pwned: bool
    count: int
    checked_at: datetime


class PasswordCheckHistoryResponse(BaseModel):
    """Resposta do histórico."""

    total: int
    items: list[PasswordCheckHistoryItem]
