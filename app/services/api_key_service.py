"""Serviço de API Keys."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.api_key import ApiKey, generate_api_key, hash_api_key
from app.database.models.user import User


class ApiKeyService:
    """Gerenciamento de API keys."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user: User, name: str) -> tuple[ApiKey, str]:
        """Cria nova API key. Retorna (ApiKey, plain_key)."""
        key = generate_api_key()
        key_hash = hash_api_key(key)
        api_key = ApiKey(user_id=user.id, key_hash=key_hash, name=name)
        self.db.add(api_key)
        await self.db.flush()
        await self.db.refresh(api_key)
        return api_key, key

    async def list_by_user(self, user: User) -> list[ApiKey]:
        """Lista API keys do usuário (sem a chave)."""
        stmt = select(ApiKey).where(ApiKey.user_id == user.id).order_by(ApiKey.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, user: User, key_id: int) -> bool:
        """Remove API key se pertencer ao usuário. Retorna True se removido."""
        stmt = select(ApiKey).where(ApiKey.id == key_id, ApiKey.user_id == user.id)
        api_key = (await self.db.execute(stmt)).scalar_one_or_none()
        if not api_key:
            return False
        await self.db.delete(api_key)
        await self.db.flush()
        return True
