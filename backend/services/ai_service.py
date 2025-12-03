"""
Servizio principale per l'integrazione con AI generativa (Banana Pro, Google Gemini)
"""
import logging
from typing import Optional, Dict, Any
from backend.services.banana_pro import banana_pro_service
from backend.services.gemini import gemini_service

logger = logging.getLogger(__name__)


class AIService:
    """Servizio principale per generazione immagini AI"""
    
    def __init__(self):
        logger.info("Servizio AI inizializzato")
        self.banana_pro = banana_pro_service
        self.gemini = gemini_service

    async def generate_image_with_product(
        self,
        customer_photo_url: str,
        product_image_url: str,
        prompt: Optional[str] = None,
        scenario: Optional[str] = None,
        ai_model: Optional[str] = "gemini"  # Default: Gemini
    ) -> Dict[str, Any]:
        """
        Genera un'immagine di un cliente che indossa un prodotto usando l'AI.
        
        Args:
            customer_photo_url: URL della foto del cliente
            product_image_url: URL dell'immagine del prodotto
            prompt: Prompt personalizzato (opzionale)
            scenario: Scenario/contesto (montagna, spiaggia, etc.)
            ai_model: Modello AI da usare ('banana_pro' o 'gemini')
        
        Returns:
            Dict con 'image_url', 'status', 'ai_service'
        """
        logger.info(f"Generazione immagine AI richiesta con modello: {ai_model}")
        logger.info(f"Foto cliente: {customer_photo_url}")
        logger.info(f"Immagine prodotto: {product_image_url}")
        logger.info(f"Prompt: {prompt}, Scenario: {scenario}")

        try:
            # Seleziona il servizio AI
            if ai_model == "banana_pro":
                if not self.banana_pro.api_key:
                    logger.warning("Banana Pro API key non configurata, uso Gemini")
                    ai_model = "gemini"
                else:
                    result = await self.banana_pro.generate_image(
                        customer_photo_url=customer_photo_url,
                        product_image_url=product_image_url,
                        prompt=prompt,
                        scenario=scenario
                    )
                    return result
            
            if ai_model == "gemini":
                if not self.gemini.api_key:
                    logger.warning("Gemini API key non configurata, uso placeholder")
                    return {
                        "image_url": "https://via.placeholder.com/1024x1024?text=AI+Generated+Image+Placeholder",
                        "status": "placeholder",
                        "ai_service": "none",
                        "error": "Gemini API key non configurata"
                    }
                
                result = await self.gemini.generate_image(
                    customer_photo_url=customer_photo_url,
                    product_image_url=product_image_url,
                    prompt=prompt,
                    scenario=scenario
                )
                return result
            
            # Fallback a placeholder se modello non riconosciuto
            logger.warning(f"Modello AI '{ai_model}' non riconosciuto, uso placeholder")
            return {
                "image_url": "https://via.placeholder.com/1024x1024?text=AI+Generated+Image+Placeholder",
                "status": "placeholder",
                "ai_service": "none",
                "error": f"Modello '{ai_model}' non supportato"
            }
            
        except Exception as e:
            logger.error(f"Errore generazione immagine AI: {e}")
            # Restituisci placeholder in caso di errore
            return {
                "image_url": "https://via.placeholder.com/1024x1024?text=Error+Generating+Image",
                "status": "error",
                "ai_service": ai_model,
                "error": str(e)
            }

    def build_prompt(
        self,
        product_category: Optional[str] = None,
        product_style: Optional[str] = None,
        scenario: Optional[str] = None
    ) -> str:
        """
        Costruisci un prompt per la generazione immagine
        
        Args:
            product_category: Categoria prodotto (vestiti, scarpe, accessori)
            product_style: Stile prodotto
            scenario: Scenario/contesto
        
        Returns:
            Prompt formattato
        """
        base_prompt = "A person wearing"
        
        if product_category:
            base_prompt += f" {product_category}"
        if product_style:
            base_prompt += f" in {product_style} style"
        
        scenario_prompts = {
            "montagna": "in a mountain setting with snow and trees, winter atmosphere",
            "spiaggia": "on a beautiful beach with sand and ocean, summer atmosphere",
            "città": "in an urban city setting, modern architecture",
            "festa": "at a party or celebration, festive atmosphere",
            "lavoro": "in a professional office environment",
            "casual": "in a casual everyday setting"
        }
        
        if scenario and scenario.lower() in scenario_prompts:
            base_prompt += f", {scenario_prompts[scenario.lower()]}"
        
        base_prompt += ". High quality, professional photography, realistic lighting"
        
        return base_prompt


ai_service = AIService()
