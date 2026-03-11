"""Endpoint de métricas Prometheus."""

from fastapi import APIRouter, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)

router = APIRouter(prefix="/metrics", tags=["Metrics"])

REQUEST_COUNT = Counter(
    "breach_api_requests_total",
    "Total de requisições",
    ["method", "endpoint"],
)
REQUEST_LATENCY = Histogram(
    "breach_api_request_duration_seconds",
    "Latência das requisições",
    ["method", "endpoint"],
)
BREACH_CHECKS_COUNT = Counter(
    "breach_api_checks_total",
    "Total de verificações de vazamento",
)


@router.get("")
async def metrics():
    """Retorna métricas no formato Prometheus."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
