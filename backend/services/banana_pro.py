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
    # Prova prima il formato nuovo (google.genai)
    from google import genai
    from google.genai import types
    USE_NEW_API = True
    GENAI_AVAILABLE = True
except ImportError:
    try:
        # Fallback al formato vecchio (google.generativeai)
        import google.generativeai as genai
        USE_NEW_API = False
        GENAI_AVAILABLE = True
    except ImportError:
        USE_NEW_API = False
        GENAI_AVAILABLE = False

logger = logging.getLogger(__name__)

if not GENAI_AVAILABLE:
    logger.warning("google.genai non disponibile. Installa con: pip install google-generativeai")


class BananaProService:
    """Servizio per generazione immagini con Banana Pro"""
    
    def __init__(self):
        self.api_key = settings.BANANA_PRO_API_KEY
        self.client = None
        self.model = None
        self.model_name = None
        self.use_new_api = False
        
        if not GENAI_AVAILABLE:
            raise ImportError("google.genai non disponibile. Installa con: pip install google-generativeai")
        
        if not self.api_key:
            logger.warning("BANANA_PRO_API_KEY non configurata")
            logger.warning("   Ottieni la API key da Google AI Studio: https://aistudio.google.com/")
            return
        
        # Usa il formato corretto in base alla versione disponibile
        try:
            if USE_NEW_API:
                # Formato nuovo: google.genai.Client
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                # Usa modello per generazione immagini con generate_content
                # gemini-2.5-flash-image supporta generate_content con input immagini
                self.model_name = "gemini-2.5-flash-image"  # Modello per generazione immagini
                self.use_new_api = True
                logger.info(f"✅ Google Generative AI configurato (nuovo formato) con modello {self.model_name}")
            else:
                # Formato vecchio: google.generativeai
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash-image')
                self.model_name = "gemini-2.5-flash-image"
                self.use_new_api = False
                logger.info(f"✅ Google Generative AI configurato (formato legacy) con modello {self.model_name}")
        except Exception as e:
            logger.error(f"❌ Errore configurazione Google Generative AI: {e}")
            raise
    
    async def generate_image(
        self,
        customer_photo_urls: list[str],  # Lista di URL foto cliente (fino a 3)
        product_image_urls: list[str],  # Lista di URL immagini prodotto (fino a 10)
        prompt: Optional[str] = None,
        scenario: Optional[str] = None,
        model: str = "gemini-2.5-flash-image"  # Modello per generazione immagini con input immagini
    ) -> Dict[str, Any]:
        """
        Genera un'immagine combinando foto cliente e prodotti
        
        Args:
            customer_photo_urls: Lista di URL delle foto del cliente (fino a 3)
            product_image_urls: Lista di URL delle immagini dei prodotti (fino a 10)
            prompt: Prompt personalizzato (opzionale)
            scenario: Scenario/contesto (montagna, spiaggia, etc.)
            model: Modello AI da usare
        
        Returns:
            Dict con 'image_url', 'job_id', 'status'
        """
        if not self.api_key:
            raise ValueError("BANANA_PRO_API_KEY non configurata")
        
        # Verifica che client o model siano inizializzati
        if not self.client and not self.model:
            raise ValueError("Google Generative AI non inizializzato correttamente. Verifica BANANA_PRO_API_KEY.")
        
        # Validazione input
        if not customer_photo_urls or len(customer_photo_urls) == 0:
            raise ValueError("Almeno una foto cliente è richiesta")
        if len(customer_photo_urls) > 3:
            raise ValueError("Massimo 3 foto cliente consentite")
        if not product_image_urls or len(product_image_urls) == 0:
            raise ValueError("Almeno un prodotto è richiesto")
        if len(product_image_urls) > 10:
            raise ValueError("Massimo 10 prodotti consentiti")
        
        try:
            # Pulisci URL rimuovendo parametri di query
            def clean_url(url: str) -> str:
                if not url:
                    return url
                url = url.split('?')[0]
                return url.strip()
            
            # Pulisci tutti gli URL
            customer_photo_urls_clean = [clean_url(url) for url in customer_photo_urls if url]
            product_image_urls_clean = [clean_url(url) for url in product_image_urls if url]
            
            logger.info(f"📥 Download immagini per Banana Pro:")
            logger.info(f"   Foto cliente: {len(customer_photo_urls_clean)} immagini")
            logger.info(f"   Prodotti: {len(product_image_urls_clean)} immagini")
            
            # Scarica tutte le immagini
            import httpx
            customer_images_bytes = []
            product_images_bytes = []
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Scarica tutte le foto cliente
                for i, url in enumerate(customer_photo_urls_clean, 1):
                    try:
                        response = await client.get(url)
                        response.raise_for_status()
                        customer_images_bytes.append(response.content)
                        logger.info(f"✅ Foto cliente {i}/{len(customer_photo_urls_clean)} scaricata: {len(response.content)} bytes")
                    except Exception as e:
                        logger.error(f"❌ Errore download foto cliente {i}: {e}")
                        raise Exception(f"Impossibile scaricare foto cliente {i}: {str(e)}")
                
                # Scarica tutte le immagini prodotto
                for i, url in enumerate(product_image_urls_clean, 1):
                    try:
                        response = await client.get(url)
                        response.raise_for_status()
                        product_images_bytes.append(response.content)
                        logger.info(f"✅ Immagine prodotto {i}/{len(product_image_urls_clean)} scaricata: {len(response.content)} bytes")
                    except Exception as e:
                        logger.error(f"❌ Errore download immagine prodotto {i}: {e}")
                        raise Exception(f"Impossibile scaricare immagine prodotto {i}: {str(e)}")
            
            # Costruisci prompt se non fornito
            if not prompt:
                prompt = self._build_prompt(scenario)
            
            # Costruisci riferimenti alle immagini nel prompt
            # Foto cliente: {image1}, {image2}, {image3} (fino a 3)
            # Prodotti: {image4}, {image5}, ..., {image13} (fino a 10)
            customer_refs = []
            for i in range(len(customer_images_bytes)):
                customer_refs.append(f"{{image{i+1}}}")
            
            product_refs = []
            start_idx = len(customer_images_bytes) + 1
            for i in range(len(product_images_bytes)):
                product_refs.append(f"{{image{start_idx + i}}}")
            
            # Prepara prompt completo per generazione immagine
            # IMPORTANTE: Usa riferimenti espliciti alle immagini come nel notebook funzionante
            customer_refs_str = ", ".join(customer_refs)
            product_refs_str = ", ".join(product_refs)
            
            full_prompt = (
                f"Immagine professionale che ritrae la persona dalle foto {customer_refs_str} con indossati "
                f"gli articoli di abbigliamento come da immagini {product_refs_str}. "
                f"{prompt} "
                f"Il volto deve essere fedele alle foto così come la forma fisica. "
                f"L'immagine deve essere di alta qualità, stile fotografia professionale con illuminazione e composizione appropriate. "
                f"Tutti gli articoli devono essere visibili e ben indossati dalla persona."
            )
            
            logger.info(f"🚀 Generazione immagine con {self.model_name}")
            logger.info(f"   Foto cliente: {len(customer_images_bytes)} immagini")
            logger.info(f"   Prodotti: {len(product_images_bytes)} immagini")
            logger.info(f"   Prompt: {full_prompt[:200]}...")
            
            # Usa il formato corretto come nel notebook funzionante
            def generate_image_sync():
                """Funzione sincrona per generare immagine (la libreria non è async)"""
                from PIL import Image
                import io
                
                # Converti tutte le immagini bytes in PIL Images
                customer_images = [Image.open(io.BytesIO(img_bytes)) for img_bytes in customer_images_bytes]
                product_images = [Image.open(io.BytesIO(img_bytes)) for img_bytes in product_images_bytes]
                
                # IMPORTANTE: L'ordine delle immagini deve corrispondere ai riferimenti nel prompt
                # Prima tutte le foto cliente, poi tutti i prodotti
                all_images = customer_images + product_images
                
                # Genera immagine usando il formato corretto in base all'API disponibile
                if self.use_new_api:
                    # Formato nuovo: google.genai.Client
                    # Passa prompt con riferimenti espliciti + tutte le immagini nell'ordine corretto
                    contents = [full_prompt] + all_images
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=contents,
                    )
                else:
                    # Formato vecchio: google.generativeai.GenerativeModel
                    contents = [full_prompt] + all_images
                    response = self.model.generate_content(contents)
                
                return response
            
            # Esegui in thread separato per non bloccare l'event loop
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, generate_image_sync)
            
            logger.info(f"   ✅ Risposta ricevuta da Gemini API")
            
            # Estrai immagine dalla risposta usando il formato corretto in base all'API disponibile
            if self.use_new_api:
                # Formato nuovo: response.parts contiene le parti della risposta
                for part in response.parts:
                    if part.text is not None:
                        logger.info(f"   Part contiene testo: {part.text[:200]}...")
                    elif part.inline_data is not None:
                        # Usa as_image() per ottenere l'immagine PIL
                        try:
                            generated_image = part.as_image()
                            
                            # Verifica che l'immagine sia valida
                            if generated_image is None:
                                logger.warning("   ⚠️ as_image() ha restituito None")
                                continue
                            
                            # Verifica che sia una PIL Image con attributo size
                            from PIL import Image
                            if not isinstance(generated_image, Image.Image):
                                logger.warning(f"   ⚠️ as_image() ha restituito tipo non PIL: {type(generated_image)}")
                                # Prova a estrarre i dati direttamente
                                if hasattr(part.inline_data, 'data'):
                                    image_data = part.inline_data.data
                                    
                                    # Converti bytes a stringa se necessario
                                    if isinstance(image_data, bytes):
                                        import base64
                                        image_data_base64 = base64.b64encode(image_data).decode('utf-8')
                                    elif isinstance(image_data, str):
                                        image_data_base64 = image_data
                                    else:
                                        logger.error(f"   ❌ Tipo dati non supportato: {type(image_data)}")
                                        continue
                                    
                                    logger.info(f"   ✅ Trovati dati immagine base64: {len(image_data_base64)} caratteri")
                                    supabase_image_url = await self._save_to_supabase_storage(image_data_base64)
                                    logger.info(f"   ✅ Immagine salvata: {supabase_image_url}")
                                    return {
                                        "image_url": supabase_image_url,
                                        "status": "completed",
                                        "ai_service": "banana_pro"
                                    }
                                continue
                            
                            # Verifica che abbia l'attributo size
                            if not hasattr(generated_image, 'size'):
                                logger.warning(f"   ⚠️ Immagine non ha attributo size: {type(generated_image)}")
                                # Prova a convertire direttamente da inline_data
                                if hasattr(part.inline_data, 'data'):
                                    image_data = part.inline_data.data
                                    
                                    # Converti bytes a stringa se necessario
                                    if isinstance(image_data, bytes):
                                        import base64
                                        image_data_base64 = base64.b64encode(image_data).decode('utf-8')
                                    elif isinstance(image_data, str):
                                        image_data_base64 = image_data
                                    else:
                                        logger.error(f"   ❌ Tipo dati non supportato: {type(image_data)}")
                                        continue
                                    
                                    logger.info(f"   ✅ Trovati dati immagine base64: {len(image_data_base64)} caratteri")
                                    supabase_image_url = await self._save_to_supabase_storage(image_data_base64)
                                    logger.info(f"   ✅ Immagine salvata: {supabase_image_url}")
                                    return {
                                        "image_url": supabase_image_url,
                                        "status": "completed",
                                        "ai_service": "banana_pro"
                                    }
                                continue
                            
                            logger.info(f"   ✅ Trovata immagine generata: {generated_image.size}")
                            
                            # Converti PIL Image in bytes per salvare su Supabase
                            import io
                            image_bytes_io = io.BytesIO()
                            generated_image.save(image_bytes_io, format='PNG')
                            image_bytes = image_bytes_io.getvalue()
                            
                            # Converti bytes in base64 per compatibilità con _save_to_supabase_storage
                            image_data_base64 = base64.b64encode(image_bytes).decode('utf-8')
                            logger.info(f"   Immagine convertita in base64: {len(image_data_base64)} caratteri")
                            
                            # Salva l'immagine su Supabase Storage
                            logger.info(f"   Salvataggio immagine su Supabase Storage...")
                            supabase_image_url = await self._save_to_supabase_storage(image_data_base64)
                            logger.info(f"   ✅ Immagine salvata: {supabase_image_url}")
                            
                            return {
                                "image_url": supabase_image_url,
                                "status": "completed",
                                "ai_service": "banana_pro"
                            }
                        except Exception as e:
                            logger.error(f"   ❌ Errore estrazione immagine: {e}")
                            # Prova fallback: estrai dati direttamente da inline_data
                            if hasattr(part, 'inline_data') and part.inline_data is not None:
                                try:
                                    if hasattr(part.inline_data, 'data'):
                                        image_data = part.inline_data.data
                                        
                                        # Converti bytes a stringa se necessario
                                        if isinstance(image_data, bytes):
                                            import base64
                                            image_data_base64 = base64.b64encode(image_data).decode('utf-8')
                                        elif isinstance(image_data, str):
                                            image_data_base64 = image_data
                                        else:
                                            logger.error(f"   ❌ Tipo dati non supportato: {type(image_data)}")
                                            continue
                                        
                                        logger.info(f"   ✅ Fallback: trovati dati immagine base64: {len(image_data_base64)} caratteri")
                                        supabase_image_url = await self._save_to_supabase_storage(image_data_base64)
                                        logger.info(f"   ✅ Immagine salvata: {supabase_image_url}")
                                        return {
                                            "image_url": supabase_image_url,
                                            "status": "completed",
                                            "ai_service": "banana_pro"
                                        }
                                except Exception as fallback_error:
                                    import traceback
                                    logger.error(f"   ❌ Errore anche nel fallback: {fallback_error}")
                                    logger.error(f"   Traceback: {traceback.format_exc()}")
                            continue
            else:
                # Formato vecchio: response.candidates[0].content.parts
                if response.candidates and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if hasattr(part, 'inline_data') and part.inline_data:
                                # Estrai dati base64 dall'immagine
                                image_data_base64 = part.inline_data.data
                                logger.info(f"   ✅ Trovata immagine generata: {len(image_data_base64)} caratteri base64")
                                
                                # Salva l'immagine su Supabase Storage
                                logger.info(f"   Salvataggio immagine su Supabase Storage...")
                                supabase_image_url = await self._save_to_supabase_storage(image_data_base64)
                                logger.info(f"   ✅ Immagine salvata: {supabase_image_url}")
                                
                                return {
                                    "image_url": supabase_image_url,
                                    "status": "completed",
                                    "ai_service": "banana_pro"
                                }
            
            # Se non c'è immagine nella risposta
            logger.error("⚠️  Gemini API non ha restituito immagine nella risposta")
            logger.error(f"   Numero di parts nella risposta: {len(response.parts) if hasattr(response, 'parts') else 0}")
            raise ValueError(
                "Gemini API non ha restituito un'immagine. "
                f"Verifica che il modello '{self.model_name}' sia disponibile "
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
            image_data: Dati immagine in base64 (stringa) da Google Imagen API OPPURE URL (stringa)
            
        Returns:
            URL pubblico dell'immagine su Supabase Storage
        """
        try:
            from backend.database import get_supabase_admin
            from uuid import uuid4
            import base64
            
            # Usa admin client per upload Storage (bypassa RLS)
            supabase_admin = get_supabase_admin()
            
            # Converti bytes a stringa se necessario
            if isinstance(image_data, bytes):
                image_data = image_data.decode('utf-8')
            
            # Verifica che sia una stringa
            if not isinstance(image_data, str):
                raise ValueError(f"image_data deve essere una stringa o bytes, ricevuto: {type(image_data)}")
            
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
        base_prompt = "Vista di tre quarti, posa naturale"
        
        scenario_prompts = {
            "montagna": "in un ambiente montano con neve e alberi, atmosfera invernale",
            "spiaggia": "su una bella spiaggia con sabbia e oceano, atmosfera estiva",
            "città": "in un ambiente urbano cittadino, architettura moderna, stile street",
            "festa": "a una festa o celebrazione, atmosfera festosa, ambiente elegante",
            "lavoro": "in un ambiente d'ufficio professionale, business casual",
            "casual": "in un ambiente casual quotidiano, illuminazione naturale"
        }
        
        if scenario and scenario.lower() in scenario_prompts:
            return f"{base_prompt}, {scenario_prompts[scenario.lower()]}"
        
        return base_prompt


banana_pro_service = BananaProService()

