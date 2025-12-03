"""
Backend principale per CRM Shops
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database import init_supabase, test_connection
import logging

# Configurazione logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CRM Shops API",
    description="API per sistema CRM negozi con AI generativa",
    version="0.1.0",
    debug=settings.DEBUG
)

# Configurazione CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Evento eseguito all'avvio dell'applicazione"""
    logger.info("Avvio applicazione CRM Shops")
    
    # Valida variabili d'ambiente in produzione
    if settings.ENVIRONMENT == "production":
        from backend.utils.env_loader import validate_required_env_vars
        validation = validate_required_env_vars()
        if not validation["all_valid"]:
            logger.error("❌ Variabili d'ambiente richieste mancanti in produzione!")
            logger.error("L'applicazione potrebbe non funzionare correttamente.")

    # Inizializza Supabase se le credenziali sono configurate
    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        try:
            init_supabase()
            if test_connection():
                logger.info("✅ Connessione Supabase stabilita")
            else:
                logger.warning("⚠️ Connessione Supabase non riuscita")
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione Supabase: {e}")
    else:
        logger.warning("⚠️ Credenziali Supabase non configurate")

# Importa route
from backend.routes import auth, products, outfits, shops, customer_photos, generated_images, customers, shop_stats

# Registra route
app.include_router(auth.router)
app.include_router(shops.router)
app.include_router(products.router)
app.include_router(outfits.router)
app.include_router(customer_photos.router)
app.include_router(generated_images.router)
app.include_router(customers.router)
app.include_router(shop_stats.router)


@app.get("/")
async def root():
    """Endpoint root per verificare che l'API funzioni"""
    return {
        "message": "CRM Shops API",
        "status": "running",
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    supabase_status = "not_configured"
    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        supabase_status = "connected" if test_connection() else "error"
    
    return {
        "status": "healthy",
        "supabase": supabase_status,
        "environment": settings.ENVIRONMENT
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)









