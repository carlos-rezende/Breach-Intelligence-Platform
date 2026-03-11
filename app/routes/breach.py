"""Rotas de verificação de vazamentos."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.dependencies import get_current_user_optional
from app.core.rate_limit import limiter
from app.database import get_db
from app.database.models.user import User
from app.database.models.webhook import Webhook
from app.schemas.breach import BreachCheckRequest, BreachCheckResponse
from app.services.breach_service import BreachService
from app.services.webhook_service import WebhookService

router = APIRouter(prefix="/breach-check", tags=["Breach Check"])
settings = get_settings()


@router.post("", response_model=BreachCheckResponse)
@limiter.limit(f"{settings.rate_limit_requests}/minute")
async def check_breach(
    request: Request,
    body: BreachCheckRequest,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    """
    Verifica se um email apareceu em vazamentos de dados.

    Fluxo: validar → cache → providers → processar → score → salvar → retornar.
    Se autenticado e com webhooks, notifica após a verificação.
    """
    service = BreachService(db)
    result = await service.check_email(body.email)
    if user:
        stmt = select(Webhook).where(Webhook.user_id == user.id)
        webhooks = list((await db.execute(stmt)).scalars().all())
        if webhooks:
            payload = result.model_dump(mode="json")
            await WebhookService.notify_webhooks(webhooks, payload)
    return result


