"""
Route per autenticazione
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional

router = APIRouter(prefix="/api/auth", tags=["autenticazione"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: str  # "cliente" o "negoziante"


@router.post("/login")
async def login(request: LoginRequest):
    """Endpoint per login utente"""
    # TODO: Implementare autenticazione con Supabase Auth
    return {"message": "Login endpoint - da implementare", "email": request.email}


@router.post("/register")
async def register(request: RegisterRequest):
    """Endpoint per registrazione nuovo utente"""
    # TODO: Implementare registrazione con Supabase Auth
    return {
        "message": "Register endpoint - da implementare",
        "email": request.email,
        "role": request.role
    }


@router.post("/logout")
async def logout():
    """Endpoint per logout utente"""
    # TODO: Implementare logout
    return {"message": "Logout endpoint - da implementare"}

