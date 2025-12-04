// Configurazione frontend
// In produzione, questo file può essere generato dinamicamente o sostituito
// con variabili d'ambiente durante il build

const CONFIG = {
    // URL base dell'API backend
    // In sviluppo: localhost
    // In produzione: URL del backend su Render
    API_BASE_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8000'
        : (window.API_BASE_URL || 'https://crm-shops.onrender.com'),
    
    // Timeout per le richieste API (ms)
    API_TIMEOUT: 30000,
    
    // Chiavi localStorage
    AUTH_TOKEN_KEY: 'crm_shops_auth_token',
    USER_ROLE_KEY: 'crm_shops_user_role',
    USER_DATA_KEY: 'crm_shops_user_data',
    
    // Configurazione paginazione
    ITEMS_PER_PAGE: 20,
    
    // Debug mode
    DEBUG: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
};

// Esporta configurazione globale
window.CONFIG = CONFIG;

// Log configurazione in modalità debug
if (CONFIG.DEBUG) {
    console.log('🔧 Configurazione Frontend:', CONFIG);
}

