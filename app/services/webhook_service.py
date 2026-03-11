"""Serviço de Webhooks."""

import hashlib
import hmac
import secrets
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User
from app.database.models.webhook import Webhook


class WebhookService:
    """Gerenciamento e disparo de webhooks."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user: User, url: str) -> tuple[Webhook, str]:
        """Cria webhook. Retorna (Webhook, secret)."""
        secret = secrets.token_hex(32)
        webhook = Webhook(user_id=user.id, url=url, secret=secret)
        self.db.add(webhook)
        await self.db.flush()
        await self.db.refresh(webhook)
        return webhook, secret

    async def list_by_user(self, user: User) -> list[Webhook]:
        """Lista webhooks do usuário."""
        stmt = select(Webhook).where(Webhook.user_id == user.id).order_by(Webhook.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, user: User, webhook_id: int) -> bool:
        """Remove webhook se pertencer ao usuário."""
        stmt = select(Webhook).where(Webhook.id == webhook_id, Webhook.user_id == user.id)
        webhook = (await self.db.execute(stmt)).scalar_one_or_none()
        if not webhook:
            return False
        await self.db.delete(webhook)
        await self.db.flush()
        return True

    @staticmethod
    def _sign_payload(payload: str, secret: str) -> str:
        """Gera assinatura HMAC-SHA256 do payload."""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()

    @staticmethod
    async def notify_webhooks(webhooks: list[Webhook], payload: dict[str, Any]) -> None:
        """Dispara payload para lista de webhooks (fire-and-forget)."""
        import json
        for webhook in webhooks:
            try:
                body = json.dumps(payload, default=str)
                signature = WebhookService._sign_payload(body, webhook.secret)
                async with httpx.AsyncClient(timeout=5.0) as client:
                    await client.post(
                        webhook.url,
                        content=body,
                        headers={
                            "Content-Type": "application/json",
                            "X-Webhook-Signature": f"sha256={signature}",
                        },
                    )
            except Exception:
                pass
