// Frontend principale per CRM Shops
// Carica configurazione (deve essere incluso dopo config.js)
const API_BASE_URL = window.CONFIG?.API_BASE_URL || 'http://localhost:8000';
const AUTH_TOKEN_KEY = window.CONFIG?.AUTH_TOKEN_KEY || 'crm_shops_auth_token';
const USER_ROLE_KEY = window.CONFIG?.USER_ROLE_KEY || 'crm_shops_user_role';

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
                <div class="dashboard-negoziante">
                    <h3>Area Negozio</h3>
                    <p>Gestisci i tuoi negozi, prodotti e clienti.</p>
                    
                    <div class="dashboard-tabs">
                        <button class="tab-btn active" data-tab="shops">I Miei Negozi</button>
                        <button class="tab-btn" data-tab="products">Prodotti</button>
                        <button class="tab-btn" data-tab="customers">Clienti</button>
                        <button class="tab-btn" data-tab="stats">Statistiche</button>
                    </div>
                    
                    <div id="shop-tab-shops" class="tab-content active">
                        <div class="section-header">
                            <h4>I Miei Negozi</h4>
                            <button class="btn btn-primary" data-action="create-shop">+ Nuovo Negozio</button>
                        </div>
                        <div id="shops-list">
                            <p class="empty-state">Caricamento negozi...</p>
                        </div>
                    </div>
                    
                    <div id="shop-tab-products" class="tab-content">
                        <div class="section-header">
                            <h4>Gestione Prodotti</h4>
                            <button class="btn btn-primary" data-action="create-product">+ Nuovo Prodotto</button>
                        </div>
                        <div id="products-list" class="products-grid">
                            <div class="loading">Caricamento prodotti...</div>
                        </div>
                    </div>
                    
                    <div id="shop-tab-customers" class="tab-content">
                        <div class="section-header">
                            <h4>Gestione Clienti</h4>
                            <button class="btn btn-primary" data-action="create-customer">+ Nuovo Cliente</button>
                        </div>
                        <div id="customers-list" class="customers-grid">
                            <div class="loading">Caricamento clienti...</div>
                        </div>
                    </div>
                    
                    <div id="shop-tab-stats" class="tab-content">
                        <div id="stats-content">
                            <p class="empty-state">Seleziona un negozio per vedere le statistiche</p>
                        </div>
                    </div>
                </div>
                
                <script>
                    // Carica script pagine negoziante
                    (function() {
                        function loadScript(src, callback) {
                            if (document.querySelector('script[src="' + src + '"]')) {
                                if (callback) callback();
                                return;
                            }
                            const script = document.createElement('script');
                            script.src = src;
                            script.onload = callback;
                            document.head.appendChild(script);
                        }
                        
                        // Carica tutti gli script in parallelo e poi inizializza
                        Promise.all([
                            new Promise(resolve => loadScript('pages/shops.js', resolve)),
                            new Promise(resolve => loadScript('pages/products.js', resolve)),
                            new Promise(resolve => loadScript('pages/shop_customers.js', resolve)),
                            new Promise(resolve => loadScript('pages/shop_stats.js', resolve))
                        ]).then(() => {
                            // Attendi un momento per assicurarsi che le funzioni siano esportate
                            setTimeout(() => {
                                console.log('✅ Script caricati, funzioni disponibili:', {
                                    showCreateShopForm: !!window.showCreateShopForm,
                                    showCreateProductForm: !!window.showCreateProductForm,
                                    showCreateCustomerForm: !!window.showCreateCustomerForm,
                                    loadShops: !!window.loadShops,
                                    loadProducts: !!window.loadProducts,
                                    loadCustomers: !!window.loadCustomers
                                });
                                
                                // Dopo che tutti gli script sono caricati, inizializza
                                if (window.loadShops) window.loadShops();
                                
                                // Riconfigura event delegation dopo caricamento script
                                setupEventDelegation();
                            }, 300);
                        }).catch(err => {
                            console.error('❌ Errore caricamento script:', err);
                        });
                    })();
                </script>
            ` : `
                <div class="dashboard-cliente">
                    <h3>Area Cliente</h3>
                    <p>Qui potrai gestire le tue foto, i tuoi outfit e le immagini generate.</p>
                    
                    <div class="dashboard-tabs">
                        <button class="tab-btn active" data-tab="photos">Le Mie Foto</button>
                        <button class="tab-btn" data-tab="outfits">I Miei Outfit</button>
                        <button class="tab-btn" data-tab="generated">Immagini Generate</button>
                    </div>
                    
                    <div id="tab-photos" class="tab-content active">
                        <div class="section-header">
                            <h4>Le Mie Foto</h4>
                            <button class="btn btn-primary" data-action="upload-photo">+ Carica Foto</button>
                        </div>
                        <div id="photos-list" class="photos-grid">
                            <div class="loading">Caricamento foto...</div>
                        </div>
                    </div>
                    
                    <div id="tab-outfits" class="tab-content">
                        <div class="section-header">
                            <h4>I Miei Outfit</h4>
                            <button class="btn btn-primary" data-action="create-outfit">+ Crea Outfit</button>
                        </div>
                        <div id="outfits-list">
                            <p class="empty-state">Funzionalità outfit in sviluppo...</p>
                        </div>
                    </div>
                    
                    <div id="tab-generated" class="tab-content">
                        <div class="section-header">
                            <h4>Immagini Generate</h4>
                            <button class="btn btn-primary" data-action="generate-image">+ Genera Immagine AI</button>
                        </div>
                        <div id="generated-images-list" class="generated-images-grid">
                            <div class="loading">Caricamento immagini...</div>
                        </div>
                    </div>
                </div>
                
                <script>
                    // Carica script pagine
                    (function() {
                        function loadScript(src, callback) {
                            if (document.querySelector('script[src="' + src + '"]')) {
                                if (callback) callback();
                                return;
                            }
                            const script = document.createElement('script');
                            script.src = src;
                            script.onload = callback;
                            document.head.appendChild(script);
                        }
                        
                        loadScript('pages/customer_photos.js', () => {
                            if (window.loadCustomerPhotos) window.loadCustomerPhotos();
                        });
                        loadScript('pages/generated_images.js', () => {
                            if (window.loadGeneratedImages) window.loadGeneratedImages();
                        });
                    })();
                </script>
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
    
    document.getElementById('main-content').innerHTML = `
        <div class="products-page">
            <h2>Gestione Prodotti</h2>
            <button class="btn btn-primary" data-action="create-product">+ Nuovo Prodotto</button>
            <div id="products-list" class="products-grid">
                <div class="loading">Caricamento prodotti...</div>
            </div>
        </div>
    `;
    
    // Carica script prodotti se non già caricato
    if (!window.productsLoaded) {
        const script = document.createElement('script');
        script.src = 'pages/products.js';
        script.onload = () => {
            window.productsLoaded = true;
            loadProducts();
        };
        document.head.appendChild(script);
    } else {
        loadProducts();
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

// Tab Management per cliente
function showTab(tabName) {
    // Nascondi tutti i tab content
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Rimuovi active da tutti i tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Mostra il tab selezionato
    const selectedTab = document.getElementById(`tab-${tabName}`);
    const selectedBtn = Array.from(document.querySelectorAll('.tab-btn')).find(
        btn => btn.textContent.includes(getTabTitle(tabName))
    );
    
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    if (selectedBtn) {
        selectedBtn.classList.add('active');
    }
}

function getTabTitle(tabName) {
    const titles = {
        'photos': 'Le Mie Foto',
        'outfits': 'I Miei Outfit',
        'generated': 'Immagini Generate'
    };
    return titles[tabName] || '';
}

// Utility per messaggi
function showSuccess(message) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'success-message show';
    msgDiv.textContent = message;
    const mainContent = document.getElementById('main-content');
    if (mainContent) {
        mainContent.insertBefore(msgDiv, mainContent.firstChild);
        setTimeout(() => msgDiv.remove(), 5000);
    }
}

