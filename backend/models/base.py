"""
Base per modelli database
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from backend.config import settings
from backend.models.database import Base
import logging

logger = logging.getLogger(__name__)

# Crea engine SQLAlchemy
engine = None
SessionLocal = None


def init_db():
    """Inizializza connessione database"""
    global engine, SessionLocal
    
    if not settings.DATABASE_URL:
        logger.warning("DATABASE_URL non configurata, usando Supabase client invece di SQLAlchemy")
        return None
    
    try:
        engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            echo=settings.DEBUG
        )
        SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
        logger.info("Database engine inizializzato")
        return SessionLocal
    except Exception as e:
        logger.error(f"Errore inizializzazione database: {e}")
        return None


def get_db():
    """Ottiene sessione database (dependency injection per FastAPI)"""
    if SessionLocal is None:
        init_db()
    
    if SessionLocal is None:
        return None
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Crea tutte le tabelle (solo per sviluppo, usa migrazioni in produzione)"""
    if engine is None:
        init_db()
    
    if engine is None:
        logger.error("Impossibile creare tabelle: engine non inizializzato")
        return False
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelle create con successo")
        return True
    except Exception as e:
        logger.error(f"Errore creazione tabelle: {e}")
        return False



