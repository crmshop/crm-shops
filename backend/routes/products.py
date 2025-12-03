"""
Route per gestione prodotti
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

router = APIRouter(prefix="/api/products", tags=["prodotti"])


class ProductCreate(BaseModel):
    shop_id: UUID
    name: str
    description: Optional[str] = None
    category: str  # 'vestiti', 'scarpe', 'accessori'
    season: Optional[str] = None
    occasion: Optional[str] = None
    style: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    available: bool = True


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    season: Optional[str] = None
    occasion: Optional[str] = None
    style: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    available: Optional[bool] = None


@router.get("/")
async def list_products(
    shop_id: Optional[UUID] = None,
    category: Optional[str] = None,
    available: Optional[bool] = None
):
    """Lista prodotti con filtri opzionali"""
    # TODO: Implementare query Supabase
    return {
        "message": "Lista prodotti - da implementare",
        "filters": {
            "shop_id": str(shop_id) if shop_id else None,
            "category": category,
            "available": available
        }
    }


@router.get("/{product_id}")
async def get_product(product_id: UUID):
    """Ottieni dettagli di un prodotto"""
    # TODO: Implementare query Supabase
    return {
        "message": "Dettagli prodotto - da implementare",
        "product_id": str(product_id)
    }


@router.post("/")
async def create_product(product: ProductCreate):
    """Crea un nuovo prodotto"""
    # TODO: Implementare inserimento Supabase
    return {
        "message": "Prodotto creato - da implementare",
        "product": product.dict()
    }


@router.put("/{product_id}")
async def update_product(product_id: UUID, product: ProductUpdate):
    """Aggiorna un prodotto"""
    # TODO: Implementare aggiornamento Supabase
    return {
        "message": "Prodotto aggiornato - da implementare",
        "product_id": str(product_id),
        "updates": product.dict(exclude_unset=True)
    }


@router.delete("/{product_id}")
async def delete_product(product_id: UUID):
    """Elimina un prodotto"""
    # TODO: Implementare eliminazione Supabase
    return {
        "message": "Prodotto eliminato - da implementare",
        "product_id": str(product_id)
    }

