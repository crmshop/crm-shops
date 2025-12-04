"""
Configurazione database e Supabase
"""
from supabase import create_client, Client
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

# Inizializza client Supabase (anon key per operazioni utente)
supabase: Client | None = None

# Inizializza client Supabase Admin (service key per operazioni backend)
supabase_admin: Client | None = None


def init_supabase() -> Client:
    """Inizializza e restituisce il client Supabase con chiave anonima"""
    global supabase
    
    if supabase is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            raise ValueError(
                "SUPABASE_URL e SUPABASE_KEY devono essere configurate nelle variabili d'ambiente"
            )
        
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        logger.info("Client Supabase inizializzato correttamente")
    
    return supabase


def init_supabase_admin() -> Client:
    """Inizializza e restituisce il client Supabase Admin con service role key
    Questo client bypassa le RLS policies e deve essere usato solo per operazioni backend
    come upload su Storage, migrazioni, etc.
    """
    global supabase_admin
    
    if supabase_admin is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
            raise ValueError(
                "SUPABASE_URL e SUPABASE_SERVICE_KEY devono essere configurate nelle variabili d'ambiente"
            )
        
        supabase_admin = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
        logger.info("Client Supabase Admin inizializzato correttamente")
    
    return supabase_admin


def get_supabase() -> Client:
    """Ottiene il client Supabase (dependency injection per FastAPI)
    Usa la chiave anonima - rispetta le RLS policies
    """
    if supabase is None:
        return init_supabase()
    return supabase


def get_supabase_admin() -> Client:
    """Ottiene il client Supabase Admin (per operazioni backend)
    Usa la service role key - bypassa le RLS policies
    Usare SOLO per operazioni backend come upload Storage, migrazioni, etc.
    """
    if supabase_admin is None:
        return init_supabase_admin()
    return supabase_admin


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

