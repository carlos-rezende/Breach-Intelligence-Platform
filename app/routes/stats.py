"""Rotas de estatísticas."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.stats import ProviderStats, StatsResponse
from app.services.breach_service import BreachService

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """
    Estatísticas da plataforma:
    - Total de consultas
    - Emails analisados
    - Vazamentos detectados
    - Consultas por provedor
    """
    service = BreachService(db)
    data = await service.get_stats()
    return StatsResponse(
        total_checks=data["total_checks"],
        emails_analyzed=data["emails_analyzed"],
        breaches_detected=data["breaches_detected"],
        checks_by_provider=[
            ProviderStats(provider=p["provider"], checks_count=p["checks_count"])
            for p in data["checks_by_provider"]
        ],
    )
