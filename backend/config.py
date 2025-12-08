"""
Configurazione applicazione
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pydantic import field_validator, computed_field
import os
from dotenv import load_dotenv

load_dotenv()

# Default origins per sviluppo
DEFAULT_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:5500"
]


def parse_origins(value) -> List[str]:
    """Parser robusto per ALLOWED_ORIGINS"""
    if isinstance(value, list):
        return value
    
    if isinstance(value, str):
        if not value.strip():
            return DEFAULT_ORIGINS
        origins = [origin.strip() for origin in value.split(",") if origin.strip()]
        return origins if origins else DEFAULT_ORIGINS
    
    return DEFAULT_ORIGINS


class Settings(BaseSettings):
    """Impostazioni applicazione"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",  # Ignora campi extra nel .env
        env_parse_none_str=True,  # Tratta stringhe vuote come None
        env_prefix=""  # Nessun prefisso per le env vars
    )
    
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    
    # Database
    DATABASE_URL: str = ""
    
    # AI Services
    BANANA_PRO_API_KEY: str = ""  # API key da Google AI Studio per Nano Banana Pro
    GEMINI_API_KEY: str = ""
    
    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS - Usa str invece di List[str] per evitare problemi di parsing Pydantic
    # Mappa ALLOWED_ORIGINS env var a questo campo
    ALLOWED_ORIGINS_STR: str = ""
    
    def get_allowed_origins(self) -> List[str]:
        """Metodo per ottenere ALLOWED_ORIGINS come lista"""
        # Leggi dalla variabile d'ambiente direttamente (Pydantic non mapperà automaticamente)
        env_value = os.getenv("ALLOWED_ORIGINS", "")
        value = self.ALLOWED_ORIGINS_STR or env_value
        return parse_origins(value)
    
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """Property per compatibilità con codice esistente"""
        return self.get_allowed_origins()
    
    def model_post_init(self, __context):
        """Post-init per leggere ALLOWED_ORIGINS dalla env var"""
        # Se ALLOWED_ORIGINS_STR è vuoto, leggi da env var
        if not self.ALLOWED_ORIGINS_STR:
            env_value = os.getenv("ALLOWED_ORIGINS", "")
            if env_value:
                self.ALLOWED_ORIGINS_STR = env_value
    
    @field_validator('DEBUG', mode='before')
    @classmethod
    def parse_debug(cls, v):
        """Parser per DEBUG da stringa"""
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)
    
    @field_validator('PORT', mode='before')
    @classmethod
    def parse_port(cls, v):
        """Parser per PORT"""
        if isinstance(v, str):
            return int(v)
        return v


settings = Settings()

