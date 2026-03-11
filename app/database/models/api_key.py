"""Modelo de API Key."""

import hashlib
import secrets
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base

if TYPE_CHECKING:
    from app.database.models.user import User


def generate_api_key() -> str:
    """Gera API key no formato bip_xxxxxxxx."""
    return f"bip_{secrets.token_hex(24)}"


def hash_api_key(key: str) -> str:
    """Retorna hash SHA-256 da API key."""
    return hashlib.sha256(key.encode()).hexdigest()


class ApiKey(Base):
    """API Key para autenticação programática."""

    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    key_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="api_keys")
