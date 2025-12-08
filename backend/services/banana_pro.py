"""
Servizio per integrazione Banana Pro API
Usa la libreria google.generativeai per generare immagini con Gemini 3 Pro Image Preview
"""
import logging
from typing import Optional, Dict, Any
from backend.config import settings
import base64
import asyncio
import httpx

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

logger = logging.getLogger(__name__)

if not GENAI_AVAILABLE:
    logger.warning("google.generativeai non disponibile. Installa con: pip install google-generativeai")


class BananaProService:
    """Servizio per generazione immagini con Banana Pro"""
    
    def __init__(self):
        self.api_key = settings.BANANA_PRO_API_KEY
        if not GENAI_AVAILABLE:
            raise ImportError("google.generativeai non disponibile. Installa con: pip install google-generativeai")
        
        # Configura Google Generative AI
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('models/gemini-3-pro-image-preview')
        
        if not self.api_key:
            logger.warning("BANANA_PRO_API_KEY non configurata")
            logger.warning("   Ottieni la API key da Google AI Studio: https://aistudio.google.com/")
    
    async def generate_image(
        self,
        customer_photo_url: str,
        product_image_url: str,
        prompt: Optional[str] = None,
        scenario: Optional[str] = None,
        model: str = "gemini-3-pro-image-preview"  # Modello Gemini 3 Pro Image Preview per generazione immagini
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
            
            # Pulisci URL rimuovendo parametri di query
            def clean_url(url: str) -> str:
                if not url:
                    return url
                url = url.split('?')[0]
                return url.strip()
            
            customer_photo_url_clean = clean_url(customer_photo_url)
            product_image_url_clean = clean_url(product_image_url)
            
            logger.info(f"📥 Download immagini per Banana Pro:")
            logger.info(f"   Foto cliente: {customer_photo_url_clean}")
            logger.info(f"   Prodotto: {product_image_url_clean}")
            
            # Scarica le immagini per includerle nella richiesta
            import httpx
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Scarica foto cliente
                try:
                    customer_response = await client.get(customer_photo_url_clean)
                    customer_response.raise_for_status()
                    customer_image_bytes = customer_response.content
                    logger.info(f"✅ Foto cliente scaricata: {len(customer_image_bytes)} bytes")
                except Exception as e:
                    logger.error(f"❌ Errore download foto cliente: {e}")
                    raise Exception(f"Impossibile scaricare foto cliente: {str(e)}")
                
                # Scarica immagine prodotto
                try:
                    product_response = await client.get(product_image_url_clean)
                    product_response.raise_for_status()
                    product_image_bytes = product_response.content
                    logger.info(f"✅ Immagine prodotto scaricata: {len(product_image_bytes)} bytes")
                except Exception as e:
                    logger.error(f"❌ Errore download immagine prodotto: {e}")
                    raise Exception(f"Impossibile scaricare immagine prodotto: {str(e)}")
            
            # Costruisci prompt se non fornito
            if not prompt:
                prompt = self._build_prompt(scenario)
            
            # Prepara prompt completo per generazione immagine
            full_prompt = f"{prompt}\n\nCreate a realistic, high-quality image showing a person from the first photo wearing the clothing item shown in the second photo. The image should be professional photography style with proper lighting and composition."
            
            logger.info(f"🚀 Generazione immagine con Gemini 3 Pro Image Preview")
            logger.info(f"   Prompt: {full_prompt[:200]}...")
            
            # Usa la libreria google.generativeai invece delle chiamate HTTP dirette
            # La libreria gestisce correttamente response_mime_type="image/png"
            def generate_image_sync():
                """Funzione sincrona per generare immagine (la libreria non è async)"""
                import PIL.Image
                import io
                
                # Converti bytes in PIL Image
                customer_image = PIL.Image.open(io.BytesIO(customer_image_bytes))
                product_image = PIL.Image.open(io.BytesIO(product_image_bytes))
                
                # Genera immagine usando la libreria
                response = self.model.generate_content(
                    [
                        full_prompt,
                        customer_image,
                        product_image
                    ],
                    generation_config=genai.types.GenerationConfig(
                        response_mime_type="image/png"
                    )
                )
                
                return response
            
            # Esegui in thread separato per non bloccare l'event loop
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, generate_image_sync)
            
            logger.info(f"   ✅ Risposta ricevuta da Gemini API")
            
            # Estrai immagine dalla risposta (formato della libreria)
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            image_data = part.inline_data.data
                            logger.info(f"   ✅ Trovata immagine generata: {len(image_data)} caratteri base64")
                            
                            # Salva l'immagine su Supabase Storage
                            logger.info(f"   Salvataggio immagine su Supabase Storage...")
                            supabase_image_url = await self._save_to_supabase_storage(image_data)
                            logger.info(f"   ✅ Immagine salvata: {supabase_image_url}")
                            
                            return {
                                "image_url": supabase_image_url,
                                "status": "completed",
                                "ai_service": "banana_pro"
                            }
            
            # Se non c'è immagine nella risposta
            logger.error("⚠️  Gemini API non ha restituito immagine nella risposta")
            raise ValueError(
                "Gemini API non ha restituito un'immagine. "
                "Verifica che il modello 'gemini-3-pro-image-preview' sia disponibile "
                "e che la fatturazione sia attiva sul tuo account Google Cloud."
            )
                    
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
    
    async def _save_to_supabase_storage(self, image_data: str) -> str:
        """
        Salva l'immagine su Supabase Storage
        
        Args:
            image_data: Dati immagine in base64 da Google Imagen API OPPURE URL
            
        Returns:
            URL pubblico dell'immagine su Supabase Storage
        """
        try:
            from backend.database import get_supabase_admin
            from uuid import uuid4
            import base64
            
            # Usa admin client per upload Storage (bypassa RLS)
            supabase_admin = get_supabase_admin()
            
            # Determina se è un URL o base64
            if image_data.startswith("http://") or image_data.startswith("https://"):
                # È un URL - scarica l'immagine
                async with httpx.AsyncClient(timeout=30.0) as client:
                    logger.info(f"📥 Download immagine da banana.dev: {image_data}")
                    response = await client.get(image_data)
                    response.raise_for_status()
                    image_bytes = response.content
                    
                    if not image_bytes or len(image_bytes) == 0:
                        raise ValueError("Immagine scaricata vuota")
                    
                    logger.info(f"✅ Immagine scaricata: {len(image_bytes)} bytes")
            elif image_data.startswith("data:image") or len(image_data) > 100:
                # Probabilmente è base64
                logger.info(f"📥 Decodifica immagine base64 da banana.dev")
                try:
                    # Rimuovi il prefisso data:image se presente
                    if "," in image_data:
                        image_data = image_data.split(",")[1]
                    image_bytes = base64.b64decode(image_data)
                    logger.info(f"✅ Immagine decodificata: {len(image_bytes)} bytes")
                except Exception as e:
                    raise ValueError(f"Errore decodifica base64: {e}")
            else:
                raise ValueError(f"Formato immagine non riconosciuto: {image_data[:50]}...")
            
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

