"""Breach Intelligence Platform - Aplicação principal."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.cache.redis_client import check_redis_connection, close_redis, init_redis
from app.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.core.rate_limit import limiter
from app.database import check_db_connection, init_db
from app.routes.api_keys import router as api_keys_router
from app.routes.auth import router as auth_router
from app.routes.breach import router as breach_router
from app.routes.history import router as history_router
from app.routes.metrics import router as metrics_router
from app.routes.password import router as password_router
from app.routes.password_history import router as password_history_router
from app.routes.stats import router as stats_router
from app.routes.webhooks import router as webhooks_router

setup_logging()
logger = get_logger("main")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida da aplicação (resiliente a falhas de DB/Redis)."""
    logger.info("application_starting", app=settings.app_name)
    try:
        await init_db()
        logger.info("database_initialized")
    except Exception as e:
        logger.error("database_init_failed", error=str(e), exc_info=True)
    try:
        await init_redis()
        logger.info("redis_initialized")
    except Exception as e:
        logger.error("redis_init_failed", error=str(e), exc_info=True)
    yield
    await close_redis()
    logger.info("application_shutting_down")


def create_app() -> FastAPI:
    """Cria aplicação FastAPI."""
    app = FastAPI(
        title=settings.app_name,
        description="API de threat intelligence para verificação de vazamentos de email",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(breach_router)
    app.include_router(password_router)
    app.include_router(password_history_router)
    app.include_router(history_router)
    app.include_router(stats_router)
    app.include_router(auth_router)
    app.include_router(api_keys_router)
    app.include_router(webhooks_router)
    app.include_router(metrics_router)

    static_dir = Path(__file__).resolve().parent.parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

        @app.get("/")
        async def root():
            from fastapi.responses import FileResponse
            return FileResponse(static_dir / "index.html")

    @app.get("/health")
    async def health_check():
        """Health check: API, PostgreSQL, Redis, Celery workers."""
        db_ok = await check_db_connection()
        redis_ok = await check_redis_connection()
        celery_ok = redis_ok

        status_val = "healthy" if (db_ok and redis_ok) else "unhealthy"
        return {
            "status": status_val,
            "api": "ok",
            "database": "ok" if db_ok else "error",
            "redis": "ok" if redis_ok else "error",
            "workers": "ok" if celery_ok else "error",
        }

    return app


app = create_app()
