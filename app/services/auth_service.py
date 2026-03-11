"""Serviço de autenticação."""

from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.database.models.user import User

settings = get_settings()


class AuthService:
    """Serviço de autenticação e registro."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, email: str, password: str) -> User | None:
        """Registra novo usuário. Retorna None se email já existe."""
        stmt = select(User).where(User.email == email.lower())
        existing = (await self.db.execute(stmt)).scalar_one_or_none()
        if existing:
            return None

        user = User(
            email=email.lower(),
            hashed_password=get_password_hash(password),
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def authenticate(self, email: str, password: str) -> User | None:
        """Autentica usuário. Retorna User ou None."""
        stmt = select(User).where(User.email == email.lower())
        user = (await self.db.execute(stmt)).scalar_one_or_none()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    def create_token(self, user: User) -> str:
        """Cria token JWT para o usuário."""
        return create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        )
