// Pagina gestione clienti per negozianti
// Usa namespace per evitare conflitti se script caricato più volte
(function() {
    'use strict';
    
    // Verifica se già inizializzato
    if (window.customersPageInitialized) {
        return;
    }
    window.customersPageInitialized = true;
    
let currentCustomers = [];
let currentShops = [];

async function loadCustomers() {
    const container = document.getElementById('customers-list');
    if (!container) {
        console.warn('Container customers-list non trovato');
        return;
    }
    
    try {
        console.log('📥 Caricamento clienti...');
        const data = await window.apiCall('/api/customers/');
        console.log('✅ Clienti caricati:', data);
        currentCustomers = data.customers || data || [];
        renderCustomers();
    } catch (error) {
        console.error('❌ Errore caricamento clienti:', error);
        currentCustomers = [];
        container.innerHTML = `<p class="error">Errore nel caricamento clienti: ${error.message}</p>`;
        if (window.showError) {
            window.showError('Errore nel caricamento clienti: ' + error.message);
        }
    }
}

async function loadShops() {
    try {
        const data = await window.apiCall('/api/shops/');
        currentShops = data.shops || data || [];
        return currentShops;
    } catch (error) {
        console.error('Errore caricamento negozi:', error);
        return [];
    }
}

function renderCustomers() {
    const container = document.getElementById('customers-list');
    if (!container) {
        console.warn('⚠️ Container customers-list non trovato per rendering');
        console.log('🔍 Tentativo di trovare container...');
        // Prova a trovare il container dopo un breve delay
        setTimeout(() => {
            const retryContainer = document.getElementById('customers-list');
            if (retryContainer && currentCustomers.length > 0) {
                console.log('✅ Container trovato al retry, rendering...');
                renderCustomers();
            }
        }, 500);
        return;
    }
    
    console.log('🎨 Rendering clienti:', currentCustomers.length);
    console.log('📋 Dati clienti:', currentCustomers);
    
    if (currentCustomers.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>Nessun cliente registrato.</p>
                <p>Crea il tuo primo cliente!</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = currentCustomers.map(customer => `
        <div class="customer-card">
            <div class="customer-header">
                <h3>${customer.full_name || customer.email}</h3>
                <span class="customer-email">${customer.email}</span>
            </div>
            <div class="customer-info">
                ${customer.phone ? `<p><strong>Telefono:</strong> ${customer.phone}</p>` : ''}
                ${customer.address ? `<p><strong>Indirizzo:</strong> ${customer.address}</p>` : ''}
                ${customer.notes ? `<p><strong>Note:</strong> ${customer.notes}</p>` : ''}
                <p class="customer-date">Registrato: ${new Date(customer.created_at).toLocaleDateString('it-IT')}</p>
            </div>
            <div class="customer-actions">
                <button onclick="viewCustomerPhotos('${customer.id}')" class="btn btn-small">Foto</button>
                <button onclick="editCustomer('${customer.id}')" class="btn btn-small">Modifica</button>
                <button onclick="uploadCustomerPhoto('${customer.id}')" class="btn btn-small btn-primary">+ Foto</button>
            </div>
        </div>
    `).join('');
}

function showCreateCustomerForm() {
    loadShops().then(shops => {
        if (shops.length === 0) {
            showError('Devi prima creare un negozio!');
            return;
        }
        
        const formHTML = `
            <div class="modal" id="customer-modal">
                <div class="modal-content">
                    <span class="close" onclick="closeCustomerModal()">&times;</span>
                    <h2>Nuovo Cliente</h2>
                    <form id="customer-form">
                        <div class="form-group">
                            <label>Negozio *</label>
                            <select id="customer-shop" required>
                                ${shops.map(s => `<option value="${s.id}">${s.name}</option>`).join('')}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Email *</label>
                            <input type="email" id="customer-email" required>
                            <small>Email del cliente (non riceverà email di conferma)</small>
                        </div>
                        <div class="form-group">
                            <label>Nome Completo</label>
                            <input type="text" id="customer-name">
                        </div>
                        <div class="form-group">
                            <label>Telefono</label>
                            <input type="tel" id="customer-phone">
                        </div>
                        <div class="form-group">
                            <label>Indirizzo</label>
                            <input type="text" id="customer-address">
                        </div>
                        <div class="form-group">
                            <label>Note</label>
                            <textarea id="customer-notes" rows="3" placeholder="Note aggiuntive sul cliente..."></textarea>
                        </div>
                        <div class="form-group">
                            <label>Foto Cliente (max 3)</label>
                            <input type="file" id="customer-photos" accept="image/*" multiple>
                            <small>Puoi caricare massimo 3 immagini</small>
                            <div id="customer-photos-preview" class="photos-preview"></div>
                        </div>
                        <button type="submit" class="btn btn-primary">Crea Cliente</button>
                    </form>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', formHTML);
        
        // Gestione preview immagini
        const photosInput = document.getElementById('customer-photos');
        const previewDiv = document.getElementById('customer-photos-preview');
        
        photosInput.addEventListener('change', function(e) {
            const files = Array.from(e.target.files);
            if (files.length > 3) {
                showError('Puoi caricare massimo 3 immagini');
                e.target.value = '';
                previewDiv.innerHTML = '';
                return;
            }
            
            previewDiv.innerHTML = '';
            files.forEach((file, index) => {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.style.width = '100px';
                    img.style.height = '100px';
                    img.style.objectFit = 'cover';
                    img.style.margin = '5px';
                    img.style.borderRadius = '4px';
                    previewDiv.appendChild(img);
                };
                reader.readAsDataURL(file);
            });
        });
        
        document.getElementById('customer-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await createCustomer();
        });
    });
}

async function createCustomer() {
    try {
        const photosInput = document.getElementById('customer-photos');
        const files = Array.from(photosInput.files);
        
        if (files.length > 3) {
            if (window.showError) {
                window.showError('Puoi caricare massimo 3 immagini');
            } else {
                alert('Puoi caricare massimo 3 immagini');
            }
            e.target.value = '';
            previewDiv.innerHTML = '';
            return;
        }
        
        const customerData = {
            shop_id: document.getElementById('customer-shop').value,
            email: document.getElementById('customer-email').value,
            // Nota: I clienti creati dal negoziante NON hanno password/account
            // Rimangono solo nell'area del negozio
            full_name: document.getElementById('customer-name').value || null,
            phone: document.getElementById('customer-phone').value || null,
            address: document.getElementById('customer-address').value || null,
            notes: document.getElementById('customer-notes').value || null
        };
        
        // Crea prima il cliente
        const customerResponse = await window.apiCall('/api/customers/', {
            method: 'POST',
            body: JSON.stringify(customerData)
        });
        
        // Poi carica le immagini se presenti
        if (files.length > 0) {
            const customerId = customerResponse.id;
            for (const file of files) {
                const formData = new FormData();
                formData.append('file', file);
                
                await window.apiCall(`/api/customers/${customerId}/photos`, {
                    method: 'POST',
                    body: formData,
                    headers: {} // Non impostare Content-Type, il browser lo fa automaticamente per FormData
                });
            }
        }
        
        showSuccess('Cliente creato con successo!');
        closeCustomerModal();
        loadCustomers();
    } catch (error) {
        showError('Errore nella creazione cliente: ' + error.message);
    }
}

function editCustomer(customerId) {
    const customer = currentCustomers.find(c => c.id === customerId);
    if (!customer) {
        showError('Cliente non trovato');
        return;
    }
    
    const formHTML = `
        <div class="modal" id="edit-customer-modal">
            <div class="modal-content">
                <span class="close" onclick="closeEditCustomerModal()">&times;</span>
                <h2>Modifica Cliente</h2>
                <form id="edit-customer-form">
                    <input type="hidden" id="edit-customer-id" value="${customer.id}">
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" id="edit-customer-email" value="${customer.email}" disabled>
                        <small>L'email non può essere modificata</small>
                    </div>
                    <div class="form-group">
                        <label>Nome Completo</label>
                        <input type="text" id="edit-customer-name" value="${customer.full_name || ''}">
                    </div>
                    <div class="form-group">
                        <label>Telefono</label>
                        <input type="tel" id="edit-customer-phone" value="${customer.phone || ''}">
                    </div>
                    <div class="form-group">
                        <label>Indirizzo</label>
                        <input type="text" id="edit-customer-address" value="${customer.address || ''}">
                    </div>
                    <div class="form-group">
                        <label>Note</label>
                        <textarea id="edit-customer-notes" rows="3">${customer.notes || ''}</textarea>
                    </div>
                    <button type="submit" class="btn btn-primary">Salva Modifiche</button>
                </form>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', formHTML);
    
    document.getElementById('edit-customer-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await updateCustomer(customer.id);
    });
}

async function updateCustomer(customerId) {
    try {
        const updateData = {
            full_name: document.getElementById('edit-customer-name').value || null,
            phone: document.getElementById('edit-customer-phone').value || null,
            address: document.getElementById('edit-customer-address').value || null,
            notes: document.getElementById('edit-customer-notes').value || null
        };
        
        await window.apiCall(`/api/customers/${customerId}`, {
            method: 'PUT',
            body: JSON.stringify(updateData)
        });
        
        showSuccess('Cliente aggiornato con successo!');
        closeEditCustomerModal();
        loadCustomers();
    } catch (error) {
        showError('Errore nell\'aggiornamento cliente: ' + error.message);
    }
}

function uploadCustomerPhoto(customerId) {
    const customer = currentCustomers.find(c => c.id === customerId);
    if (!customer) {
        showError('Cliente non trovato');
        return;
    }
    
    loadShops().then(shops => {
        const formHTML = `
            <div class="modal" id="upload-customer-photo-modal">
                <div class="modal-content">
                    <span class="close" onclick="closeUploadCustomerPhotoModal()">&times;</span>
                    <h2>Carica Foto per ${customer.full_name || customer.email}</h2>
                    <form id="upload-customer-photo-form" enctype="multipart/form-data">
                        <div class="form-group">
                            <label>Seleziona Foto *</label>
                            <input type="file" id="customer-photo-file" accept="image/*" required>
                            <small>Formati supportati: JPG, PNG, WEBP (max 10MB)</small>
                        </div>
                        <div class="form-group">
                            <label>Negozio *</label>
                            <select id="customer-photo-shop" required>
                                ${shops.map(s => `<option value="${s.id}">${s.name}</option>`).join('')}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Angolo</label>
                            <select id="customer-photo-angle">
                                <option value="">Seleziona...</option>
                                <option value="front">Frontale</option>
                                <option value="side">Laterale</option>
                                <option value="back">Posteriore</option>
                                <option value="three-quarter">Tre quarti</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>
                                <input type="checkbox" id="customer-photo-consent" checked>
                                Cliente ha dato il consenso
                            </label>
                        </div>
                        <button type="submit" class="btn btn-primary" id="upload-customer-photo-btn">
                            <span id="upload-customer-photo-btn-text">Carica Foto</span>
                            <span id="upload-customer-photo-btn-loading" style="display:none;">Caricamento...</span>
                        </button>
                    </form>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', formHTML);
        
        document.getElementById('upload-customer-photo-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await uploadPhotoForCustomer(customerId);
        });
    });
}

async function uploadPhotoForCustomer(customerId) {
    const fileInput = document.getElementById('customer-photo-file');
    const file = fileInput.files[0];
    
    if (!file) {
        showError('Seleziona un file');
        return;
    }
    
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
        showError('Il file è troppo grande. Massimo 10MB.');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    const shopId = document.getElementById('customer-photo-shop').value;
    formData.append('shop_id', shopId);
    
    const angle = document.getElementById('customer-photo-angle').value;
    if (angle) formData.append('angle', angle);
    
    const consentGiven = document.getElementById('customer-photo-consent').checked;
    formData.append('consent_given', consentGiven);
    
    const uploadBtn = document.getElementById('upload-customer-photo-btn');
    const uploadBtnText = document.getElementById('upload-customer-photo-btn-text');
    const uploadBtnLoading = document.getElementById('upload-customer-photo-btn-loading');
    
    try {
        uploadBtn.disabled = true;
        uploadBtnText.style.display = 'none';
        uploadBtnLoading.style.display = 'inline';
        
        // Recupera token da localStorage o da window.state
        const token = localStorage.getItem('crm_shops_auth_token') || 
                     localStorage.getItem('crm_token') ||
                     (window.state && window.state.token) ||
                     null;
        
        if (!token) {
            throw new Error('Token di autenticazione non trovato. Effettua il login.');
        }
        
        const apiBaseUrl = window.API_BASE_URL || window.CONFIG?.API_BASE_URL || 'http://localhost:8000';
        
        // Per FormData, NON impostare Content-Type - il browser lo fa automaticamente con boundary
        const headers = {
            'Authorization': `Bearer ${token}`
        };
        
        const response = await fetch(`${apiBaseUrl}/api/customers/${customerId}/photos`, {
            method: 'POST',
            headers: headers,
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Errore durante l\'upload');
        }
        
        showSuccess('Foto caricata con successo!');
        closeUploadCustomerPhotoModal();
        
    } catch (error) {
        showError('Errore durante l\'upload: ' + error.message);
    } finally {
        uploadBtn.disabled = false;
        uploadBtnText.style.display = 'inline';
        uploadBtnLoading.style.display = 'none';
    }
}

async function viewCustomerPhotos(customerId) {
    try {
        const data = await window.apiCall(`/api/customers/${customerId}/photos`);
        const photos = data.photos || [];
        
        const modalHTML = `
            <div class="modal" id="view-customer-photos-modal">
                <div class="modal-content large-modal">
                    <span class="close" onclick="closeViewPhotosModal()">&times;</span>
                    <h2>Foto Cliente</h2>
                    <div id="customer-photos-grid" class="photos-grid">
                        ${photos.length === 0 
                            ? '<p class="empty-state">Nessuna foto caricata per questo cliente.</p>'
                            : photos.map(photo => `
                                <div class="photo-card">
                                    <img src="${photo.image_url}" alt="Foto cliente" class="photo-image"
                                         onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'200\\' height=\\'200\\'%3E%3Crect fill=\\'%23ddd\\' width=\\'200\\' height=\\'200\\'/%3E%3Ctext fill=\\'%23999\\' font-family=\\'sans-serif\\' font-size=\\'14\\' x=\\'50%25\\' y=\\'50%25\\' text-anchor=\\'middle\\' dy=\\'.3em\\'%3EImmagine%3C/text%3E%3C/svg%3E'">
                                    <div class="photo-info">
                                        <p class="photo-angle">Angolo: ${photo.angle || 'Non specificato'}</p>
                                        <p class="photo-date">Caricata: ${new Date(photo.uploaded_at).toLocaleDateString('it-IT')}</p>
                                    </div>
                                </div>
                            `).join('')
                        }
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    } catch (error) {
        showError('Errore nel caricamento foto: ' + error.message);
    }
}

function closeViewPhotosModal() {
    const modal = document.getElementById('view-customer-photos-modal');
    if (modal) modal.remove();
}

function closeCustomerModal() {
    const modal = document.getElementById('customer-modal');
    if (modal) modal.remove();
}

function closeEditCustomerModal() {
    const modal = document.getElementById('edit-customer-modal');
    if (modal) modal.remove();
}

function closeUploadCustomerPhotoModal() {
    const modal = document.getElementById('upload-customer-photo-modal');
    if (modal) modal.remove();
}

// Esporta funzioni per uso globale
window.showCreateCustomerForm = showCreateCustomerForm;
window.editCustomer = editCustomer;
window.uploadCustomerPhoto = uploadCustomerPhoto;
window.viewCustomerPhotos = viewCustomerPhotos;
window.closeCustomerModal = closeCustomerModal;
window.closeEditCustomerModal = closeEditCustomerModal;
window.closeUploadCustomerPhotoModal = closeUploadCustomerPhotoModal;
window.closeViewPhotosModal = closeViewPhotosModal;
window.loadCustomers = loadCustomers;

})(); // Fine IIFE

