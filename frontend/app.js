// Frontend principale per CRM Shops
const API_BASE_URL = 'http://localhost:8000';

// Stato applicazione
const state = {
    user: null,
    token: null
};

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
document.addEventListener('click', (e) => {
    if (e.target.matches('[data-route]')) {
        e.preventDefault();
        router.navigate(e.target.getAttribute('data-route'));
    }
});

// API helper
async function apiCall(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (state.token) {
        headers['Authorization'] = `Bearer ${state.token}`;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers,
            ...options
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Errore sconosciuto' }));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }
        
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
        console.log('✅ API Status:', data);
        return true;
    } catch (error) {
        console.error('❌ API non raggiungibile:', error);
        showError('API non raggiungibile. Assicurati che il backend sia avviato.');
        return false;
    }
}

// Gestione autenticazione
function saveAuth(user, token) {
    state.user = user;
    state.token = token;
    localStorage.setItem('crm_user', JSON.stringify(user));
    localStorage.setItem('crm_token', token);
    updateNav();
}

function clearAuth() {
    state.user = null;
    state.token = null;
    localStorage.removeItem('crm_user');
    localStorage.removeItem('crm_token');
    updateNav();
}

function loadAuth() {
    const user = localStorage.getItem('crm_user');
    const token = localStorage.getItem('crm_token');
    if (user && token) {
        state.user = JSON.parse(user);
        state.token = token;
        updateNav();
    }
}

function updateNav() {
    const isAuthenticated = !!state.user;
    document.getElementById('nav-login').style.display = isAuthenticated ? 'none' : 'inline';
    document.getElementById('nav-register').style.display = isAuthenticated ? 'none' : 'inline';
    document.getElementById('nav-dashboard').style.display = isAuthenticated ? 'inline' : 'none';
    document.getElementById('nav-products').style.display = isAuthenticated ? 'inline' : 'none';
    document.getElementById('nav-logout').style.display = isAuthenticated ? 'inline' : 'none';
}

// Utility UI
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    document.getElementById('main-content').prepend(errorDiv);
    setTimeout(() => errorDiv.remove(), 5000);
}

function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.textContent = message;
    document.getElementById('main-content').prepend(successDiv);
    setTimeout(() => successDiv.remove(), 3000);
}

// Route: Home
router.addRoute('/', () => {
    document.getElementById('main-content').innerHTML = `
        <div class="welcome">
            <h2>Benvenuto in CRM Shops</h2>
            <p>Sistema CRM per negozi con AI generativa per visualizzazione abbigliamento</p>
            <div class="features">
                <div class="feature-card">
                    <h3>👤 Gestione Clienti</h3>
                    <p>Carica foto dei clienti e gestisci i loro profili</p>
                </div>
                <div class="feature-card">
                    <h3>🛍️ Catalogo Prodotti</h3>
                    <p>Gestisci il tuo catalogo prodotti con categorie e metadati</p>
                </div>
                <div class="feature-card">
                    <h3>🎨 Outfit Personalizzati</h3>
                    <p>Crea outfit combinando diversi capi</p>
                </div>
                <div class="feature-card">
                    <h3>🤖 AI Generativa</h3>
                    <p>Genera immagini AI dei clienti che indossano i tuoi capi</p>
                </div>
            </div>
            ${!state.user ? `
                <div class="cta">
                    <a href="#" data-route="/register" class="btn btn-primary">Inizia Ora</a>
                    <a href="#" data-route="/login" class="btn btn-secondary">Accedi</a>
                </div>
            ` : `
                <div class="cta">
                    <a href="#" data-route="/dashboard" class="btn btn-primary">Vai alla Dashboard</a>
                </div>
            `}
        </div>
    `;
});

// Route: Login
router.addRoute('/login', () => {
    document.getElementById('main-content').innerHTML = `
        <div class="auth-form">
            <h2>Accedi</h2>
            <form id="login-form">
                <div class="form-group">
                    <label for="login-email">Email</label>
                    <input type="email" id="login-email" required>
                </div>
                <div class="form-group">
                    <label for="login-password">Password</label>
                    <input type="password" id="login-password" required>
                </div>
                <button type="submit" class="btn btn-primary">Accedi</button>
            </form>
            <p>Non hai un account? <a href="#" data-route="/register">Registrati</a></p>
        </div>
    `;
    
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        try {
            const data = await apiCall('/api/auth/login', {
                method: 'POST',
                body: JSON.stringify({
                    email: document.getElementById('login-email').value,
                    password: document.getElementById('login-password').value
                })
            });
            
            saveAuth(data.user, data.access_token);
            showSuccess('Login avvenuto con successo!');
            router.navigate('/dashboard');
        } catch (error) {
            showError(error.message);
        }
    });
});

