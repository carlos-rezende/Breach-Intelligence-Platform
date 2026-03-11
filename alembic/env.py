"""Alembic environment configuration."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.database.session import Base
import app.database.models  # noqa: F401 - load all models for migrations
from app.config import get_settings

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
settings = get_settings()
db_url = settings.database_url.replace("+aiosqlite", "").replace("+asyncpg", "")
config.set_main_option("sqlalchemy.url", db_url)
async_db_url = settings.async_database_url
use_sqlite = settings.testing or settings.use_sqlite


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = async_db_url
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online_sync() -> None:
    """Run migrations with sync engine (SQLite ou quando async falha)."""
    from sqlalchemy import create_engine
    sync_url = db_url
    if "sqlite" in sync_url:
        engine = create_engine(sync_url, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(sync_url)
    with engine.connect() as connection:
        do_run_migrations(connection)
    engine.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    if use_sqlite:
        run_migrations_online_sync()
    else:
        asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
