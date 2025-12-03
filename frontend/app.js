// Frontend principale per CRM Shops
const API_BASE_URL = 'http://localhost:8000';

// Router semplice
const router = {
    routes: {},
    
    addRoute(path, handler) {
        this.routes[path] = handler;
    },
    
    navigate(path) {
        window.history.pushState({}, '', path);
        this.handleRoute();
    },
    
    handleRoute() {
        const path = window.location.pathname || '/';
        const handler = this.routes[path] || this.routes['/'];
        if (handler) {
            handler();
        }
    }
};

// Inizializza router
window.addEventListener('popstate', () => router.handleRoute());

// Route principale
router.addRoute('/', () => {
    document.getElementById('main-content').innerHTML = `
        <div class="welcome">
            <h2>Benvenuto in CRM Shops</h2>
            <p>Sistema CRM per negozi con AI generativa per visualizzazione abbigliamento</p>
        </div>
    `;
});

// API helper
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Verifica connessione API
async function checkAPI() {
    try {
        const data = await apiCall('/health');
        console.log('API Status:', data);
    } catch (error) {
        console.error('API non raggiungibile:', error);
    }
}

// Inizializza app
document.addEventListener('DOMContentLoaded', () => {
    router.handleRoute();
    checkAPI();
});









