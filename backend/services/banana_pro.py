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
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/generate",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Banana Pro restituisce un job_id, poi bisogna fare polling
                if "job_id" in result:
                    # Polling per ottenere il risultato
                    image_url = await self._poll_job_status(result["job_id"])
                    return {
                        "image_url": image_url,
                        "job_id": result["job_id"],
                        "status": "completed",
                        "ai_service": "banana_pro"
                    }
                elif "image_url" in result:
                    # Risultato immediato
                    return {
                        "image_url": result["image_url"],
                        "status": "completed",
                        "ai_service": "banana_pro"
                    }
                else:
                    raise ValueError(f"Risposta Banana Pro non valida: {result}")
                    
        except httpx.HTTPError as e:
            logger.error(f"Errore HTTP Banana Pro: {e}")
            raise Exception(f"Errore comunicazione Banana Pro: {str(e)}")
        except Exception as e:
            logger.error(f"Errore generazione Banana Pro: {e}")
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

