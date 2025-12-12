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
        customer_photo_urls: list[str],  # Lista di URL foto cliente (fino a 3)
        product_image_urls: list[str],  # Lista di URL immagini prodotto (fino a 10)
        prompt: Optional[str] = None,
        scenario: Optional[str] = None,
        ai_model: Optional[str] = "banana_pro"  # Default: Banana Pro (Gemini non può generare immagini)
    ) -> Dict[str, Any]:
        """
        Genera un'immagine di un cliente che indossa prodotti usando l'AI.
        
        Args:
            customer_photo_urls: Lista di URL delle foto del cliente (fino a 3)
            product_image_urls: Lista di URL delle immagini dei prodotti (fino a 10)
            prompt: Prompt personalizzato (opzionale)
            scenario: Scenario/contesto (montagna, spiaggia, etc.)
            ai_model: Modello AI da usare ('banana_pro' o 'gemini')
        
        Returns:
            Dict con 'image_url', 'status', 'ai_service'
        """
        logger.info(f"Generazione immagine AI richiesta con modello: {ai_model}")
        logger.info(f"Foto cliente: {len(customer_photo_urls)} immagini")
        logger.info(f"Immagini prodotto: {len(product_image_urls)} immagini")
        logger.info(f"Prompt: {prompt}, Scenario: {scenario}")

        try:
            # Seleziona il servizio AI
            if ai_model == "banana_pro":
                if not self.banana_pro.api_key:
                    logger.warning("Banana Pro API key non configurata, uso Gemini")
                    ai_model = "gemini"
                else:
                    result = await self.banana_pro.generate_image(
                        customer_photo_urls=customer_photo_urls,
                        product_image_urls=product_image_urls,
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
                
                # Gemini non supporta generazione immagini, usa solo la prima foto e prodotto
                result = await self.gemini.generate_image(
                    customer_photo_url=customer_photo_urls[0] if customer_photo_urls else "",
                    product_image_url=product_image_urls[0] if product_image_urls else "",
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
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"❌ Errore generazione immagine AI: {e}")
            logger.error(f"   Traceback completo:\n{error_trace}")
            # Restituisci placeholder in caso di errore, ma includi dettagli dell'errore
            return {
                "image_url": "https://via.placeholder.com/1024x1024?text=Error+Generating+Image",
                "status": "error",
                "ai_service": ai_model,
                "error": str(e),
                "error_details": error_trace  # Includi traceback per debug
            }

    def build_prompt(
        self,
        product_category: Optional[str] = None,
        product_style: Optional[str] = None,
        scenario: Optional[str] = None,
        scenario_details: Optional[List[dict]] = None  # Lista di scenari con dettagli
    ) -> str:
        """
        Costruisci un prompt per la generazione immagine
        
        Args:
            product_category: Categoria prodotto (giacche, blazer, maglieria, felpe&ibridi, camicie, shirty, pantaloni, calzini, short, scarpe, copricapi, accessori)
            product_style: Stile prodotto
            scenario: Scenario/contesto (deprecato, usa scenario_details)
            scenario_details: Lista di scenari con dettagli [{"description": "...", "position": "...", "environment": "...", "lighting": "...", "background": "...", "custom_text": "..."}]
        
        Returns:
            Prompt formattato
        """
        base_prompt = "Immagine professionale che ritrae la persona dalle foto cliente"
        
        if product_category:
            base_prompt += f" con indossato {product_category}"
        if product_style:
            base_prompt += f" in stile {product_style}"
        
        # Se ci sono scenari dettagliati, costruisci il prompt con i dettagli
        if scenario_details and len(scenario_details) > 0:
            scenario_parts = []
            for scenario_detail in scenario_details:
                parts = []
                
                if scenario_detail.get("description"):
                    parts.append(scenario_detail["description"])
                
                if scenario_detail.get("position"):
                    parts.append(f"posizione: {scenario_detail['position']}")
                
                if scenario_detail.get("environment"):
                    parts.append(f"ambiente: {scenario_detail['environment']}")
                
                if scenario_detail.get("lighting"):
                    parts.append(f"illuminazione: {scenario_detail['lighting']}")
                
                if scenario_detail.get("background"):
                    parts.append(f"sfondo: {scenario_detail['background']}")
                
                if scenario_detail.get("custom_text"):
                    parts.append(scenario_detail["custom_text"])
                
                if parts:
                    scenario_parts.append(", ".join(parts))
            
            if scenario_parts:
                base_prompt += ". " + ". ".join(scenario_parts)
        elif scenario:
            # Fallback per scenario semplice (retrocompatibilità)
            scenario_prompts = {
                "montagna": "in un ambiente montano con neve e alberi, atmosfera invernale",
                "spiaggia": "su una bellissima spiaggia con sabbia e oceano, atmosfera estiva",
                "città": "in un ambiente urbano cittadino, architettura moderna",
                "festa": "a una festa o celebrazione, atmosfera festosa",
                "lavoro": "in un ambiente professionale d'ufficio",
                "casual": "in un ambiente casual quotidiano"
            }
            
            if scenario.lower() in scenario_prompts:
                base_prompt += f". {scenario_prompts[scenario.lower()]}"
        
        base_prompt += ". Alta qualità, stile fotografia professionale con illuminazione e composizione appropriate. La persona deve essere chiaramente visibile e gli articoli devono essere ben indossati."
        
        return base_prompt


ai_service = AIService()
