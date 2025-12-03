"""
Route per gestione negozi
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from supabase import Client
from backend.database import get_supabase
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/shops", tags=["negozi"])


class ShopCreate(BaseModel):
    owner_id: UUID
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None


class ShopUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None


@router.get("/")
async def list_shops(
    owner_id: Optional[UUID] = None,
    supabase: Client = Depends(get_supabase)
):
    """Lista negozi con filtri opzionali"""
    try:
        query = supabase.table("shops").select("*")
        
        if owner_id:
            query = query.eq("owner_id", str(owner_id))
        
        result = query.execute()
        return {
            "shops": result.data,
            "count": len(result.data)
        }
    except Exception as e:
        logger.error(f"Errore lista negozi: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante il recupero negozi: {str(e)}"
        )


@router.get("/{shop_id}")
async def get_shop(shop_id: UUID, supabase: Client = Depends(get_supabase)):
    """Ottieni dettagli di un negozio"""
    try:
        result = supabase.table("shops").select("*").eq("id", str(shop_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Negozio non trovato"
            )
        
        return {"shop": result.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore recupero negozio: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante il recupero negozio: {str(e)}"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_shop(
    shop: ShopCreate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Crea un nuovo negozio"""
    try:
        # Solo negozianti possono creare negozi
        if current_user["role"] != "negoziante":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo i negozianti possono creare negozi"
            )
        
        shop_data = shop.dict()
        # Usa l'ID dell'utente corrente come owner
        shop_data["owner_id"] = current_user["id"]
        
        result = supabase.table("shops").insert(shop_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Errore durante la creazione del negozio"
            )
        
        return {
            "message": "Negozio creato con successo",
            "shop": result.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore creazione negozio: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Errore durante la creazione del negozio: {str(e)}"
        )


@router.put("/{shop_id}")
async def update_shop(shop_id: UUID, shop: ShopUpdate, supabase: Client = Depends(get_supabase)):
    """Aggiorna un negozio"""
    try:
        updates = shop.dict(exclude_unset=True)
        
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nessun campo da aggiornare"
            )
        
        result = supabase.table("shops").update(updates).eq("id", str(shop_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Negozio non trovato"
            )
        
        return {
            "message": "Negozio aggiornato con successo",
            "shop": result.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore aggiornamento negozio: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante l'aggiornamento del negozio: {str(e)}"
        )


@router.delete("/{shop_id}")
async def delete_shop(shop_id: UUID, supabase: Client = Depends(get_supabase)):
    """Elimina un negozio"""
    try:
        result = supabase.table("shops").delete().eq("id", str(shop_id)).execute()
        
        return {
            "message": "Negozio eliminato con successo",
            "shop_id": str(shop_id)
        }
    except Exception as e:
        logger.error(f"Errore eliminazione negozio: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante l'eliminazione del negozio: {str(e)}"
        )

