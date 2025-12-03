"""
Route per autenticazione
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from supabase import Client
from backend.database import get_supabase
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["autenticazione"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: str  # "cliente" o "negoziante"
    full_name: Optional[str] = None
    phone: Optional[str] = None


class AuthResponse(BaseModel):
    message: str
    access_token: Optional[str] = None
    user: Optional[dict] = None


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, supabase: Client = Depends(get_supabase)):
    """Endpoint per login utente"""
    try:
        # Autentica con Supabase Auth
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenziali non valide"
            )
        
        # Ottieni informazioni utente dalla tabella users
        user_data = supabase.table("users").select("*").eq("id", response.user.id).execute()
        
        return AuthResponse(
            message="Login avvenuto con successo",
            access_token=response.session.access_token if response.session else None,
            user={
                "id": response.user.id,
                "email": response.user.email,
                "role": user_data.data[0]["role"] if user_data.data else None,
                "full_name": user_data.data[0].get("full_name") if user_data.data else None
            } if user_data.data else None
        )
    except Exception as e:
        logger.error(f"Errore login: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Errore durante il login: {str(e)}"
        )


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest, supabase: Client = Depends(get_supabase)):
    """Endpoint per registrazione nuovo utente"""
    try:
        # Valida ruolo
        if request.role not in ["cliente", "negoziante"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ruolo deve essere 'cliente' o 'negoziante'"
            )
        
        # Registra utente con Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Errore durante la registrazione"
            )
        
        # Crea record nella tabella users
        user_data = {
            "id": auth_response.user.id,
            "email": request.email,
            "role": request.role,
            "full_name": request.full_name,
            "phone": request.phone
        }
        
        result = supabase.table("users").insert(user_data).execute()
        
        return AuthResponse(
            message="Registrazione avvenuta con successo. Controlla la tua email per la verifica.",
            access_token=auth_response.session.access_token if auth_response.session else None,
            user={
                "id": auth_response.user.id,
                "email": auth_response.user.email,
                "role": request.role,
                "full_name": request.full_name
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore registrazione: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Errore durante la registrazione: {str(e)}"
        )


@router.post("/logout")
async def logout(supabase: Client = Depends(get_supabase)):
    """Endpoint per logout utente"""
    try:
        supabase.auth.sign_out()
        return {"message": "Logout avvenuto con successo"}
    except Exception as e:
        logger.error(f"Errore logout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante il logout: {str(e)}"
        )

