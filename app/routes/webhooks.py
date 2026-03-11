"""Rotas de Webhooks."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.dependencies import get_current_user
from app.core.rate_limit import limiter
from app.database import get_db
from app.database.models.user import User
from app.schemas.webhook import WebhookCreate, WebhookListItem, WebhookResponse
from app.services.webhook_service import WebhookService

router = APIRouter(prefix="/auth/webhooks", tags=["Webhooks"])
settings = get_settings()


@router.post("", response_model=WebhookResponse)
@limiter.limit("5/minute")
async def create_webhook(
    request: Request,
    body: WebhookCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Cria webhook. O secret é exibido apenas uma vez."""
    service = WebhookService(db)
    webhook, secret = await service.create(user, body.url)
    return WebhookResponse(
        id=webhook.id,
        url=webhook.url,
        secret=secret,
        created_at=webhook.created_at,
    )


@router.get("", response_model=list[WebhookListItem])
async def list_webhooks(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Lista webhooks do usuário."""
    service = WebhookService(db)
    webhooks = await service.list_by_user(user)
    return [WebhookListItem(id=w.id, url=w.url, created_at=w.created_at) for w in webhooks]


@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Remove um webhook."""
    service = WebhookService(db)
    if not await service.delete(user, webhook_id):
        raise HTTPException(status_code=404, detail="Webhook não encontrado")
    return {"ok": True}
