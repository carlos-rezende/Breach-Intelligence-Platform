"""Schemas para estatísticas."""

from pydantic import BaseModel, Field


class ProviderStats(BaseModel):
    """Estatísticas por provedor."""

    provider: str
    checks_count: int


class StatsResponse(BaseModel):
    """Resposta das estatísticas."""

    total_checks: int = Field(..., description="Total de consultas")
    emails_analyzed: int = Field(..., description="Emails únicos analisados")
    breaches_detected: int = Field(..., description="Total de vazamentos detectados")
    checks_by_provider: list[ProviderStats] = Field(
        default_factory=list, description="Consultas por provedor"
    )
