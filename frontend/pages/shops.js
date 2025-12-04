// Gestione negozi per negozianti
// Usa namespace per evitare conflitti se script caricato più volte
(function() {
    'use strict';
    
    // Verifica se già inizializzato
    if (window.shopsPageInitialized) {
        return;
    }
    window.shopsPageInitialized = true;
    
// Usa API_BASE_URL globale da app.js o fallback
const getApiBaseUrl = () => window.API_BASE_URL || window.CONFIG?.API_BASE_URL || 'http://localhost:8000';

// Helper per chiamate API
async function apiCall(endpoint, options = {}) {
    const token = localStorage.getItem('crm_token');
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    try {
        const response = await fetch(`${getApiBaseUrl()}${endpoint}`, {
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

// Carica lista negozi
async function loadShops() {
    try {
        const user = JSON.parse(localStorage.getItem('crm_user') || '{}');
        if (!user.id) {
            console.error('Utente non autenticato');
            return [];
        }
        
        const data = await apiCall(`/api/shops/?owner_id=${user.id}`);
        renderShops(data.shops || []);
        return data.shops || [];
    } catch (error) {
        console.error('Errore caricamento negozi:', error);
        document.getElementById('shops-list').innerHTML = 
            `<p class="error">Errore nel caricamento negozi: ${error.message}</p>`;
        return [];
    }
}

// Renderizza lista negozi
function renderShops(shops) {
    const container = document.getElementById('shops-list');
    if (!container) return;
    
    if (shops.length === 0) {
        container.innerHTML = '<p class="empty-state">Nessun negozio trovato. Crea il tuo primo negozio!</p>';
        return;
    }
    
    container.innerHTML = shops.map(shop => `
        <div class="shop-card">
            <h4>${shop.name || 'Negozio senza nome'}</h4>
            ${shop.description ? `<p>${shop.description}</p>` : ''}
            ${shop.address ? `<p>📍 ${shop.address}</p>` : ''}
            ${shop.phone ? `<p>📞 ${shop.phone}</p>` : ''}
            ${shop.email ? `<p>✉️ ${shop.email}</p>` : ''}
            <div class="shop-actions">
                <button class="btn btn-secondary" onclick="editShop('${shop.id}')">Modifica</button>
                <button class="btn btn-danger" onclick="deleteShop('${shop.id}')">Elimina</button>
            </div>
        </div>
    `).join('');
}

// Mostra form creazione negozio
function showCreateShopForm() {
    const user = JSON.parse(localStorage.getItem('crm_user') || '{}');
    if (!user.id) {
        window.showError('Devi essere autenticato per creare un negozio');
        return;
    }
    
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.id = 'create-shop-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Nuovo Negozio</h3>
                <button class="close-btn" onclick="closeModal('create-shop-modal')">&times;</button>
            </div>
            <div class="modal-body">
                <form id="create-shop-form">
                    <div class="form-group">
                        <label for="shop-name">Nome Negozio *</label>
                        <input type="text" id="shop-name" required>
                    </div>
                    <div class="form-group">
                        <label for="shop-description">Descrizione</label>
                        <textarea id="shop-description" rows="3"></textarea>
                    </div>
                    <div class="form-group">
                        <label for="shop-address">Indirizzo</label>
                        <input type="text" id="shop-address">
                    </div>
                    <div class="form-group">
                        <label for="shop-phone">Telefono</label>
                        <input type="tel" id="shop-phone">
                    </div>
                    <div class="form-group">
                        <label for="shop-email">Email</label>
                        <input type="email" id="shop-email">
                    </div>
                    <div class="form-group">
                        <label for="shop-website">Sito Web</label>
                        <input type="url" id="shop-website">
                    </div>
                    <div class="form-actions">
                        <button type="button" class="btn btn-secondary" onclick="closeModal('create-shop-modal')">Annulla</button>
                        <button type="submit" class="btn btn-primary">Crea Negozio</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    document.getElementById('create-shop-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await createShop(user.id);
    });
}

// Crea nuovo negozio
async function createShop(ownerId) {
    try {
        const shopData = {
            owner_id: ownerId,
            name: document.getElementById('shop-name').value,
            description: document.getElementById('shop-description').value || null,
            address: document.getElementById('shop-address').value || null,
            phone: document.getElementById('shop-phone').value || null,
            email: document.getElementById('shop-email').value || null,
            website: document.getElementById('shop-website').value || null
        };
        
        await apiCall('/api/shops/', {
            method: 'POST',
            body: JSON.stringify(shopData)
        });
        
        window.showSuccess('Negozio creato con successo!');
        closeModal('create-shop-modal');
        loadShops();
    } catch (error) {
        window.showError('Errore nella creazione del negozio: ' + error.message);
    }
}

// Modifica negozio
function editShop(shopId) {
    // TODO: Implementare modifica negozio
    window.showError('Funzionalità di modifica non ancora implementata');
}

// Elimina negozio
async function deleteShop(shopId) {
    if (!confirm('Sei sicuro di voler eliminare questo negozio?')) {
        return;
    }
    
    try {
        await apiCall(`/api/shops/${shopId}`, {
            method: 'DELETE'
        });
        
        window.showSuccess('Negozio eliminato con successo!');
        loadShops();
    } catch (error) {
        window.showError('Errore nell\'eliminazione del negozio: ' + error.message);
    }
}

// Helper per chiudere modale
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.remove();
    }
}

// Esporta funzioni per uso globale
window.loadShops = loadShops;
window.showCreateShopForm = showCreateShopForm;
window.editShop = editShop;
window.deleteShop = deleteShop;
window.closeModal = closeModal;

// Carica negozi all'avvio se siamo nella dashboard
if (window.location.pathname === '/dashboard') {
    setTimeout(() => {
        const shopsTab = document.getElementById('shop-tab-shops');
        if (shopsTab && shopsTab.classList.contains('active')) {
            loadShops();
        }
    }, 500);
}

