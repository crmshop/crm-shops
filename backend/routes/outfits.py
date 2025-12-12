"""
Route per gestione outfit
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from supabase import Client
from backend.database import get_supabase
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/outfits", tags=["outfit"])


class OutfitScenario(BaseModel):
    scenario_prompt_id: UUID
    custom_text: Optional[str] = None  # Testo libero per caratteristiche aggiuntive


class OutfitCreate(BaseModel):
    customer_id: UUID  # ID cliente da shop_customers
    shop_id: UUID
    name: Optional[str] = None
    product_ids: List[UUID]  # Max 10 prodotti
    scenarios: Optional[List[OutfitScenario]] = []  # Max 3 scenari con testo libero


class OutfitResponse(BaseModel):
    id: UUID
    user_id: UUID
    shop_id: UUID
    name: Optional[str]
    product_ids: List[UUID]
    created_at: str


@router.get("/")
async def list_outfits(
    user_id: Optional[UUID] = None,
    shop_id: Optional[UUID] = None,
    supabase: Client = Depends(get_supabase)
):
    """Lista outfit con filtri opzionali"""
    try:
        query = supabase.table("outfits").select(
            "*, outfit_products(product_id), outfit_scenarios(scenario_prompt_id, custom_text)"
        )
        
        if user_id:
            query = query.eq("user_id", str(user_id))
        if shop_id:
            query = query.eq("shop_id", str(shop_id))
        
        result = query.execute()
        
        # Formatta i risultati per includere product_ids e scenari
        outfits = []
        for outfit in result.data:
            outfit_data = {**outfit}
            outfit_data["product_ids"] = [
                op["product_id"] for op in outfit.get("outfit_products", [])
            ]
            outfit_data["scenarios"] = [
                {
                    "scenario_prompt_id": os["scenario_prompt_id"],
                    "custom_text": os.get("custom_text")
                }
                for os in outfit.get("outfit_scenarios", [])
            ]
            if "outfit_products" in outfit_data:
                del outfit_data["outfit_products"]
            if "outfit_scenarios" in outfit_data:
                del outfit_data["outfit_scenarios"]
            outfits.append(outfit_data)
        
        return {
            "outfits": outfits,
            "count": len(outfits)
        }
    except Exception as e:
        logger.error(f"Errore lista outfit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante il recupero outfit: {str(e)}"
        )


@router.get("/{outfit_id}")
async def get_outfit(outfit_id: UUID, supabase: Client = Depends(get_supabase)):
    """Ottieni dettagli di un outfit"""
    try:
        result = supabase.table("outfits").select(
            "*, outfit_products(product_id), outfit_scenarios(scenario_prompt_id, custom_text)"
        ).eq("id", str(outfit_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Outfit non trovato"
            )
        
        outfit = result.data[0]
        outfit["product_ids"] = [
            op["product_id"] for op in outfit.get("outfit_products", [])
        ]
        outfit["scenarios"] = [
            {
                "scenario_prompt_id": os["scenario_prompt_id"],
                "custom_text": os.get("custom_text")
            }
            for os in outfit.get("outfit_scenarios", [])
        ]
        if "outfit_products" in outfit:
            del outfit["outfit_products"]
        if "outfit_scenarios" in outfit:
            del outfit["outfit_scenarios"]
        
        return {"outfit": outfit}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore recupero outfit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante il recupero outfit: {str(e)}"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_outfit(outfit: OutfitCreate, supabase: Client = Depends(get_supabase)):
    """Crea un nuovo outfit"""
    try:
        # Valida numero prodotti (max 10)
        if len(outfit.product_ids) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Puoi selezionare massimo 10 prodotti"
            )
        
        if len(outfit.product_ids) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Seleziona almeno un prodotto"
            )
        
        # Valida numero scenari (max 3)
        scenarios = outfit.scenarios or []
        if len(scenarios) > 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Puoi selezionare massimo 3 scenari"
            )
        
        # Verifica che gli scenari esistano e appartengano al negozio
        if scenarios:
            scenario_ids = [str(s.scenario_prompt_id) for s in scenarios]
            scenarios_result = supabase.table("scenario_prompts").select("*").in_("id", scenario_ids).execute()
            found_scenario_ids = {s["id"] for s in scenarios_result.data}
            
            for scenario in scenarios:
                if str(scenario.scenario_prompt_id) not in found_scenario_ids:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Scenario prompt {scenario.scenario_prompt_id} non trovato"
                    )
                # Verifica che lo scenario appartenga al negozio
                scenario_data = next(s for s in scenarios_result.data if s["id"] == str(scenario.scenario_prompt_id))
                if scenario_data["shop_id"] != str(outfit.shop_id):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Lo scenario {scenario.scenario_prompt_id} non appartiene a questo negozio"
                    )
        
        # Verifica che il cliente appartenga al negozio
        customer_response = supabase.table("shop_customers").select("*").eq("id", str(outfit.customer_id)).eq("shop_id", str(outfit.shop_id)).execute()
        if not customer_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente non trovato per questo negozio"
            )
        
        # Crea l'outfit
        # Nota: la tabella outfits potrebbe avere solo user_id, quindi per ora usiamo NULL
        # In futuro possiamo aggiungere customer_id alla tabella outfits
        outfit_data = {
            "shop_id": str(outfit.shop_id),
            "name": outfit.name,
            "user_id": None  # Per clienti shop_customers non abbiamo user_id
        }
        
        result = supabase.table("outfits").insert(outfit_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Errore durante la creazione dell'outfit"
            )
        
        created_outfit = result.data[0]
        outfit_id = created_outfit["id"]
        
        # Aggiungi i prodotti all'outfit
        if outfit.product_ids:
            outfit_products = [
                {"outfit_id": outfit_id, "product_id": str(pid)}
                for pid in outfit.product_ids
            ]
            supabase.table("outfit_products").insert(outfit_products).execute()
        
        # Aggiungi gli scenari all'outfit
        if scenarios:
            outfit_scenarios = [
                {
                    "outfit_id": outfit_id,
                    "scenario_prompt_id": str(s.scenario_prompt_id),
                    "custom_text": s.custom_text
                }
                for s in scenarios
            ]
            supabase.table("outfit_scenarios").insert(outfit_scenarios).execute()
        
        # Recupera l'outfit completo con i prodotti e scenari
        final_result = supabase.table("outfits").select(
            "*, outfit_products(product_id), outfit_scenarios(scenario_prompt_id, custom_text)"
        ).eq("id", outfit_id).execute()
        
        final_outfit = final_result.data[0]
        final_outfit["product_ids"] = [
            op["product_id"] for op in final_outfit.get("outfit_products", [])
        ]
        final_outfit["scenarios"] = [
            {
                "scenario_prompt_id": os["scenario_prompt_id"],
                "custom_text": os.get("custom_text")
            }
            for os in final_outfit.get("outfit_scenarios", [])
        ]
        if "outfit_products" in final_outfit:
            del final_outfit["outfit_products"]
        if "outfit_scenarios" in final_outfit:
            del final_outfit["outfit_scenarios"]
        
        return {
            "message": "Outfit creato con successo",
            "outfit": final_outfit
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore creazione outfit: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Errore durante la creazione dell'outfit: {str(e)}"
        )


class OutfitUpdate(BaseModel):
    name: Optional[str] = None
    product_ids: Optional[List[UUID]] = None  # Max 10 prodotti
    scenarios: Optional[List[OutfitScenario]] = None  # Max 3 scenari


@router.put("/{outfit_id}")
async def update_outfit(
    outfit_id: UUID,
    outfit_update: OutfitUpdate,
    supabase: Client = Depends(get_supabase)
):
    """Aggiorna un outfit esistente"""
    try:
        # Verifica che l'outfit esista
        existing_outfit = supabase.table("outfits").select("*").eq("id", str(outfit_id)).execute()
        if not existing_outfit.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Outfit non trovato"
            )
        
        outfit = existing_outfit.data[0]
        
        # Aggiorna nome se fornito
        update_data = {}
        if outfit_update.name is not None:
            update_data["name"] = outfit_update.name
        
        if update_data:
            supabase.table("outfits").update(update_data).eq("id", str(outfit_id)).execute()
        
        # Aggiorna prodotti se forniti
        if outfit_update.product_ids is not None:
            # Valida numero prodotti (max 10)
            if len(outfit_update.product_ids) > 10:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Puoi selezionare massimo 10 prodotti"
                )
            
            if len(outfit_update.product_ids) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Seleziona almeno un prodotto"
                )
            
            # Elimina prodotti esistenti
            supabase.table("outfit_products").delete().eq("outfit_id", str(outfit_id)).execute()
            
            # Inserisci nuovi prodotti
            outfit_products = [
                {"outfit_id": str(outfit_id), "product_id": str(pid)}
                for pid in outfit_update.product_ids
            ]
            if outfit_products:
                supabase.table("outfit_products").insert(outfit_products).execute()
        
        # Aggiorna scenari se forniti
        if outfit_update.scenarios is not None:
            # Valida numero scenari (max 3)
            scenarios = outfit_update.scenarios
            if len(scenarios) > 3:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Puoi selezionare massimo 3 scenari"
                )
            
            # Verifica che gli scenari esistano e appartengano al negozio
            if scenarios:
                scenario_ids = [str(s.scenario_prompt_id) for s in scenarios]
                scenarios_result = supabase.table("scenario_prompts").select("*").in_("id", scenario_ids).execute()
                found_scenario_ids = {s["id"] for s in scenarios_result.data}
                
                for scenario in scenarios:
                    if str(scenario.scenario_prompt_id) not in found_scenario_ids:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Scenario prompt {scenario.scenario_prompt_id} non trovato"
                        )
                    # Verifica che lo scenario appartenga al negozio
                    scenario_data = next(s for s in scenarios_result.data if s["id"] == str(scenario.scenario_prompt_id))
                    if scenario_data["shop_id"] != str(outfit["shop_id"]):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Lo scenario {scenario.scenario_prompt_id} non appartiene a questo negozio"
                        )
            
            # Elimina scenari esistenti
            supabase.table("outfit_scenarios").delete().eq("outfit_id", str(outfit_id)).execute()
            
            # Inserisci nuovi scenari
            if scenarios:
                outfit_scenarios = [
                    {
                        "outfit_id": str(outfit_id),
                        "scenario_prompt_id": str(s.scenario_prompt_id),
                        "custom_text": s.custom_text
                    }
                    for s in scenarios
                ]
                supabase.table("outfit_scenarios").insert(outfit_scenarios).execute()
        
        # Recupera l'outfit aggiornato con i prodotti e scenari
        final_result = supabase.table("outfits").select(
            "*, outfit_products(product_id), outfit_scenarios(scenario_prompt_id, custom_text)"
        ).eq("id", str(outfit_id)).execute()
        
        final_outfit = final_result.data[0]
        final_outfit["product_ids"] = [
            op["product_id"] for op in final_outfit.get("outfit_products", [])
        ]
        final_outfit["scenarios"] = [
            {
                "scenario_prompt_id": os["scenario_prompt_id"],
                "custom_text": os.get("custom_text")
            }
            for os in final_outfit.get("outfit_scenarios", [])
        ]
        if "outfit_products" in final_outfit:
            del final_outfit["outfit_products"]
        if "outfit_scenarios" in final_outfit:
            del final_outfit["outfit_scenarios"]
        
        return {
            "message": "Outfit aggiornato con successo",
            "outfit": final_outfit
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore aggiornamento outfit: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Errore durante l'aggiornamento dell'outfit: {str(e)}"
        )


@router.delete("/{outfit_id}")
async def delete_outfit(outfit_id: UUID, supabase: Client = Depends(get_supabase)):
    """Elimina un outfit"""
    try:
        # Le relazioni outfit_products verranno eliminate automaticamente per CASCADE
        result = supabase.table("outfits").delete().eq("id", str(outfit_id)).execute()
        
        return {
            "message": "Outfit eliminato con successo",
            "outfit_id": str(outfit_id)
        }
    except Exception as e:
        logger.error(f"Errore eliminazione outfit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante l'eliminazione dell'outfit: {str(e)}"
        )

