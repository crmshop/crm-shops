"""
Route per gestione immagini generate dall'AI
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from supabase import Client
from backend.database import get_supabase
from backend.middleware.auth import get_current_user
from backend.services.ai_service import ai_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/generated-images", tags=["immagini-generate"])


class GenerateImageRequest(BaseModel):
    customer_photo_id: UUID
    product_id: Optional[UUID] = None
    outfit_id: Optional[UUID] = None
    scenario: Optional[str] = None
    prompt_override: Optional[str] = None


@router.get("/")
async def list_generated_images(
    customer_photo_id: Optional[UUID] = None,
    product_id: Optional[UUID] = None,
    outfit_id: Optional[UUID] = None,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Lista immagini generate con filtri opzionali"""
    try:
        query = supabase.table("generated_images").select("*")
        
        if customer_photo_id:
            query = query.eq("customer_photo_id", str(customer_photo_id))
        if product_id:
            query = query.eq("product_id", str(product_id))
        if outfit_id:
            query = query.eq("outfit_id", str(outfit_id))
        
        result = query.execute()
        return {
            "images": result.data,
            "count": len(result.data)
        }
    except Exception as e:
        logger.error(f"Errore lista immagini generate: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante il recupero immagini: {str(e)}"
        )


@router.get("/{image_id}")
async def get_generated_image(
    image_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Ottieni dettagli di un'immagine generata"""
    try:
        result = supabase.table("generated_images").select("*").eq("id", str(image_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Immagine non trovata"
            )
        
        return {"image": result.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore recupero immagine: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante il recupero immagine: {str(e)}"
        )


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_image(
    request: GenerateImageRequest,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Genera un'immagine AI combinando foto cliente e prodotto/outfit"""
    try:
        # Verifica che la foto cliente esista e appartenga all'utente
        photo_result = supabase.table("customer_photos").select("*").eq("id", str(request.customer_photo_id)).execute()
        
        if not photo_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Foto cliente non trovata"
            )
        
        photo = photo_result.data[0]
        
        # Verifica permessi
        if current_user["role"] == "cliente" and photo["user_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accesso negato"
            )
        
        # Ottieni informazioni prodotto/outfit per costruire il prompt
        product_data = None
        if request.product_id:
            product_result = supabase.table("products").select("*").eq("id", str(request.product_id)).execute()
            if product_result.data:
                product_data = product_result.data[0]
        
        # Costruisci prompt
        prompt = request.prompt_override
        if not prompt and product_data:
            prompt = ai_service.build_prompt(
                product_category=product_data.get("category"),
                product_style=product_data.get("style"),
                scenario=request.scenario
            )
        
        # Genera immagine usando servizio AI
        ai_result = await ai_service.generate_image(
            customer_photo_url=photo["image_url"],
            product_image_url=product_data.get("image_url") if product_data else None,
            prompt=prompt,
            scenario=request.scenario,
            service="banana_pro"  # Default, può essere configurato
        )
        
        generated_image_url = ai_result["image_url"]
        prompt_used = ai_result["prompt_used"]
        ai_service_used = ai_result["ai_service"]
        
        image_data = {
            "customer_photo_id": str(request.customer_photo_id),
            "image_url": generated_image_url,
            "prompt_used": prompt_used,
            "scenario": request.scenario,
            "ai_service": ai_service_used
        }
        
        if request.product_id:
            image_data["product_id"] = str(request.product_id)
        if request.outfit_id:
            image_data["outfit_id"] = str(request.outfit_id)
        
        result = supabase.table("generated_images").insert(image_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Errore durante la generazione dell'immagine"
            )
        
        return {
            "message": "Immagine generata con successo (placeholder - implementare AI service)",
            "image": result.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore generazione immagine: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante la generazione dell'immagine: {str(e)}"
        )


@router.delete("/{image_id}")
async def delete_generated_image(
    image_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Elimina un'immagine generata"""
    try:
        result = supabase.table("generated_images").delete().eq("id", str(image_id)).execute()
        
        return {
            "message": "Immagine eliminata con successo",
            "image_id": str(image_id)
        }
    except Exception as e:
        logger.error(f"Errore eliminazione immagine: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante l'eliminazione dell'immagine: {str(e)}"
        )

