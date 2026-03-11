"""Rotas de API Keys."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.dependencies import get_current_user
from app.core.rate_limit import limiter
from app.database import get_db
from app.database.models.user import User
from app.schemas.api_key import ApiKeyCreate, ApiKeyListItem, ApiKeyResponse
from app.services.api_key_service import ApiKeyService

router = APIRouter(prefix="/auth/api-keys", tags=["API Keys"])
settings = get_settings()


@router.post("", response_model=ApiKeyResponse)
@limiter.limit("5/minute")
async def create_api_key(
    request: Request,
    body: ApiKeyCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Cria nova API key. A chave é exibida apenas uma vez."""
    service = ApiKeyService(db)
    api_key, plain_key = await service.create(user, body.name)
    return ApiKeyResponse(
        id=api_key.id,
        name=api_key.name,
        key=plain_key,
        created_at=api_key.created_at,
    )


@router.get("", response_model=list[ApiKeyListItem])
async def list_api_keys(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Lista API keys do usuário (sem exibir as chaves)."""
    service = ApiKeyService(db)
    keys = await service.list_by_user(user)
    return [ApiKeyListItem(id=k.id, name=k.name, created_at=k.created_at) for k in keys]


@router.delete("/{key_id}")
async def delete_api_key(
    key_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Remove uma API key."""
    service = ApiKeyService(db)
    if not await service.delete(user, key_id):
        raise HTTPException(status_code=404, detail="API key não encontrada")
    return {"ok": True}
