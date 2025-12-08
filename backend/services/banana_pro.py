"""
Servizio per integrazione Banana Pro API
"""
import httpx
import logging
from typing import Optional, Dict, Any
from backend.config import settings
import base64
import json

logger = logging.getLogger(__name__)


class BananaProService:
    """Servizio per generazione immagini con Banana Pro"""
    
    def __init__(self):
        self.api_key = settings.BANANA_PRO_API_KEY
        self.base_url = "https://api.banana.dev"  # URL base Banana Pro
        if not self.api_key:
            logger.warning("BANANA_PRO_API_KEY non configurata")
    
    async def generate_image(
        self,
        customer_photo_url: str,
        product_image_url: str,
        prompt: Optional[str] = None,
        scenario: Optional[str] = None,
        model: str = "stable-diffusion-xl"  # Modello predefinito
    ) -> Dict[str, Any]:
        """
        Genera un'immagine combinando foto cliente e prodotto
        
        Args:
            customer_photo_url: URL della foto del cliente
            product_image_url: URL dell'immagine del prodotto
            prompt: Prompt personalizzato (opzionale)
            scenario: Scenario/contesto (montagna, spiaggia, etc.)
            model: Modello AI da usare
        
        Returns:
            Dict con 'image_url', 'job_id', 'status'
        """
        if not self.api_key:
            raise ValueError("BANANA_PRO_API_KEY non configurata")
        
        try:
            # Costruisci prompt se non fornito
            if not prompt:
                prompt = self._build_prompt(scenario)
            
            # Prepara payload per Banana Pro
            payload = {
                "model": model,
                "prompt": prompt,
                "negative_prompt": "blurry, low quality, distorted",
                "num_inference_steps": 50,
                "guidance_scale": 7.5,
                "width": 1024,
                "height": 1024,
                "customer_image_url": customer_photo_url,
                "product_image_url": product_image_url
            }
            
            # Chiamata API Banana Pro
            logger.info(f"🚀 Chiamata API Banana Pro: {self.base_url}/v1/generate")
            logger.info(f"   Payload: {json.dumps(payload, indent=2)}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/generate",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )
                
                logger.info(f"   Status code: {response.status_code}")
                logger.info(f"   Response headers: {dict(response.headers)}")
                
                response.raise_for_status()
                result = response.json()
                logger.info(f"   Risultato Banana Pro: {json.dumps(result, indent=2)}")
                
                # Banana Pro restituisce un job_id, poi bisogna fare polling
                if "job_id" in result:
                    # Polling per ottenere il risultato
                    banana_image_url = await self._poll_job_status(result["job_id"])
                    # Salva l'immagine su Supabase Storage
                    supabase_image_url = await self._save_to_supabase_storage(banana_image_url)
                    return {
                        "image_url": supabase_image_url,
                        "banana_pro_url": banana_image_url,  # Mantieni anche l'URL originale
                        "job_id": result["job_id"],
                        "status": "completed",
                        "ai_service": "banana_pro"
                    }
                elif "image_url" in result:
                    # Risultato immediato
                    banana_image_url = result["image_url"]
                    # Salva l'immagine su Supabase Storage
                    supabase_image_url = await self._save_to_supabase_storage(banana_image_url)
                    return {
                        "image_url": supabase_image_url,
                        "banana_pro_url": banana_image_url,  # Mantieni anche l'URL originale
                        "status": "completed",
                        "ai_service": "banana_pro"
                    }
                else:
                    raise ValueError(f"Risposta Banana Pro non valida: {result}")
                    
        except httpx.HTTPError as e:
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"❌ Errore HTTP Banana Pro: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"   Response status: {e.response.status_code}")
                logger.error(f"   Response body: {e.response.text}")
            logger.error(f"   Traceback completo:\n{error_trace}")
            raise Exception(f"Errore comunicazione Banana Pro: {str(e)}") from e
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"❌ Errore generazione Banana Pro: {e}")
            logger.error(f"   Traceback completo:\n{error_trace}")
            raise
    
    async def _poll_job_status(self, job_id: str, max_attempts: int = 30) -> str:
        """Polling per verificare lo stato del job"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            for attempt in range(max_attempts):
                try:
                    response = await client.get(
                        f"{self.base_url}/v1/jobs/{job_id}",
                        headers={"Authorization": f"Bearer {self.api_key}"}
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    if result.get("status") == "completed":
                        return result.get("image_url", "")
                    elif result.get("status") == "failed":
                        raise Exception(f"Job Banana Pro fallito: {result.get('error', 'Unknown error')}")
                    
                    # Attendi prima del prossimo polling
                    import asyncio
                    await asyncio.sleep(2)
                    
                except httpx.HTTPError as e:
                    logger.error(f"Errore polling Banana Pro: {e}")
                    if attempt == max_attempts - 1:
                        raise
                    import asyncio
                    await asyncio.sleep(2)
            
            raise TimeoutError("Timeout polling job Banana Pro")
    
    async def _save_to_supabase_storage(self, image_url: str) -> str:
        """
        Scarica l'immagine da Banana Pro e la salva su Supabase Storage
        
        Args:
            image_url: URL dell'immagine generata da Banana Pro
            
        Returns:
            URL pubblico dell'immagine su Supabase Storage
        """
        try:
            from backend.database import get_supabase_admin
            from uuid import uuid4
            
            # Usa admin client per upload Storage (bypassa RLS)
            supabase_admin = get_supabase_admin()
            
            # Scarica l'immagine da Banana Pro
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.info(f"📥 Download immagine da Banana Pro: {image_url}")
                response = await client.get(image_url)
                response.raise_for_status()
                image_bytes = response.content
                
                # Verifica che sia un'immagine valida
                if not image_bytes or len(image_bytes) == 0:
                    raise ValueError("Immagine scaricata vuota")
                
                logger.info(f"✅ Immagine scaricata: {len(image_bytes)} bytes")
            
            # Genera nome file univoco
            file_name = f"generated/{uuid4()}.jpg"
            
            # Carica su Supabase Storage
            bucket_name = "generated-images"
            logger.info(f"📤 Upload su Supabase Storage: {bucket_name}/{file_name}")
            
            # Prova a caricare, se esiste già genera un nuovo nome
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    supabase_admin.storage.from_(bucket_name).upload(
                        file_name,
                        image_bytes,
                        file_options={"content-type": "image/jpeg", "upsert": "true"}
                    )
                    break
                except Exception as e:
                    if "duplicate" in str(e).lower() or "already exists" in str(e).lower():
                        # Genera nuovo nome se esiste già
                        file_name = f"generated/{uuid4()}.jpg"
                        if attempt == max_retries - 1:
                            raise
                    else:
                        raise
            
            # Ottieni URL pubblico
            public_url = supabase_admin.storage.from_(bucket_name).get_public_url(file_name)
            logger.info(f"✅ Immagine salvata su Supabase Storage: {public_url}")
            
            return public_url
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"❌ Errore salvataggio immagine Banana Pro su Supabase Storage: {e}")
            logger.error(f"   Traceback completo:\n{error_trace}")
            # Fallback: restituisci l'URL originale di Banana Pro
            logger.warning(f"⚠️  Uso URL Banana Pro originale come fallback: {image_url}")
            # Rilancia l'eccezione per essere gestita dal chiamante
            raise Exception(f"Errore salvataggio su Supabase Storage: {str(e)}") from e
    
    def _build_prompt(self, scenario: Optional[str] = None) -> str:
        """Costruisci prompt base per generazione immagine"""
        base_prompt = "A person wearing the selected clothing item, high quality, professional photography"
        
        scenario_prompts = {
            "montagna": "in a mountain setting with snow and trees, winter atmosphere",
            "spiaggia": "on a beautiful beach with sand and ocean, summer atmosphere",
            "città": "in an urban city setting, modern architecture, street style",
            "festa": "at a party or celebration, festive atmosphere, elegant setting",
            "lavoro": "in a professional office environment, business casual",
            "casual": "in a casual everyday setting, natural lighting"
        }
        
        if scenario and scenario.lower() in scenario_prompts:
            return f"{base_prompt}, {scenario_prompts[scenario.lower()]}"
        
        return base_prompt


banana_pro_service = BananaProService()

