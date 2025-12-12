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


class OutfitScenarioDetail(BaseModel):
    scenario_prompt_id: UUID
    custom_text: Optional[str] = None


class GenerateOutfitImageRequest(BaseModel):
    shop_id: UUID
    customer_id: UUID  # ID da shop_customers
    product_ids: List[UUID]  # Max 10 prodotti
    outfit_id: Optional[UUID] = None  # Se presente, recupera scenari dall'outfit
    scenarios: Optional[List[OutfitScenarioDetail]] = []  # Scenari con testo libero (max 3)
    scenario: Optional[str] = None  # Deprecato, usa scenarios
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
        
        # Per compatibilità con endpoint singolo prodotto, usa liste con un elemento
        customer_photo_urls = [photo["image_url"]]
        product_image_urls = [product_data.get("image_url")] if product_data and product_data.get("image_url") else []
        
        if not product_image_urls:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prodotto non ha un'immagine disponibile"
            )
        
        ai_result = await ai_service.generate_image_with_product(
            customer_photo_urls=customer_photo_urls,
            product_image_urls=product_image_urls,
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
        
        # Recupera tutte le foto del cliente (fino a 3)
        customer_photos_response = supabase.table("customer_photos").select("*").eq("customer_id", str(request.customer_id)).limit(3).execute()
        if not customer_photos_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nessuna foto trovata per questo cliente"
            )
        
        customer_photos = customer_photos_response.data
        customer_photo_urls = [photo.get("image_url") for photo in customer_photos if photo.get("image_url")]
        
        if not customer_photo_urls:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nessuna foto cliente valida trovata"
            )
        
        logger.info(f"📸 Foto cliente recuperate: {len(customer_photo_urls)}")
        
        # Recupera prodotti
        products_response = supabase.table("products").select("*").in_("id", [str(pid) for pid in request.product_ids]).execute()
        if not products_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prodotti non trovati"
            )
        
        products = products_response.data
        
        # Log dettagliato per debug
        logger.info(f"🛍️ Prodotti recuperati dal database: {len(products)}")
        for idx, p in enumerate(products, 1):
            image_url = p.get("image_url")
            logger.info(f"   Prodotto {idx}: {p.get('name', 'Sconosciuto')} - URL: {image_url if image_url else 'NON DISPONIBILE'}")
        
        # Filtra solo prodotti con URL immagine validi (non None, non vuoti, e che iniziano con http)
        product_image_urls = []
        products_without_images = []
        
        for p in products:
            image_url = p.get("image_url")
            if not image_url:
                products_without_images.append(p.get("name", "Sconosciuto"))
                continue
            if not isinstance(image_url, str):
                products_without_images.append(f"{p.get('name', 'Sconosciuto')} (URL non stringa: {type(image_url)})")
                continue
            if not image_url.strip():
                products_without_images.append(f"{p.get('name', 'Sconosciuto')} (URL vuoto)")
                continue
            if not (image_url.startswith("http://") or image_url.startswith("https://")):
                products_without_images.append(f"{p.get('name', 'Sconosciuto')} (URL non valido: {image_url[:50]}...)")
                continue
            product_image_urls.append(image_url)
        
        if not product_image_urls:
            product_names = [p.get("name", "Sconosciuto") for p in products]
            error_msg = f"Nessun prodotto ha un'immagine disponibile. Prodotti selezionati: {', '.join(product_names)}"
            if products_without_images:
                error_msg += f". Prodotti senza immagini valide: {', '.join(products_without_images)}"
            logger.error(f"❌ {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        if products_without_images:
            logger.warning(f"⚠️  {len(products_without_images)} prodotti senza immagini valide: {', '.join(products_without_images)}")
        
        logger.info(f"✅ {len(product_image_urls)} prodotti con immagini valide su {len(products)} totali")
        logger.info(f"   URL immagini prodotto: {product_image_urls}")
        
        # Recupera dettagli scenari se outfit_id è presente o se scenarios è fornito
        scenario_details = []
        if request.outfit_id:
            # Recupera scenari dall'outfit
            outfit_result = supabase.table("outfits").select(
                "outfit_scenarios(scenario_prompt_id, custom_text, scenario_prompts(*))"
            ).eq("id", str(request.outfit_id)).execute()
            
            if outfit_result.data and outfit_result.data[0].get("outfit_scenarios"):
                for os in outfit_result.data[0]["outfit_scenarios"]:
                    scenario_prompt = os.get("scenario_prompts", {})
                    scenario_details.append({
                        "description": scenario_prompt.get("description", ""),
                        "position": scenario_prompt.get("position"),
                        "environment": scenario_prompt.get("environment"),
                        "lighting": scenario_prompt.get("lighting"),
                        "background": scenario_prompt.get("background"),
                        "custom_text": os.get("custom_text")
                    })
        elif request.scenarios:
            # Recupera dettagli scenari dalla lista fornita
            scenario_ids = [str(s.scenario_prompt_id) for s in request.scenarios]
            scenarios_result = supabase.table("scenario_prompts").select("*").in_("id", scenario_ids).execute()
            scenarios_dict = {s["id"]: s for s in scenarios_result.data}
            
            for scenario_request in request.scenarios:
                scenario_prompt = scenarios_dict.get(str(scenario_request.scenario_prompt_id), {})
                scenario_details.append({
                    "description": scenario_prompt.get("description", ""),
                    "position": scenario_prompt.get("position"),
                    "environment": scenario_prompt.get("environment"),
                    "lighting": scenario_prompt.get("lighting"),
                    "background": scenario_prompt.get("background"),
                    "custom_text": scenario_request.custom_text
                })
        
        # Verifica che gli URL delle immagini prodotto siano validi prima di iniziare la generazione
        if not product_image_urls or len(product_image_urls) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nessuna immagine prodotto valida disponibile per la generazione"
            )
        
        # Verifica che tutti gli URL siano stringhe valide
        invalid_urls = []
        for idx, url in enumerate(product_image_urls, 1):
            if not url or not isinstance(url, str) or not url.strip():
                invalid_urls.append(f"URL {idx}: {url}")
            elif not (url.startswith("http://") or url.startswith("https://")):
                invalid_urls.append(f"URL {idx}: {url[:50]}... (non inizia con http/https)")
        
        if invalid_urls:
            logger.error(f"❌ URL immagini prodotto non validi: {invalid_urls}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Alcune immagini prodotto hanno URL non validi: {', '.join(invalid_urls)}"
            )
        
        # Se ci sono scenari, genera una foto per ogni scenario (max 3)
        # Se non ci sono scenari, genera una sola foto
        scenarios_to_generate = scenario_details if scenario_details else [None]  # Se nessuno scenario, genera una foto
        
        # Limita a max 3 scenari
        if len(scenarios_to_generate) > 3:
            scenarios_to_generate = scenarios_to_generate[:3]
            logger.warning(f"⚠️  Più di 3 scenari forniti, genero solo i primi 3")
        
        product_names = [p.get("name", "") for p in products]
        product_categories = [p.get("category", "") for p in products]
        
        logger.info(f"🎨 Inizio generazione {len(scenarios_to_generate)} immagine/i con {len(product_image_urls)} immagini prodotto")
        
        generated_images = []
        errors = []
        
        # Genera una foto per ogni scenario
        for idx, scenario_detail in enumerate(scenarios_to_generate):
            try:
                # Costruisci prompt per questo scenario specifico
                prompt = request.prompt_override
                if not prompt:
                    # Usa build_prompt con questo scenario specifico
                    from backend.services.ai_service import ai_service
                    scenario_list = [scenario_detail] if scenario_detail else None
                    prompt = ai_service.build_prompt(
                        product_category=", ".join(set(product_categories)) if product_categories else None,
                        scenario_details=scenario_list,
                        scenario=request.scenario  # Fallback per retrocompatibilità
                    )
                    
                    # Aggiungi nomi prodotti al prompt
                    if product_names:
                        prompt += f" Articoli indossati: {', '.join(product_names)}."
                
                logger.info(f"🎨 Generazione immagine {idx + 1}/{len(scenarios_to_generate)} per scenario: {scenario_detail.get('description', 'Nessuno') if scenario_detail else 'Default'}")
                logger.info(f"   📸 Foto cliente da usare: {len(customer_photo_urls)} immagini")
                logger.info(f"   🛍️ Immagini prodotto da usare: {len(product_image_urls)} immagini")
                logger.info(f"   📝 Prompt: {prompt[:200]}...")
                
                # Verifica che le foto cliente siano valide
                if not customer_photo_urls or len(customer_photo_urls) == 0:
                    error_msg = f"Nessuna foto cliente valida per la generazione immagine {idx + 1}"
                    logger.error(f"❌ {error_msg}")
                    errors.append(error_msg)
                    continue
                
                # Genera immagine usando AI service con tutte le immagini
                from backend.services.ai_service import ai_service
                
                ai_result = await ai_service.generate_image_with_product(
                    customer_photo_urls=customer_photo_urls,  # Lista di tutte le foto cliente (fino a 3)
                    product_image_urls=product_image_urls,  # Lista di tutte le immagini prodotto (fino a 10)
                    prompt=prompt,
                    scenario=request.scenario,  # Mantenuto per retrocompatibilità
                    ai_model="banana_pro"  # Usa Banana Pro per generazione immagini
                )
                
                generated_image_url = ai_result.get("image_url", "")
                
                if not generated_image_url:
                    error_msg = f"Immagine {idx + 1} non generata correttamente"
                    logger.error(f"❌ {error_msg}")
                    errors.append(error_msg)
                    continue
                
                # Determina scenario description per questo scenario
                scenario_description = None
                if scenario_detail:
                    scenario_description = scenario_detail.get("description", "")
                    if scenario_detail.get("custom_text"):
                        scenario_description += f" - {scenario_detail['custom_text']}"
                elif request.scenario:
                    scenario_description = request.scenario
                
                # Salva immagine generata
                # Usa la prima foto cliente come riferimento principale
                image_data = {
                    "customer_photo_id": str(customer_photos[0]["id"]),
                    "image_url": generated_image_url,
                    "prompt_used": prompt,
                    "scenario": scenario_description,
                    "ai_service": ai_result.get("ai_service", "banana_pro")  # Usa il servizio effettivamente usato
                }
                
                if request.outfit_id:
                    image_data["outfit_id"] = str(request.outfit_id)
                
                # Se c'è un errore nel risultato, loggalo
                if ai_result.get("status") == "error":
                    error_msg = f"Errore durante generazione immagine {idx + 1}: {ai_result.get('error', 'Unknown error')}"
                    logger.error(f"❌ {error_msg}")
                    if ai_result.get("error_details"):
                        logger.error(f"   Dettagli errore:\n{ai_result.get('error_details')}")
                    errors.append(error_msg)
                    continue
                
                result = supabase.table("generated_images").insert(image_data).execute()
                
                if result.data:
                    generated_images.append(result.data[0])
                    logger.info(f"✅ Immagine {idx + 1}/{len(scenarios_to_generate)} salvata con successo")
                else:
                    error_msg = f"Errore durante il salvataggio dell'immagine {idx + 1}"
                    logger.error(f"❌ {error_msg}")
                    errors.append(error_msg)
                    
            except Exception as e:
                error_msg = f"Errore durante generazione immagine {idx + 1}: {str(e)}"
                logger.error(f"❌ {error_msg}")
                errors.append(error_msg)
                continue
        
        if not generated_images:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Nessuna immagine generata con successo. Errori: {'; '.join(errors)}"
            )
        
        return {
            "message": f"{len(generated_images)} immagine/i outfit generate con successo",
            "images": generated_images,
            "count": len(generated_images),
            "errors": errors if errors else None
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

