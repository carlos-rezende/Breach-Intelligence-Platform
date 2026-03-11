"""Cliente Redis para cache."""


from redis.asyncio import Redis

from app.config import get_settings

_redis: Redis | None = None


async def init_redis() -> Redis | None:
    """Inicializa conexão Redis."""
    global _redis
    settings = get_settings()
    try:
        _redis = Redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        await _redis.ping()
        return _redis
    except Exception:
        _redis = None
        return None


async def close_redis() -> None:
    """Fecha conexão Redis."""
    global _redis
    if _redis:
        await _redis.close()
        _redis = None


def get_redis() -> Redis | None:
    """Retorna cliente Redis."""
    return _redis


async def check_redis_connection() -> bool:
    """Verifica conexão Redis."""
    client = get_redis()
    if not client:
        return False
    try:
        await client.ping()
        return True
    except Exception:
        return False
