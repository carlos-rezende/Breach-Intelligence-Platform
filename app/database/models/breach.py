"""Modelos de verificação de vazamentos."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base

if TYPE_CHECKING:
    from app.database.models.breach import BreachRecord


class BreachCheck(Base):
    """Registro de consulta de vazamento."""

    __tablename__ = "breach_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    breach_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    providers_used: Mapped[str] = mapped_column(String(500), nullable=True)
    risk_score: Mapped[str] = mapped_column(String(20), nullable=False, default="safe")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    breaches: Mapped[list["BreachRecord"]] = relationship(
        "BreachRecord",
        back_populates="breach_check",
        cascade="all, delete-orphan",
    )


class BreachRecord(Base):
    """Registro individual de vazamento."""

    __tablename__ = "breach_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    breach_check_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("breach_checks.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=True)

    breach_check: Mapped["BreachCheck"] = relationship(
        "BreachCheck", back_populates="breaches"
    )
