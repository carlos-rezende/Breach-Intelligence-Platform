"""Serviço de verificação de vazamentos."""

import json
from datetime import UTC, datetime

from redis.asyncio import Redis
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.cache.redis_client import get_redis
from app.config import get_settings
from app.database.models.breach import BreachCheck, BreachRecord
from app.providers.base_provider import BreachInfo as ProviderBreachInfo
from app.providers.demo_provider import DemoProvider
from app.providers.hibp_provider import HIBPProvider
from app.providers.leakcheck_provider import LeakCheckProvider
from app.schemas.breach import BreachCheckResponse, BreachInfo
from app.utils.risk_score import calculate_risk_score

settings = get_settings()


class BreachService:
    """Orquestra verificação de vazamentos em múltiplos providers."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.redis: Redis | None = get_redis()
        self.providers = [
            DemoProvider(),
            HIBPProvider(),
            LeakCheckProvider(),
        ]

    def _cache_key(self, email: str) -> str:
        return f"breach_check:{email.lower()}"

    async def _get_from_cache(self, email: str) -> BreachCheckResponse | None:
        """Obtém resultado do cache."""
        if not self.redis:
            return None
        try:
            cached = await self.redis.get(self._cache_key(email))
            if cached:
                data = json.loads(cached)
                data["checked_at"] = datetime.fromisoformat(data["checked_at"])
                return BreachCheckResponse(**data)
        except Exception:
            pass
        return None

    async def _set_cache(self, email: str, result: BreachCheckResponse) -> None:
        """Salva resultado no cache (24h)."""
        if not self.redis:
            return
        try:
            data = result.model_dump(mode="json")
            await self.redis.setex(
                self._cache_key(email),
                settings.cache_ttl_seconds,
                json.dumps(data, default=str),
            )
        except Exception:
            pass

    async def check_email(self, email: str) -> BreachCheckResponse:
        """
        Fluxo completo:
        1. Validar email
        2. Verificar cache Redis
        3. Consultar providers disponíveis
        4. Processar e consolidar dados
        5. Calcular score de risco
        6. Salvar no banco
        7. Retornar resultado
        """
        email_lower = email.lower().strip()

        cached = await self._get_from_cache(email_lower)
        if cached:
            return cached

        all_breaches = []
        providers_used = []

        for provider in self.providers:
            if provider.is_available():
                result = await provider.check_email(email_lower)
                providers_used.append(provider.name)
                if result.success and result.breaches:
                    for b in result.breaches:
                        all_breaches.append(b)

        seen = set()
        unique_breaches: list[ProviderBreachInfo] = []
        for b in all_breaches:
            if b.name not in seen:
                seen.add(b.name)
                unique_breaches.append(b)

        breach_count = len(unique_breaches)
        risk_score = calculate_risk_score(breach_count)
        checked_at = datetime.now(UTC)

        breach_check = BreachCheck(
            email=email_lower,
            breach_count=breach_count,
            providers_used=",".join(providers_used) if providers_used else None,
            risk_score=risk_score,
        )
        self.db.add(breach_check)
        await self.db.flush()

        for info in unique_breaches:
            record = BreachRecord(
                breach_check_id=breach_check.id,
                name=info.name,
                year=info.year,
                provider=info.provider,
            )
            self.db.add(record)

        await self.db.flush()

        result = BreachCheckResponse(
            email=email_lower,
            breached=breach_count > 0,
            breach_count=breach_count,
            breaches=[BreachInfo(name=b.name, year=b.year) for b in unique_breaches],
            risk_score=risk_score,
            checked_at=checked_at,
        )

        await self._set_cache(email_lower, result)

        return result

    async def get_history(self, email: str) -> list[BreachCheck]:
        """Retorna histórico de consultas."""
        stmt = (
            select(BreachCheck)
            .where(BreachCheck.email == email.lower())
            .options(selectinload(BreachCheck.breaches))
            .order_by(BreachCheck.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_stats(self) -> dict:
        """Retorna estatísticas da plataforma."""
        total_checks = int(
            (await self.db.execute(select(func.count(BreachCheck.id)))).scalar() or 0
        )
        emails_analyzed = int(
            (
                await self.db.execute(
                    select(func.count(func.distinct(BreachCheck.email)))
                )
            ).scalar()
            or 0
        )
        breaches_detected = int(
            (await self.db.execute(select(func.sum(BreachCheck.breach_count)))).scalar()
            or 0
        )

        provider_counts: dict[str, int] = {}
        stmt = select(BreachCheck.providers_used).where(
            BreachCheck.providers_used.isnot(None)
        )
        rows = (await self.db.execute(stmt)).scalars().all()
        for row in rows:
            if row[0]:
                for p in row[0].split(","):
                    p = p.strip()
                    if p:
                        provider_counts[p] = provider_counts.get(p, 0) + 1

        checks_by_provider = [
            {"provider": p, "checks_count": c}
            for p, c in sorted(provider_counts.items(), key=lambda x: -x[1])
        ]

        return {
            "total_checks": total_checks,
            "emails_analyzed": emails_analyzed,
            "breaches_detected": breaches_detected,
            "checks_by_provider": checks_by_provider,
        }
