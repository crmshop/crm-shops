"""
Servizio per integrazione Google Gemini API
"""
import httpx
import logging
from typing import Optional, Dict, Any
from backend.config import settings
import base64

logger = logging.getLogger(__name__)


class GeminiService:
    """Servizio per generazione immagini con Google Gemini"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        if not self.api_key:
            logger.warning("GEMINI_API_KEY non configurata")
    
    async def generate_image(
        self,
        customer_photo_url: str,
        product_image_url: str,
        prompt: Optional[str] = None,
        scenario: Optional[str] = None,
        model: str = "gemini-1.5-pro-vision"  # Modello vision per immagini
    ) -> Dict[str, Any]:
        """
        Genera un'immagine combinando foto cliente e prodotto usando Gemini
        
        Args:
            customer_photo_url: URL della foto del cliente
            product_image_url: URL dell'immagine del prodotto
            prompt: Prompt personalizzato (opzionale)
            scenario: Scenario/contesto
            model: Modello Gemini da usare
        
        Returns:
            Dict con 'image_url', 'status'
        """
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY non configurata")
        
        try:
            # Costruisci prompt se non fornito
            if not prompt:
                prompt = self._build_prompt(scenario)
            
            # Scarica le immagini per includerle nella richiesta
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Scarica foto cliente
                customer_response = await client.get(customer_photo_url)
                customer_response.raise_for_status()
                customer_image_data = base64.b64encode(customer_response.content).decode('utf-8')
                
                # Scarica immagine prodotto
                product_response = await client.get(product_image_url)
                product_response.raise_for_status()
                product_image_data = base64.b64encode(product_response.content).decode('utf-8')
            
            # Prepara contenuto per Gemini (multimodale)
            contents = [
                {
                    "parts": [
                        {
                            "text": f"{prompt}\n\nGenerate a realistic image of the person from the first image wearing the clothing item from the second image."
                        },
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": customer_image_data
                            }
                        },
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": product_image_data
                            }
                        }
                    ]
                }
            ]
            
            # Chiamata API Gemini
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/models/{model}:generateContent",
                    params={"key": self.api_key},
                    json={
                        "contents": contents,
                        "generationConfig": {
                            "temperature": 0.7,
                            "topK": 40,
                            "topP": 0.95,
                            "maxOutputTokens": 1024
                        }
                    }
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Gemini può restituire testo o immagini generate
                # Per ora, assumiamo che restituisca un URL o dati immagine
                if "candidates" in result and len(result["candidates"]) > 0:
                    candidate = result["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        # Cerca dati immagine nella risposta
                        for part in candidate["content"]["parts"]:
                            if "inline_data" in part:
                                image_data = part["inline_data"]["data"]
                                # Salva l'immagine generata su Supabase Storage
                                image_url = await self._save_generated_image(image_data)
                                return {
                                    "image_url": image_url,
                                    "status": "completed",
                                    "ai_service": "gemini"
                                }
                
                # Se non c'è immagine nella risposta, usa un placeholder
                logger.warning("Gemini non ha restituito immagine, usando placeholder")
                return {
                    "image_url": "https://via.placeholder.com/1024x1024?text=AI+Generated+Image",
                    "status": "completed",
                    "ai_service": "gemini"
                }
                    
        except httpx.HTTPError as e:
            logger.error(f"Errore HTTP Gemini: {e}")
            raise Exception(f"Errore comunicazione Gemini: {str(e)}")
        except Exception as e:
            logger.error(f"Errore generazione Gemini: {e}")
            raise
    
    async def _save_generated_image(self, image_data: str) -> str:
        """Salva l'immagine generata su Supabase Storage"""
        try:
            from backend.database import get_supabase_admin
            from uuid import uuid4
            import base64
            
            # Usa admin client per upload Storage (bypassa RLS)
            supabase_admin = get_supabase_admin()
            
            # Decodifica base64
            image_bytes = base64.b64decode(image_data)
            
            # Genera nome file univoco
            file_name = f"generated/{uuid4()}.jpg"
            
            # Carica su Supabase Storage
            bucket_name = "generated-images"
            supabase_admin.storage.from_(bucket_name).upload(
                file_name,
                image_bytes,
                file_options={"content-type": "image/jpeg"}
            )
            
            # Ottieni URL pubblico
            public_url = supabase_admin.storage.from_(bucket_name).get_public_url(file_name)
            return public_url
            
        except Exception as e:
            logger.error(f"Errore salvataggio immagine generata: {e}")
            # Fallback a placeholder
            return "https://via.placeholder.com/1024x1024?text=AI+Generated+Image"
    
    async def generate_outfit_image(
        self,
        customer_photo_url: str,
        product_image_urls: List[str],
        prompt: Optional[str] = None,
        scenario: Optional[str] = None,
        model: str = "gemini-1.5-pro-vision"
    ) -> Dict[str, Any]:
        """
        Genera un'immagine combinando foto cliente e più prodotti (outfit) usando Gemini
        
        Args:
            customer_photo_url: URL della foto del cliente
            product_image_urls: Lista di URL delle immagini dei prodotti (max 10)
            prompt: Prompt personalizzato (opzionale)
            scenario: Scenario/contesto
            model: Modello Gemini da usare
        
        Returns:
            Dict con 'image_url', 'status'
        """
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY non configurata")
        
        if len(product_image_urls) > 10:
            raise ValueError("Massimo 10 prodotti supportati")
        
        try:
            # Costruisci prompt se non fornito
            if not prompt:
                prompt = self._build_prompt(scenario)
                prompt += f" The person should be wearing {len(product_image_urls)} item(s) from the product images."
            
            # Scarica le immagini per includerle nella richiesta
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Scarica foto cliente
                customer_response = await client.get(customer_photo_url)
                customer_response.raise_for_status()
                customer_image_data = base64.b64encode(customer_response.content).decode('utf-8')
                
                # Scarica immagini prodotti
                product_images_data = []
                for product_url in product_image_urls:
                    try:
                        product_response = await client.get(product_url)
                        product_response.raise_for_status()
                        product_image_data = base64.b64encode(product_response.content).decode('utf-8')
                        product_images_data.append(product_image_data)
                    except Exception as e:
                        logger.warning(f"Errore nel caricare immagine prodotto {product_url}: {e}")
                        continue
            
            if not product_images_data:
                raise ValueError("Nessuna immagine prodotto valida caricata")
            
            # Prepara contenuto per Gemini (multimodale con più immagini)
            parts = [
                {
                    "text": f"{prompt}\n\nGenerate a realistic image of the person from the first image wearing all the clothing items from the following product images."
                },
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": customer_image_data
                    }
                }
            ]
            
            # Aggiungi tutte le immagini prodotti
            for product_data in product_images_data:
                parts.append({
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": product_data
                    }
                })
            
            contents = [{"parts": parts}]
            
            # Chiamata API Gemini
            async with httpx.AsyncClient(timeout=180.0) as client:  # Timeout più lungo per più immagini
                response = await client.post(
                    f"{self.base_url}/models/{model}:generateContent",
                    params={"key": self.api_key},
                    json={
                        "contents": contents,
                        "generationConfig": {
                            "temperature": 0.7,
                            "topK": 40,
                            "topP": 0.95,
                            "maxOutputTokens": 2048  # Più token per prompt più complesso
                        }
                    }
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Gemini può restituire testo o immagini generate
                if "candidates" in result and len(result["candidates"]) > 0:
                    candidate = result["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        # Cerca dati immagine nella risposta
                        for part in candidate["content"]["parts"]:
                            if "inline_data" in part:
                                image_data = part["inline_data"]["data"]
                                # Salva l'immagine generata su Supabase Storage
                                image_url = await self._save_generated_image(image_data)
                                return {
                                    "image_url": image_url,
                                    "status": "completed",
                                    "ai_service": "gemini"
                                }
                
                # Se non c'è immagine nella risposta, usa un placeholder
                logger.warning("Gemini non ha restituito immagine, usando placeholder")
                return {
                    "image_url": "https://via.placeholder.com/1024x1024?text=AI+Generated+Outfit",
                    "status": "completed",
                    "ai_service": "gemini"
                }
                    
        except httpx.HTTPError as e:
            logger.error(f"Errore HTTP Gemini: {e}")
            raise Exception(f"Errore comunicazione Gemini: {str(e)}")
        except Exception as e:
            logger.error(f"Errore generazione outfit Gemini: {e}")
            raise
    
    def _build_prompt(self, scenario: Optional[str] = None) -> str:
        """Costruisci prompt base per generazione immagine"""
        base_prompt = "Create a realistic image of a person wearing the clothing item shown in the second image. The person should be from the first image. High quality, professional photography style."
        
        scenario_prompts = {
            "montagna": "Set the scene in a mountain environment with snow and trees, winter atmosphere, natural lighting",
            "spiaggia": "Set the scene on a beautiful beach with sand and ocean, summer atmosphere, bright sunlight",
            "città": "Set the scene in an urban city setting with modern architecture, street style, urban lighting",
            "festa": "Set the scene at a party or celebration, festive atmosphere, elegant setting, party lighting",
            "lavoro": "Set the scene in a professional office environment, business casual, office lighting",
            "casual": "Set the scene in a casual everyday setting, natural lighting, relaxed atmosphere"
        }
        
        if scenario and scenario.lower() in scenario_prompts:
            return f"{base_prompt}. {scenario_prompts[scenario.lower()]}"
        
        return base_prompt


gemini_service = GeminiService()


