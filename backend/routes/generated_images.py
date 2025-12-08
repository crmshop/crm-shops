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


class GenerateOutfitImageRequest(BaseModel):
    shop_id: UUID
    customer_id: UUID  # ID da shop_customers
    product_ids: List[UUID]  # Max 10 prodotti
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
        # NOTA: Gemini non può generare immagini, solo analizzarle
        # Usa Banana Pro per generazione immagini (default)
        ai_model = "banana_pro"  # Banana Pro usa Stable Diffusion per generare immagini
        
        ai_result = await ai_service.generate_image_with_product(
            customer_photo_url=photo["image_url"],
            product_image_url=product_data.get("image_url") if product_data else None,
            prompt=prompt,
            scenario=request.scenario,
            ai_model=ai_model
        )
        
        generated_image_url = ai_result.get("image_url", "")
        prompt_used = prompt or ai_result.get("prompt_used", "")
        ai_service_used = ai_result.get("ai_service", ai_model)
        
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


@router.post("/generate-outfit", status_code=status.HTTP_201_CREATED)
async def generate_outfit_image(
    request: GenerateOutfitImageRequest,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Genera un'immagine AI combinando foto cliente e più prodotti (outfit)"""
    try:
        # Valida numero prodotti (max 10)
        if len(request.product_ids) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Puoi selezionare massimo 10 prodotti"
            )
        
        if len(request.product_ids) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Seleziona almeno un prodotto"
            )
        
        # Verifica che il cliente appartenga al negozio
        customer_response = supabase.table("shop_customers").select("*").eq("id", str(request.customer_id)).eq("shop_id", str(request.shop_id)).execute()
        if not customer_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente non trovato per questo negozio"
            )
        
        customer = customer_response.data[0]
        
        # Recupera foto del cliente (prima foto disponibile)
        customer_photos_response = supabase.table("customer_photos").select("*").eq("customer_id", str(request.customer_id)).limit(1).execute()
        if not customer_photos_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nessuna foto trovata per questo cliente"
            )
        
        customer_photo = customer_photos_response.data[0]
        customer_photo_url = customer_photo["image_url"]
        
        # Recupera prodotti
        products_response = supabase.table("products").select("*").in_("id", [str(pid) for pid in request.product_ids]).execute()
        if not products_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prodotti non trovati"
            )
        
        products = products_response.data
        product_image_urls = [p.get("image_url") for p in products if p.get("image_url")]
        
        if not product_image_urls:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nessun prodotto ha un'immagine disponibile"
            )
        
        # Costruisci prompt
        prompt = request.prompt_override
        if not prompt:
            product_names = [p.get("name", "") for p in products]
            prompt = f"Create a realistic image of the person from the customer photo wearing the following items: {', '.join(product_names)}. High quality, professional photography style."
        
        # Genera immagine usando AI service (Banana Pro per generazione immagini)
        # NOTA: Gemini non può generare immagini, solo analizzarle
        # Per ora usiamo solo il primo prodotto, Banana Pro non supporta multiple products
        # TODO: Implementare supporto per multiple products con Banana Pro
        
        from backend.services.ai_service import ai_service
        
        # Usa Banana Pro per generazione immagini (Gemini non supporta generazione)
        # Per outfit con più prodotti, usa il primo prodotto per ora
        first_product_url = product_image_urls[0] if product_image_urls else None
        if not first_product_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Almeno un prodotto è richiesto per generare l'immagine"
            )
        
        ai_result = await ai_service.generate_image_with_product(
            customer_photo_url=customer_photo_url,
            product_image_url=first_product_url,
            prompt=prompt,
            scenario=request.scenario,
            ai_model="banana_pro"  # Usa Banana Pro invece di Gemini
        )
        
        generated_image_url = ai_result.get("image_url", "")
        
        # Salva immagine generata
        image_data = {
            "customer_photo_id": str(customer_photo["id"]),
            "image_url": generated_image_url,
            "prompt_used": prompt,
            "scenario": request.scenario,
            "ai_service": "gemini"
        }
        
        result = supabase.table("generated_images").insert(image_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Errore durante la generazione dell'immagine"
            )
        
        return {
            "message": "Immagine outfit generata con successo",
            "image": result.data[0],
            "image_url": generated_image_url
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore generazione immagine outfit: {e}")
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

