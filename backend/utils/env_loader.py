"""
Utility per caricare variabili d'ambiente in modo sicuro
"""
import os
from typing import Optional
from backend.config import settings
import logging

logger = logging.getLogger(__name__)


def get_env_var(key: str, default: Optional[str] = None, required: bool = False) -> str:
    """
    Ottiene una variabile d'ambiente con validazione
    
    Args:
        key: Nome della variabile d'ambiente
        default: Valore di default se non trovata
        required: Se True, solleva errore se mancante
    
    Returns:
        Valore della variabile d'ambiente
    """
    value = os.getenv(key, default)
    
    if required and not value:
        raise ValueError(f"Variabile d'ambiente richiesta mancante: {key}")
    
    return value


def validate_required_env_vars() -> dict:
    """
    Valida che tutte le variabili d'ambiente richieste siano presenti
    
    Returns:
        dict con stato di validazione per ogni variabile
    """
    required_vars = {
        "SUPABASE_URL": settings.SUPABASE_URL,
        "SUPABASE_KEY": settings.SUPABASE_KEY,
    }
    
    optional_vars = {
        "SUPABASE_SERVICE_KEY": settings.SUPABASE_SERVICE_KEY,
        "BANANA_PRO_API_KEY": settings.BANANA_PRO_API_KEY,
        "GEMINI_API_KEY": settings.GEMINI_API_KEY,
        "SECRET_KEY": settings.SECRET_KEY,
    }
    
    validation = {
        "required": {},
        "optional": {},
        "all_valid": True
    }
    
    # Valida variabili richieste
    for key, value in required_vars.items():
        is_valid = bool(value)
        validation["required"][key] = {
            "present": is_valid,
            "value": "***" if is_valid else None
        }
        if not is_valid:
            validation["all_valid"] = False
            logger.warning(f"⚠️  Variabile richiesta mancante: {key}")
    
    # Valida variabili opzionali
    for key, value in optional_vars.items():
        validation["optional"][key] = {
            "present": bool(value),
            "value": "***" if value else None
        }
    
    return validation


def print_env_status():
    """Stampa lo stato delle variabili d'ambiente"""
    validation = validate_required_env_vars()
    
    print("\n" + "="*50)
    print("📋 Stato Variabili d'Ambiente")
    print("="*50)
    
    print("\n✅ Variabili Richieste:")
    for key, status in validation["required"].items():
        icon = "✅" if status["present"] else "❌"
        print(f"  {icon} {key}: {'Configurata' if status['present'] else 'MANCANTE'}")
    
    print("\n⚙️  Variabili Opzionali:")
    for key, status in validation["optional"].items():
        icon = "✅" if status["present"] else "⚪"
        print(f"  {icon} {key}: {'Configurata' if status['present'] else 'Non configurata'}")
    
    print("\n" + "="*50)
    
    if validation["all_valid"]:
        print("✅ Tutte le variabili richieste sono configurate!")
    else:
        print("❌ Alcune variabili richieste sono mancanti!")
        print("   Configura le variabili mancanti prima di avviare l'applicazione.")
    
    print("="*50 + "\n")




