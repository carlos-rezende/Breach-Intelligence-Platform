"""Configuração de rate limiting."""

from slowapi import Limiter
from slowapi.util import get_remote_address


def get_identifier(request) -> str:
    """Identificador para rate limit: IP ou user_id se autenticado."""
    return get_remote_address(request)


limiter = Limiter(key_func=get_identifier)
