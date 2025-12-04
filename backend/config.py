"""
Configurazione applicazione
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pydantic import field_validator
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Impostazioni applicazione"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # Ignora campi extra nel .env
    )
    
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    
    # Database
    DATABASE_URL: str = ""
    
    # AI Services
    BANANA_PRO_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    
    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS - Default origins per sviluppo
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5500"
    ]
    
    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v):
        """Parser per ALLOWED_ORIGINS da stringa separata da virgola"""
        # Se è già una lista, restituiscila così com'è
        if isinstance(v, list):
            return v
        
        # Se è una stringa, parsala
        if isinstance(v, str):
            # Se è vuota, usa i default
            if not v.strip():
                return [
                    "http://localhost:3000",
                    "http://localhost:8080",
                    "http://localhost:5500"
                ]
            # Rimuovi spazi e filtra stringhe vuote
            origins = [origin.strip() for origin in v.split(",") if origin.strip()]
            # Se dopo il parsing è vuota, usa i default
            if not origins:
                return [
                    "http://localhost:3000",
                    "http://localhost:8080",
                    "http://localhost:5500"
                ]
            return origins
        
        # Se è None o altro tipo, usa i default
        return [
            "http://localhost:3000",
            "http://localhost:8080",
            "http://localhost:5500"
        ]
    
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

