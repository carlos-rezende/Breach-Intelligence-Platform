"""Dependencies da API."""


from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import decode_access_token
from app.database import get_db
from app.database.models.api_key import ApiKey, hash_api_key
from app.database.models.user import User

security = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Retorna usuário se autenticado (JWT ou API key), None caso contrário."""
    if not credentials:
        return None
    token = credentials.credentials
    if token.startswith("bip_"):
        key_hash = hash_api_key(token)
        stmt = select(ApiKey).where(ApiKey.key_hash == key_hash).options(selectinload(ApiKey.user))
        api_key = (await db.execute(stmt)).scalar_one_or_none()
        return api_key.user if api_key else None
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None
    email = payload["sub"]
    stmt = select(User).where(User.email == email)
    user = (await db.execute(stmt)).scalar_one_or_none()
    return user


async def get_current_user(
    user: User | None = Depends(get_current_user_optional),
) -> User:
    """Requer autenticação. Retorna usuário ou 401."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação necessária",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