// Route: Register
router.addRoute('/register', () => {
    document.getElementById('main-content').innerHTML = `
        <div class="auth-form">
            <h2>Registrati</h2>
            <form id="register-form">
                <div class="form-group">
                    <label for="register-email">Email</label>
                    <input type="email" id="register-email" required>
                </div>
                <div class="form-group">
                    <label for="register-password">Password</label>
                    <input type="password" id="register-password" required>
                </div>
                <div class="form-group">
                    <label for="register-role">Ruolo</label>
                    <select id="register-role" required>
                        <option value="cliente">Cliente</option>
                        <option value="negoziante">Negozio</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="register-name">Nome Completo (opzionale)</label>
                    <input type="text" id="register-name">
                </div>
                <button type="submit" class="btn btn-primary">Registrati</button>
            </form>
            <p>Hai già un account? <a href="#" data-route="/login">Accedi</a></p>
        </div>
    `;
    
    document.getElementById('register-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        try {
            const data = await apiCall('/api/auth/register', {
                method: 'POST',
                body: JSON.stringify({
                    email: document.getElementById('register-email').value,
                    password: document.getElementById('register-password').value,
                    role: document.getElementById('register-role').value,
                    full_name: document.getElementById('register-name').value || null
                })
            });
            
            showSuccess('Registrazione completata! Controlla la tua email per verificare l\'account.');
            setTimeout(() => router.navigate('/login'), 2000);
        } catch (error) {
            showError(error.message);
        }
    });
});

// Route: Dashboard
router.addRoute('/dashboard', () => {
    if (!state.user) {
        router.navigate('/login');
        return;
    }
    
    const isShopOwner = state.user.role === 'negoziante';
    
    document.getElementById('main-content').innerHTML = `
        <div class="dashboard">
            <h2>Dashboard - ${state.user.full_name || state.user.email}</h2>
            <p>Ruolo: <strong>${state.user.role}</strong></p>
            
            ${isShopOwner ? `
                <div class="dashboard-section">
                    <h3>Gestione Negozio</h3>
                    <div class="dashboard-actions">
                        <a href="#" data-route="/shops" class="btn btn-primary">I Miei Negozi</a>
                        <a href="#" data-route="/products" class="btn btn-primary">Gestisci Prodotti</a>
                    </div>
                </div>
            ` : `
                <div class="dashboard-section">
                    <h3>Area Cliente</h3>
                    <div class="dashboard-actions">
                        <a href="#" data-route="/photos" class="btn btn-primary">Le Mie Foto</a>
                        <a href="#" data-route="/outfits" class="btn btn-primary">I Miei Outfit</a>
                    </div>
                </div>
            `}
        </div>
    `;
});

// Route: Products
router.addRoute('/products', async () => {
    if (!state.user || state.user.role !== 'negoziante') {
        router.navigate('/dashboard');
        return;
    }
    
    try {
        const data = await apiCall('/api/products/');
        const products = data.products || [];
        
        document.getElementById('main-content').innerHTML = `
            <div class="products-page">
                <h2>Gestione Prodotti</h2>
                <button class="btn btn-primary" onclick="showCreateProductForm()">+ Nuovo Prodotto</button>
                <div id="products-list" class="products-grid">
                    ${products.length === 0 ? '<p>Nessun prodotto. Crea il primo prodotto!</p>' : 
                        products.map(p => `
                            <div class="product-card">
                                <h3>${p.name}</h3>
                                <p><strong>Categoria:</strong> ${p.category}</p>
                                ${p.price ? `<p><strong>Prezzo:</strong> €${p.price}</p>` : ''}
                                ${p.available ? '<span class="badge badge-success">Disponibile</span>' : '<span class="badge badge-danger">Non disponibile</span>'}
                            </div>
                        `).join('')
                    }
                </div>
            </div>
        `;
    } catch (error) {
        showError('Errore nel caricamento prodotti: ' + error.message);
    }
});

// Logout
document.addEventListener('click', async (e) => {
    if (e.target.id === 'nav-logout') {
        e.preventDefault();
        try {
            await apiCall('/api/auth/logout', { method: 'POST' });
        } catch (error) {
            console.error('Errore logout:', error);
        }
        clearAuth();
        showSuccess('Logout avvenuto con successo');
        router.navigate('/');
    }
});

// Inizializza app
document.addEventListener('DOMContentLoaded', async () => {
    loadAuth();
    await checkAPI();
    router.handleRoute();
});
