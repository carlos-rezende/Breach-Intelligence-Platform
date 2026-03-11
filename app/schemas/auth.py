"""Schemas para autenticação."""

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Registro de usuário."""

    email: EmailStr = Field(..., description="Email do usuário")
    password: str = Field(..., min_length=8, description="Senha (mínimo 8 caracteres)")


class UserLogin(BaseModel):
    """Login de usuário."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Resposta com token JWT."""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Resposta com dados do usuário."""

    id: int
    email: str
