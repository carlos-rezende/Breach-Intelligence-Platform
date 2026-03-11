"""Rotas de verificação de senha."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.dependencies import get_current_user_optional
from app.core.rate_limit import limiter
from app.database import get_db
from app.database.models.password_check import PasswordCheck
from app.database.models.user import User
from app.schemas.password import PasswordCheckRequest, PasswordCheckResponse
from app.services.password_service import check_password

router = APIRouter(prefix="/password-check", tags=["Password Check"])
settings = get_settings()


@router.post("", response_model=PasswordCheckResponse)
@limiter.limit(f"{settings.rate_limit_requests}/minute")
async def check_password_breach(
    request: Request,
    body: PasswordCheckRequest,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    """
    Verifica se uma senha apareceu em vazamentos de dados.

    Usa a API Pwned Passwords (k-anonymity) - a senha nunca é enviada,
    apenas um hash parcial. Não requer API key.
    Se autenticado, salva no histórico.
    """
    pwned, count = await check_password(body.password)
    checked_at = datetime.now(UTC)

    if user:
        record = PasswordCheck(user_id=user.id, pwned=pwned, count=count)
        db.add(record)
        await db.flush()

    return PasswordCheckResponse(
        pwned=pwned,
        count=count,
        checked_at=checked_at,
    )
