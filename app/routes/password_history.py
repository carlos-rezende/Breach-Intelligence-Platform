"""Rotas de histórico de verificações de senha."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.database.models.password_check import PasswordCheck
from app.database.models.user import User
from app.schemas.password import PasswordCheckHistoryItem, PasswordCheckHistoryResponse

router = APIRouter(prefix="/password-history", tags=["Password History"])


@router.get("", response_model=PasswordCheckHistoryResponse)
async def get_password_history(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Retorna histórico de verificações de senha do usuário (sem dados da senha)."""
    stmt = (
        select(PasswordCheck)
        .where(PasswordCheck.user_id == user.id)
        .order_by(PasswordCheck.created_at.desc())
        .limit(100)
    )
    result = await db.execute(stmt)
    checks = list(result.scalars().all())
    return PasswordCheckHistoryResponse(
        total=len(checks),
        items=[
            PasswordCheckHistoryItem(
                pwned=c.pwned,
                count=c.count,
                checked_at=c.created_at,
            )
            for c in checks
        ],
    )
