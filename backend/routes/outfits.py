"""
Route per gestione outfit
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from supabase import Client
from backend.database import get_supabase
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/outfits", tags=["outfit"])


class OutfitCreate(BaseModel):
    user_id: UUID
    shop_id: UUID
    name: Optional[str] = None
    product_ids: List[UUID]


class OutfitResponse(BaseModel):
    id: UUID
    user_id: UUID
    shop_id: UUID
    name: Optional[str]
    product_ids: List[UUID]
    created_at: str


@router.get("/")
async def list_outfits(
    user_id: Optional[UUID] = None,
    shop_id: Optional[UUID] = None,
    supabase: Client = Depends(get_supabase)
):
    """Lista outfit con filtri opzionali"""
    try:
        query = supabase.table("outfits").select("*, outfit_products(product_id)")
        
        if user_id:
            query = query.eq("user_id", str(user_id))
        if shop_id:
            query = query.eq("shop_id", str(shop_id))
        
        result = query.execute()
        
        # Formatta i risultati per includere product_ids
        outfits = []
        for outfit in result.data:
            outfit_data = {**outfit}
            outfit_data["product_ids"] = [
                op["product_id"] for op in outfit.get("outfit_products", [])
            ]
            if "outfit_products" in outfit_data:
                del outfit_data["outfit_products"]
            outfits.append(outfit_data)
        
        return {
            "outfits": outfits,
            "count": len(outfits)
        }
    except Exception as e:
        logger.error(f"Errore lista outfit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante il recupero outfit: {str(e)}"
        )


@router.get("/{outfit_id}")
async def get_outfit(outfit_id: UUID, supabase: Client = Depends(get_supabase)):
    """Ottieni dettagli di un outfit"""
    try:
        result = supabase.table("outfits").select("*, outfit_products(product_id)").eq("id", str(outfit_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Outfit non trovato"
            )
        
        outfit = result.data[0]
        outfit["product_ids"] = [
            op["product_id"] for op in outfit.get("outfit_products", [])
        ]
        if "outfit_products" in outfit:
            del outfit["outfit_products"]
        
        return {"outfit": outfit}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore recupero outfit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante il recupero outfit: {str(e)}"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_outfit(outfit: OutfitCreate, supabase: Client = Depends(get_supabase)):
    """Crea un nuovo outfit"""
    try:
        # Crea l'outfit
        outfit_data = {
            "user_id": str(outfit.user_id),
            "shop_id": str(outfit.shop_id),
            "name": outfit.name
        }
        
        result = supabase.table("outfits").insert(outfit_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Errore durante la creazione dell'outfit"
            )
        
        created_outfit = result.data[0]
        outfit_id = created_outfit["id"]
        
        # Aggiungi i prodotti all'outfit
        if outfit.product_ids:
            outfit_products = [
                {"outfit_id": outfit_id, "product_id": str(pid)}
                for pid in outfit.product_ids
            ]
            supabase.table("outfit_products").insert(outfit_products).execute()
        
        # Recupera l'outfit completo con i prodotti
        final_result = supabase.table("outfits").select("*, outfit_products(product_id)").eq("id", outfit_id).execute()
        
        final_outfit = final_result.data[0]
        final_outfit["product_ids"] = [
            op["product_id"] for op in final_outfit.get("outfit_products", [])
        ]
        if "outfit_products" in final_outfit:
            del final_outfit["outfit_products"]
        
        return {
            "message": "Outfit creato con successo",
            "outfit": final_outfit
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore creazione outfit: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Errore durante la creazione dell'outfit: {str(e)}"
        )


@router.delete("/{outfit_id}")
async def delete_outfit(outfit_id: UUID, supabase: Client = Depends(get_supabase)):
    """Elimina un outfit"""
    try:
        # Le relazioni outfit_products verranno eliminate automaticamente per CASCADE
        result = supabase.table("outfits").delete().eq("id", str(outfit_id)).execute()
        
        return {
            "message": "Outfit eliminato con successo",
            "outfit_id": str(outfit_id)
        }
    except Exception as e:
        logger.error(f"Errore eliminazione outfit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante l'eliminazione dell'outfit: {str(e)}"
        )

