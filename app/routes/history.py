"""Rotas de histórico."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.breach import BreachHistoryItem, BreachInfo, HistoryResponse
from app.services.breach_service import BreachService

router = APIRouter(prefix="/history", tags=["History"])


@router.get("/{email}", response_model=HistoryResponse)
async def get_history(
    email: str,
    db: AsyncSession = Depends(get_db),
):
    """Retorna histórico completo de verificações para o email."""
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Email inválido")

    service = BreachService(db)
    checks = await service.get_history(email)

    items = [
        BreachHistoryItem(
            id=c.id,
            email=c.email,
            breach_count=c.breach_count,
            providers_used=c.providers_used,
            risk_score=c.risk_score,
            created_at=c.created_at,
            breaches=[BreachInfo(name=b.name, year=b.year) for b in c.breaches],
        )
        for c in checks
    ]

    return HistoryResponse(
        email=email.lower(),
        total_checks=len(checks),
        checks=items,
    )
