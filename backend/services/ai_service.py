"""
Servizio per generazione immagini AI
Supporta Banana Pro e Google Gemini
"""
from typing import Optional, Dict, Any
from backend.config import settings
import httpx
import logging
import base64
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)


class AIService:
    """Classe base per servizi AI"""
    
    def __init__(self):
        self.banana_pro_key = settings.BANANA_PRO_API_KEY
        self.gemini_key = settings.GEMINI_API_KEY
    
    async def generate_image(
        self,
        customer_photo_url: str,
        product_image_url: Optional[str] = None,
        outfit_product_urls: Optional[list] = None,
        prompt: Optional[str] = None,
        scenario: Optional[str] = None,
        service: str = "banana_pro"
    ) -> Dict[str, Any]:
        """
        Genera un'immagine combinando foto cliente e prodotto/outfit
        
        Args:
            customer_photo_url: URL della foto del cliente
            product_image_url: URL dell'immagine del prodotto (opzionale)
            outfit_product_urls: Lista di URL prodotti per outfit (opzionale)
            prompt: Prompt personalizzato (opzionale)
            scenario: Scenario/contesto (opzionale)
            service: Servizio da usare ('banana_pro' o 'gemini')
        
        Returns:
            Dict con 'image_url', 'prompt_used', 'ai_service'
        """
        if service == "banana_pro":
            return await self._generate_with_banana_pro(
                customer_photo_url, product_image_url, outfit_product_urls, prompt, scenario
            )
        elif service == "gemini":
            return await self._generate_with_gemini(
                customer_photo_url, product_image_url, outfit_product_urls, prompt, scenario
            )
        else:
            raise ValueError(f"Servizio AI non supportato: {service}")
    
    async def _generate_with_banana_pro(
        self,
        customer_photo_url: str,
        product_image_url: Optional[str] = None,
        outfit_product_urls: Optional[list] = None,
        prompt: Optional[str] = None,
        scenario: Optional[str] = None
    ) -> Dict[str, Any]:
        """Genera immagine usando Banana Pro"""
        # TODO: Implementare chiamata reale a Banana Pro API
        # Per ora restituisce un placeholder
        
        if not self.banana_pro_key:
            logger.warning("Banana Pro API key non configurata, usando placeholder")
            return {
                "image_url": "https://placeholder.com/banana-pro-generated.jpg",
                "prompt_used": prompt or "Generate image of person wearing product",
                "ai_service": "banana_pro",
                "status": "placeholder"
            }
        
        # Placeholder per implementazione futura
        logger.info("Chiamata Banana Pro (placeholder)")
        
        return {
            "image_url": "https://placeholder.com/banana-pro-generated.jpg",
            "prompt_used": prompt or "Generate image of person wearing product",
            "ai_service": "banana_pro",
            "status": "placeholder"
        }
    
    async def _generate_with_gemini(
        self,
        customer_photo_url: str,
        product_image_url: Optional[str] = None,
        outfit_product_urls: Optional[list] = None,
        prompt: Optional[str] = None,
        scenario: Optional[str] = None
    ) -> Dict[str, Any]:
        """Genera immagine usando Google Gemini"""
        # TODO: Implementare chiamata reale a Gemini API
        
        if not self.gemini_key:
            logger.warning("Gemini API key non configurata, usando placeholder")
            return {
                "image_url": "https://placeholder.com/gemini-generated.jpg",
                "prompt_used": prompt or "Generate image of person wearing product",
                "ai_service": "gemini",
                "status": "placeholder"
            }
        
        # Placeholder per implementazione futura
        logger.info("Chiamata Gemini (placeholder)")
        
        return {
            "image_url": "https://placeholder.com/gemini-generated.jpg",
            "prompt_used": prompt or "Generate image of person wearing product",
            "ai_service": "gemini",
            "status": "placeholder"
        }
    
    def build_prompt(
        self,
        product_category: Optional[str] = None,
        product_style: Optional[str] = None,
        scenario: Optional[str] = None,
        base_prompt: Optional[str] = None
    ) -> str:
        """Costruisce un prompt personalizzato per la generazione"""
        if base_prompt:
            return base_prompt
        
        prompt_parts = ["Generate a realistic image of a person wearing"]
        
        if product_category:
            prompt_parts.append(f"a {product_category}")
        
        if product_style:
            prompt_parts.append(f"in {product_style} style")
        
        if scenario:
            prompt_parts.append(f"in a {scenario} setting")
        
        prompt_parts.append(". The person should look natural and the clothing should fit perfectly.")
        
        return " ".join(prompt_parts)


# Istanza globale del servizio AI
ai_service = AIService()

