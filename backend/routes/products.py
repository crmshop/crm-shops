"""
Route per gestione prodotti
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from supabase import Client
from backend.database import get_supabase
from backend.middleware.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

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
    image_url: Optional[str] = None  # Deprecato: usa images invece
    images: Optional[List[str]] = None  # Lista di URL immagini (max 3)
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
    available: Optional[bool] = None,
    supabase: Client = Depends(get_supabase)
):
    """Lista prodotti con filtri opzionali"""
    try:
        query = supabase.table("products").select("*")
        
        if shop_id:
            query = query.eq("shop_id", str(shop_id))
        if category:
            query = query.eq("category", category)
        if available is not None:
            query = query.eq("available", available)
        
        result = query.execute()
        return {
            "products": result.data,
            "count": len(result.data)
        }
    except Exception as e:
        logger.error(f"Errore lista prodotti: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante il recupero prodotti: {str(e)}"
        )


@router.get("/{product_id}")
async def get_product(product_id: UUID, supabase: Client = Depends(get_supabase)):
    """Ottieni dettagli di un prodotto"""
    try:
        result = supabase.table("products").select("*").eq("id", str(product_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prodotto non trovato"
            )
        
        return {"product": result.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore recupero prodotto: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante il recupero prodotto: {str(e)}"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Crea un nuovo prodotto"""
    try:
        # Solo negozianti possono creare prodotti
        if current_user["role"] != "negoziante":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo i negozianti possono creare prodotti"
            )
        
        # Verifica che il negozio appartenga all'utente corrente
        shop_result = supabase.table("shops").select("*").eq("id", str(product.shop_id)).execute()
        if not shop_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Negozio non trovato"
            )
        
        if shop_result.data[0]["owner_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Puoi creare prodotti solo per i tuoi negozi"
            )
        
        # Valida categoria
        if product.category not in ["vestiti", "scarpe", "accessori"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Categoria deve essere 'vestiti', 'scarpe' o 'accessori'"
            )
        
        product_data = product.dict()
        product_data["shop_id"] = str(product_data["shop_id"])
        
        result = supabase.table("products").insert(product_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Errore durante la creazione del prodotto"
            )
        
        return {
            "message": "Prodotto creato con successo",
            "product": result.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore creazione prodotto: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Errore durante la creazione del prodotto: {str(e)}"
        )


@router.put("/{product_id}")
async def update_product(product_id: UUID, product: ProductUpdate, supabase: Client = Depends(get_supabase)):
    """Aggiorna un prodotto"""
    try:
        updates = product.dict(exclude_unset=True)
        
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nessun campo da aggiornare"
            )
        
        result = supabase.table("products").update(updates).eq("id", str(product_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prodotto non trovato"
            )
        
        return {
            "message": "Prodotto aggiornato con successo",
            "product": result.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore aggiornamento prodotto: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante l'aggiornamento del prodotto: {str(e)}"
        )


@router.delete("/{product_id}")
async def delete_product(product_id: UUID, supabase: Client = Depends(get_supabase)):
    """Elimina un prodotto"""
    try:
        result = supabase.table("products").delete().eq("id", str(product_id)).execute()
        
        return {
            "message": "Prodotto eliminato con successo",
            "product_id": str(product_id)
        }
    except Exception as e:
        logger.error(f"Errore eliminazione prodotto: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante l'eliminazione del prodotto: {str(e)}"
        )

