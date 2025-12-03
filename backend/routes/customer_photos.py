"""
Route per gestione foto clienti
"""
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from supabase import Client
from backend.database import get_supabase
from backend.middleware.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/customer-photos", tags=["foto-clienti"])


class CustomerPhotoCreate(BaseModel):
    shop_id: Optional[UUID] = None
    angle: Optional[str] = None  # 'frontale', 'laterale', 'posteriore'
    consent_given: bool = False


@router.get("/")
async def list_customer_photos(
    user_id: Optional[UUID] = None,
    shop_id: Optional[UUID] = None,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Lista foto clienti con filtri opzionali"""
    try:
        query = supabase.table("customer_photos").select("*")
        
        # Gli utenti possono vedere solo le proprie foto (tranne negozianti)
        if current_user["role"] == "cliente":
            query = query.eq("user_id", current_user["id"])
        elif user_id:
            query = query.eq("user_id", str(user_id))
        
        if shop_id:
            query = query.eq("shop_id", str(shop_id))
        
        result = query.execute()
        return {
            "photos": result.data,
            "count": len(result.data)
        }
    except Exception as e:
        logger.error(f"Errore lista foto: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante il recupero foto: {str(e)}"
        )


@router.get("/{photo_id}")
async def get_customer_photo(
    photo_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Ottieni dettagli di una foto"""
    try:
        result = supabase.table("customer_photos").select("*").eq("id", str(photo_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Foto non trovata"
            )
        
        photo = result.data[0]
        
        # Verifica permessi: i clienti possono vedere solo le proprie foto
        if current_user["role"] == "cliente" and photo["user_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accesso negato"
            )
        
        return {"photo": photo}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore recupero foto: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante il recupero foto: {str(e)}"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_customer_photo(
    file: UploadFile = File(...),
    shop_id: Optional[UUID] = None,
    angle: Optional[str] = None,
    consent_given: bool = False,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Carica una foto cliente su Supabase Storage"""
    try:
        # Leggi il file
        file_content = await file.read()
        file_name = f"{current_user['id']}/{file.filename}"
        
        # Carica su Supabase Storage
        bucket_name = "customer-photos"
        
        # Verifica che il bucket esista (da configurare manualmente su Supabase)
        storage_response = supabase.storage.from_(bucket_name).upload(
            file_name,
            file_content,
            file_options={"content-type": file.content_type or "image/jpeg"}
        )
        
        # Ottieni URL pubblico
        public_url = supabase.storage.from_(bucket_name).get_public_url(file_name)
        
        # Salva metadati nel database
        photo_data = {
            "user_id": current_user["id"],
            "image_url": public_url,
            "angle": angle,
            "consent_given": consent_given
        }
        
        if shop_id:
            photo_data["shop_id"] = str(shop_id)
        
        result = supabase.table("customer_photos").insert(photo_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Errore durante il salvataggio della foto"
            )
        
        return {
            "message": "Foto caricata con successo",
            "photo": result.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore upload foto: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Errore durante il caricamento della foto: {str(e)}"
        )


@router.delete("/{photo_id}")
async def delete_customer_photo(
    photo_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Elimina una foto cliente"""
    try:
        # Verifica permessi
        photo_result = supabase.table("customer_photos").select("*").eq("id", str(photo_id)).execute()
        
        if not photo_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Foto non trovata"
            )
        
        photo = photo_result.data[0]
        
        # I clienti possono eliminare solo le proprie foto
        if current_user["role"] == "cliente" and photo["user_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accesso negato"
            )
        
        # Elimina dal database (il file su Storage può rimanere per ora)
        result = supabase.table("customer_photos").delete().eq("id", str(photo_id)).execute()
        
        return {
            "message": "Foto eliminata con successo",
            "photo_id": str(photo_id)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore eliminazione foto: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante l'eliminazione della foto: {str(e)}"
        )