function showError(message) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'error-message show';
    msgDiv.textContent = message;
    const mainContent = document.getElementById('main-content');
    if (mainContent) {
        mainContent.insertBefore(msgDiv, mainContent.firstChild);
        setTimeout(() => msgDiv.remove(), 5000);
    }
}

// Event delegation globale per gestire click su elementi dinamici
function setupEventDelegation() {
    // Rimuovi listener precedenti se esistono
    if (window._actionClickHandler) {
        document.removeEventListener('click', window._actionClickHandler);
    }
    if (window._tabClickHandler) {
        document.removeEventListener('click', window._tabClickHandler);
    }
    
    // Gestore per action buttons
    window._actionClickHandler = function(e) {
        const action = e.target.getAttribute('data-action');
        if (!action) return;
        
        // Se la funzione non è disponibile, attendi e riprova
        function tryAction(actionName, funcName, retries = 3, maxRetries = 3) {
            if (window[funcName]) {
                window[funcName]();
                return true;
            } else if (retries > 0) {
                // Attendi un po' e riprova (gli script potrebbero essere ancora in caricamento)
                setTimeout(() => {
                    tryAction(actionName, funcName, retries - 1, maxRetries);
                }, 200);
                return false;
            } else {
                console.warn(`${funcName} non ancora caricata dopo ${maxRetries} tentativi`);
                if (window.showError) {
                    window.showError(`Funzionalità non ancora disponibile. Attendi qualche secondo e riprova.`);
                } else {
                    alert(`Funzionalità non ancora disponibile. Attendi qualche secondo e riprova.`);
                }
                return false;
            }
        }
        
        switch(action) {
            case 'create-shop':
                tryAction('create-shop', 'showCreateShopForm');
                break;
            case 'create-product':
                tryAction('create-product', 'showCreateProductForm');
                break;
            case 'create-customer':
                tryAction('create-customer', 'showCreateCustomerForm');
                break;
            case 'create-outfit':
                tryAction('create-outfit', 'showCreateOutfitForm');
                break;
            case 'generate-image':
                tryAction('generate-image', 'showGenerateImageForm');
                break;
            case 'upload-photo':
                tryAction('upload-photo', 'showUploadPhotoForm');
                break;
        }
    };
    
    // Gestore per tab buttons
    window._tabClickHandler = function(e) {
        const tabAction = e.target.getAttribute('data-tab');
        if (!tabAction) return;
        
        if (e.target.closest('.dashboard-negoziante')) {
            if (window.showShopTab) {
                window.showShopTab(tabAction);
            }
        } else if (e.target.closest('.dashboard-cliente')) {
            if (window.showTab) {
                window.showTab(tabAction);
            }
        }
    };
    
    document.addEventListener('click', window._actionClickHandler);
    document.addEventListener('click', window._tabClickHandler);
}

