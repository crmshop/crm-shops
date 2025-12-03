"""
Configurazione database e Supabase
"""
from supabase import create_client, Client
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

# Inizializza client Supabase
supabase: Client | None = None


def init_supabase() -> Client:
    """Inizializza e restituisce il client Supabase"""
    global supabase
    
    if supabase is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            raise ValueError(
                "SUPABASE_URL e SUPABASE_KEY devono essere configurate nelle variabili d'ambiente"
            )
        
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        logger.info("Client Supabase inizializzato correttamente")
    
    return supabase


def get_supabase() -> Client:
    """Ottiene il client Supabase (lazy initialization)"""
    if supabase is None:
        return init_supabase()
    return supabase


def test_connection() -> bool:
    """Testa la connessione a Supabase"""
    try:
        client = get_supabase()
        # Prova una query semplice per verificare la connessione
        # (ad esempio, ottenere informazioni sul progetto)
        return True
    except Exception as e:
        logger.error(f"Errore connessione Supabase: {e}")
        return False
