"""Configurações centralizadas da aplicação."""

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


def _to_async_pg_url(url: str) -> str:
    """Converte URL PostgreSQL para driver asyncpg."""
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url[12:]
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url[10:]
    return url


def _to_sync_pg_url(url: str) -> str:
    """Converte URL PostgreSQL para formato síncrono."""
    return url.replace("postgresql+asyncpg://", "postgresql://")


class Settings(BaseSettings):
    """Configurações carregadas de variáveis de ambiente."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "Breach Intelligence Platform"
    debug: bool = False
    testing: bool = False
    use_sqlite: bool = False

    secret_key: str = "change-me-in-production-use-openssl-rand-hex-32"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "breach_user"
    postgres_password: str = "breach_password"
    postgres_db: str = "breach_intelligence"

    @property
    def database_url(self) -> str:
        """URL de conexão síncrona."""
        if self.testing:
            return "sqlite:///./test.db"
        if self.use_sqlite:
            return "sqlite:///./breach_dev.db"
        env_url = os.environ.get("DATABASE_URL")
        if env_url:
            return _to_sync_pg_url(env_url)
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def async_database_url(self) -> str:
        """URL de conexão assíncrona (postgresql+asyncpg para produção)."""
        if self.testing:
            return "sqlite+aiosqlite:///./test.db"
        if self.use_sqlite:
            return "sqlite+aiosqlite:///./breach_dev.db"
        env_url = os.environ.get("DATABASE_URL")
        if env_url:
            return _to_async_pg_url(env_url)
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None
    cache_ttl_seconds: int = 86400

    @property
    def redis_url(self) -> str:
        """URL de conexão Redis (usa REDIS_URL se definido, ex: Render)."""
        env_url = os.environ.get("REDIS_URL")
        if env_url:
            return env_url
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"

    celery_broker_url: str | None = None

    @property
    def celery_broker(self) -> str:
        """URL do broker Celery."""
        return self.celery_broker_url or self.redis_url

    hibp_api_key: str = ""
    hibp_base_url: str = "https://haveibeenpwned.com/api/v3"
    hibp_user_agent: str = "BreachIntelligencePlatform/1.0"

    rate_limit_requests: int = 60
    rate_limit_period: int = 60


@lru_cache
def get_settings() -> Settings:
    """Retorna instância cacheada das configurações."""
    return Settings()