// Tab Management per negoziante
function showShopTab(tabName) {
    document.querySelectorAll('#shop-tab-' + tabName.split('-')[0] + ' ~ .tab-content, .tab-content[id^="shop-tab-"]').forEach(tab => {
        if (tab.id.startsWith('shop-tab-')) {
            tab.classList.remove('active');
        }
    });
    
    document.querySelectorAll('.dashboard-negoziante .tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    const selectedTab = document.getElementById(`shop-tab-${tabName}`);
    const selectedBtn = Array.from(document.querySelectorAll('.dashboard-negoziante .tab-btn')).find(
        btn => {
            const titles = {
                'shops': 'I Miei Negozi',
                'products': 'Prodotti',
                'customers': 'Clienti'
            };
            return btn.textContent.includes(titles[tabName] || '');
        }
    );
    
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    if (selectedBtn) {
        selectedBtn.classList.add('active');
    }
    
    // Carica dati quando si cambia tab
    if (tabName === 'shops' && window.loadShops) {
        window.loadShops();
    } else if (tabName === 'products' && window.loadProducts) {
        window.loadProducts();
    } else if (tabName === 'customers' && window.loadCustomers) {
        window.loadCustomers();
    } else if (tabName === 'stats') {
        // Carica statistiche del primo negozio disponibile
        // In futuro, permettere selezione negozio
        if (window.loadShopsForStats) {
            window.loadShopsForStats();
        }
    }
}

// Esporta funzioni globali
window.showTab = showTab;
window.showShopTab = showShopTab;
window.showSuccess = showSuccess;
window.showError = showError;
window.setupEventDelegation = setupEventDelegation;

// Inizializza event delegation all'avvio
setupEventDelegation();

// Inizializza app
document.addEventListener('DOMContentLoaded', async () => {
    loadAuth();
    await checkAPI();
    router.handleRoute();
});
