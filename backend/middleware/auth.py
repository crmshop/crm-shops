"""
Middleware per autenticazione JWT
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from backend.database import get_supabase
from jose import JWTError, jwt
from backend.config import settings
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase)
):
    """Ottiene l'utente corrente dal token JWT"""
    token = credentials.credentials
    
    try:
        # Verifica il token con Supabase
        user = supabase.auth.get_user(token)
        
        if not user.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token non valido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Ottieni informazioni aggiuntive dalla tabella users
        user_data = supabase.table("users").select("*").eq("id", user.user.id).execute()
        
        if not user_data.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utente non trovato",
            )
        
        return {
            "id": user.user.id,
            "email": user.user.email,
            "role": user_data.data[0]["role"],
            "full_name": user_data.data[0].get("full_name"),
            "token": token
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token non valido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Errore autenticazione: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Errore durante l'autenticazione",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_role(required_role: str):
    """Dependency per richiedere un ruolo specifico"""
    async def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accesso negato. Richiesto ruolo: {required_role}"
            )
        return current_user
    return role_checker




