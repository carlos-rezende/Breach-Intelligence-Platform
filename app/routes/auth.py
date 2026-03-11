"""Rotas de autenticação."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.rate_limit import limiter
from app.database import get_db
from app.schemas.auth import TokenResponse, UserLogin, UserRegister, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()


@router.post("/register", response_model=UserResponse)
@limiter.limit("10/minute")
async def register(
    request: Request,
    body: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    """Registra novo usuário."""
    service = AuthService(db)
    user = await service.register(body.email, body.password)
    if not user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    return UserResponse(id=user.id, email=user.email)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("20/minute")
async def login(
    request: Request,
    body: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Autentica e retorna token JWT."""
    service = AuthService(db)
    user = await service.authenticate(body.email, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    token = service.create_token(user)
    return TokenResponse(access_token=token)
