"""
Route per statistiche negozio (solo negozianti)
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List, Dict
from uuid import UUID
from backend.database import get_supabase
from backend.middleware.auth import get_current_shop_owner
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/shop-stats", tags=["statistiche"])


class ShopStatsResponse(BaseModel):
    shop_id: UUID
    total_customers: int
    total_products: int
    total_photos: int
    total_generated_images: int
    recent_customers: List[Dict]
    top_products: List[Dict]
    period: str


@router.get("/{shop_id}", response_model=ShopStatsResponse)
async def get_shop_stats(
    shop_id: UUID,
    period: Optional[str] = "30days",  # "7days", "30days", "90days", "all"
    current_user: dict = Depends(get_current_shop_owner)
):
    """Ottieni statistiche di un negozio"""
    supabase = get_supabase()
    
    # Verifica che il negozio appartenga al negoziante
    shop_response = supabase.from_('shops').select('id, owner_id').eq('id', str(shop_id)).single().execute()
    if not shop_response.data or shop_response.data['owner_id'] != current_user['id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non autorizzato a vedere le statistiche di questo negozio"
        )
    
    try:
        # Calcola data di inizio periodo
        now = datetime.now()
        if period == "7days":
            start_date = now - timedelta(days=7)
        elif period == "30days":
            start_date = now - timedelta(days=30)
        elif period == "90days":
            start_date = now - timedelta(days=90)
        else:
            start_date = None
        
        # Conta clienti negozio
        customers_query = supabase.from_('shop_customers').select('id', count='exact').eq('shop_id', str(shop_id))
        if start_date:
            customers_query = customers_query.gte('created_at', start_date.isoformat())
        customers_response = customers_query.execute()
        total_customers = customers_response.count if hasattr(customers_response, 'count') else len(customers_response.data) if customers_response.data else 0
        
        # Conta prodotti
        products_query = supabase.from_('products').select('id', count='exact').eq('shop_id', str(shop_id))
        products_response = products_query.execute()
        total_products = products_response.count if hasattr(products_response, 'count') else len(products_response.data) if products_response.data else 0
        
        # Conta foto clienti negozio
        photos_query = supabase.from_('customer_photos').select('id', count='exact').eq('shop_id', str(shop_id))
        if start_date:
            photos_query = photos_query.gte('uploaded_at', start_date.isoformat())
        photos_response = photos_query.execute()
        total_photos = photos_response.count if hasattr(photos_response, 'count') else len(photos_response.data) if photos_response.data else 0
        
        # Conta immagini generate (tramite foto clienti negozio)
        generated_query = supabase.from_('generated_images').select('id', count='exact')
        if start_date:
            generated_query = generated_query.gte('generated_at', start_date.isoformat())
        # Filtra per prodotti del negozio
        products_list = supabase.from_('products').select('id').eq('shop_id', str(shop_id)).execute()
        product_ids = [p['id'] for p in products_list.data] if products_list.data else []
        if product_ids:
            generated_query = generated_query.in_('product_id', [str(pid) for pid in product_ids])
        generated_response = generated_query.execute()
        total_generated_images = generated_response.count if hasattr(generated_response, 'count') else len(generated_response.data) if generated_response.data else 0
        
        # Clienti recenti (ultimi 10)
        recent_customers_response = supabase.from_('shop_customers').select('*').eq('shop_id', str(shop_id)).order('created_at', desc=True).limit(10).execute()
        recent_customers = recent_customers_response.data or []
        
        # Prodotti più popolari (per ora, tutti i prodotti)
        top_products_response = supabase.from_('products').select('*').eq('shop_id', str(shop_id)).order('created_at', desc=True).limit(10).execute()
        top_products = top_products_response.data or []
        
        return ShopStatsResponse(
            shop_id=shop_id,
            total_customers=total_customers,
            total_products=total_products,
            total_photos=total_photos,
            total_generated_images=total_generated_images,
            recent_customers=recent_customers,
            top_products=top_products,
            period=period
        )
        
    except Exception as e:
        logger.error(f"Errore nel recupero statistiche negozio {shop_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore nel recupero delle statistiche"
        )


@router.get("/")
async def get_all_shops_stats(
    period: Optional[str] = "30days",
    current_user: dict = Depends(get_current_shop_owner)
):
    """Ottieni statistiche di tutti i negozi del negoziante"""
    supabase = get_supabase()
    
    try:
        # Recupera tutti i negozi del negoziante
        shops_response = supabase.from_('shops').select('id').eq('owner_id', current_user['id']).execute()
        shop_ids = [shop['id'] for shop in shops_response.data] if shops_response.data else []
        
        stats = []
        for shop_id in shop_ids:
            try:
                shop_stats = await get_shop_stats(shop_id, period, current_user)
                stats.append(shop_stats.model_dump())
            except Exception as e:
                logger.error(f"Errore statistiche negozio {shop_id}: {e}")
                continue
        
        return {"shops_stats": stats}
        
    except Exception as e:
        logger.error(f"Errore nel recupero statistiche: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore nel recupero delle statistiche"
        )


