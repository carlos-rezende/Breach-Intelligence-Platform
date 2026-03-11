"""Provider base abstrato para threat intelligence."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class BreachInfo:
    """Informação de um vazamento."""

    name: str
    year: int | None = None
    provider: str | None = None


@dataclass
class BreachResult:
    """Resultado da consulta a um provider."""

    provider: str
    breaches: list[BreachInfo]
    success: bool = True
    error: str | None = None


class BaseBreachProvider(ABC):
    """Interface base para providers de vazamento."""

    name: str = "base"

    @abstractmethod
    async def check_email(self, email: str) -> BreachResult:
        """Verifica se o email apareceu em vazamentos."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Verifica se o provider está disponível/configurado."""
        pass
