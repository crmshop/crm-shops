"""
Route per gestione scenario prompts
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from supabase import Client
from backend.database import get_supabase
from backend.middleware.auth import get_current_shop_owner
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/scenario-prompts", tags=["scenario-prompts"])


class ScenarioPromptCreate(BaseModel):
    shop_id: UUID
    name: str
    description: str  # Descrizione posizione, ambiente, illuminazione, ecc.
    position: Optional[str] = None  # Es: "in piedi", "seduto", "camminando"
    environment: Optional[str] = None  # Es: "interno", "esterno", "spiaggia", "città"
    lighting: Optional[str] = None  # Es: "naturale", "artificiale", "serale"
    background: Optional[str] = None  # Descrizione sfondo


class ScenarioPromptUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    position: Optional[str] = None
    environment: Optional[str] = None
    lighting: Optional[str] = None
    background: Optional[str] = None


@router.get("/")
async def list_scenario_prompts(
    shop_id: Optional[UUID] = None,
    current_user: dict = Depends(get_current_shop_owner),
    supabase: Client = Depends(get_supabase)
):
    """Lista scenario prompts con filtri opzionali"""
    try:
        query = supabase.table("scenario_prompts").select("*")
        
        if shop_id:
            # Verifica che il negozio appartenga al negoziante
            shop_result = supabase.table("shops").select("owner_id").eq("id", str(shop_id)).single().execute()
            if not shop_result.data or shop_result.data["owner_id"] != current_user["id"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Accesso negato a questo negozio"
                )
            query = query.eq("shop_id", str(shop_id))
        else:
            # Se non specificato shop_id, mostra solo scenari dei negozi del negoziante
            shops_result = supabase.table("shops").select("id").eq("owner_id", current_user["id"]).execute()
            shop_ids = [shop["id"] for shop in shops_result.data]
            if shop_ids:
                query = query.in_("shop_id", [str(sid) for sid in shop_ids])
            else:
                return {"scenarios": [], "count": 0}
        
        result = query.execute()
        return {
            "scenarios": result.data,
            "count": len(result.data)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore lista scenario prompts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante il recupero scenario prompts: {str(e)}"
        )


@router.get("/{scenario_id}")
async def get_scenario_prompt(
    scenario_id: UUID,
    current_user: dict = Depends(get_current_shop_owner),
    supabase: Client = Depends(get_supabase)
):
    """Ottieni dettagli di uno scenario prompt"""
    try:
        result = supabase.table("scenario_prompts").select("*").eq("id", str(scenario_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scenario prompt non trovato"
            )
        
        scenario = result.data[0]
        
        # Verifica permessi
        shop_result = supabase.table("shops").select("owner_id").eq("id", scenario["shop_id"]).single().execute()
        if not shop_result.data or shop_result.data["owner_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accesso negato"
            )
        
        return {"scenario": scenario}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore recupero scenario prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante il recupero scenario prompt: {str(e)}"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_scenario_prompt(
    scenario: ScenarioPromptCreate,
    current_user: dict = Depends(get_current_shop_owner),
    supabase: Client = Depends(get_supabase)
):
    """Crea un nuovo scenario prompt"""
    try:
        # Verifica che il negozio appartenga al negoziante
        shop_result = supabase.table("shops").select("owner_id").eq("id", str(scenario.shop_id)).single().execute()
        if not shop_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Negozio non trovato"
            )
        
        if shop_result.data["owner_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Puoi creare scenario prompts solo per i tuoi negozi"
            )
        
        scenario_data = {
            "shop_id": str(scenario.shop_id),
            "name": scenario.name,
            "description": scenario.description,
            "position": scenario.position,
            "environment": scenario.environment,
            "lighting": scenario.lighting,
            "background": scenario.background
        }
        
        result = supabase.table("scenario_prompts").insert(scenario_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Errore durante la creazione dello scenario prompt"
            )
        
        return {
            "message": "Scenario prompt creato con successo",
            "scenario": result.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore creazione scenario prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Errore durante la creazione dello scenario prompt: {str(e)}"
        )


@router.put("/{scenario_id}")
async def update_scenario_prompt(
    scenario_id: UUID,
    scenario: ScenarioPromptUpdate,
    current_user: dict = Depends(get_current_shop_owner),
    supabase: Client = Depends(get_supabase)
):
    """Aggiorna uno scenario prompt"""
    try:
        # Verifica permessi
        existing_result = supabase.table("scenario_prompts").select("shop_id").eq("id", str(scenario_id)).execute()
        if not existing_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scenario prompt non trovato"
            )
        
        shop_result = supabase.table("shops").select("owner_id").eq("id", existing_result.data[0]["shop_id"]).single().execute()
        if not shop_result.data or shop_result.data["owner_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accesso negato"
            )
        
        updates = scenario.dict(exclude_unset=True)
        
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nessun campo da aggiornare"
            )
        
        result = supabase.table("scenario_prompts").update(updates).eq("id", str(scenario_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scenario prompt non trovato"
            )
        
        return {
            "message": "Scenario prompt aggiornato con successo",
            "scenario": result.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore aggiornamento scenario prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante l'aggiornamento dello scenario prompt: {str(e)}"
        )


@router.delete("/{scenario_id}")
async def delete_scenario_prompt(
    scenario_id: UUID,
    current_user: dict = Depends(get_current_shop_owner),
    supabase: Client = Depends(get_supabase)
):
    """Elimina uno scenario prompt"""
    try:
        # Verifica permessi
        existing_result = supabase.table("scenario_prompts").select("shop_id").eq("id", str(scenario_id)).execute()
        if not existing_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scenario prompt non trovato"
            )
        
        shop_result = supabase.table("shops").select("owner_id").eq("id", existing_result.data[0]["shop_id"]).single().execute()
        if not shop_result.data or shop_result.data["owner_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accesso negato"
            )
        
        result = supabase.table("scenario_prompts").delete().eq("id", str(scenario_id)).execute()
        
        return {
            "message": "Scenario prompt eliminato con successo",
            "scenario_id": str(scenario_id)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore eliminazione scenario prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante l'eliminazione dello scenario prompt: {str(e)}"
        )
