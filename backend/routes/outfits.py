"""
Route per gestione outfit
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

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
async def list_outfits(user_id: Optional[UUID] = None, shop_id: Optional[UUID] = None):
    """Lista outfit con filtri opzionali"""
    # TODO: Implementare query Supabase
    return {
        "message": "Lista outfit - da implementare",
        "filters": {
            "user_id": str(user_id) if user_id else None,
            "shop_id": str(shop_id) if shop_id else None
        }
    }


@router.get("/{outfit_id}")
async def get_outfit(outfit_id: UUID):
    """Ottieni dettagli di un outfit"""
    # TODO: Implementare query Supabase
    return {
        "message": "Dettagli outfit - da implementare",
        "outfit_id": str(outfit_id)
    }


@router.post("/")
async def create_outfit(outfit: OutfitCreate):
    """Crea un nuovo outfit"""
    # TODO: Implementare inserimento Supabase
    return {
        "message": "Outfit creato - da implementare",
        "outfit": outfit.dict()
    }


@router.delete("/{outfit_id}")
async def delete_outfit(outfit_id: UUID):
    """Elimina un outfit"""
    # TODO: Implementare eliminazione Supabase
    return {
        "message": "Outfit eliminato - da implementare",
        "outfit_id": str(outfit_id)
    }

