"""Modelo de usuário."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base

if TYPE_CHECKING:
    from app.database.models.api_key import ApiKey
    from app.database.models.password_check import PasswordCheck
    from app.database.models.webhook import Webhook


class User(Base):
    """Usuário da plataforma."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    password_checks: Mapped[list["PasswordCheck"]] = relationship(
        "PasswordCheck", back_populates="user", cascade="all, delete-orphan"
    )
    api_keys: Mapped[list["ApiKey"]] = relationship(
        "ApiKey", back_populates="user", cascade="all, delete-orphan"
    )
    webhooks: Mapped[list["Webhook"]] = relationship(
        "Webhook", back_populates="user", cascade="all, delete-orphan"
    )
