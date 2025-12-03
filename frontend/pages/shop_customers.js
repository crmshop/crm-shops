// Pagina gestione clienti per negozianti
let currentCustomers = [];
let currentShops = [];

async function loadCustomers() {
    try {
        const data = await apiCall('/api/customers/');
        currentCustomers = data.customers || data || [];
        renderCustomers();
    } catch (error) {
        showError('Errore nel caricamento clienti: ' + error.message);
        currentCustomers = [];
        renderCustomers();
    }
}

async function loadShops() {
    try {
        const data = await apiCall('/api/shops/');
        currentShops = data.shops || data || [];
        return currentShops;
    } catch (error) {
        console.error('Errore caricamento negozi:', error);
        return [];
    }
}

function renderCustomers() {
    const container = document.getElementById('customers-list');
    if (!container) return;
    
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
                        </div>
                        <div class="form-group">
                            <label>Password Temporanea *</label>
                            <input type="password" id="customer-password" required minlength="6">
                            <small>Il cliente potrà cambiarla al primo accesso</small>
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
                        <button type="submit" class="btn btn-primary">Crea Cliente</button>
                    </form>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', formHTML);
        
        document.getElementById('customer-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await createCustomer();
        });
    });
}

async function createCustomer() {
    try {
        const customerData = {
            shop_id: document.getElementById('customer-shop').value,
            email: document.getElementById('customer-email').value,
            password: document.getElementById('customer-password').value,
            full_name: document.getElementById('customer-name').value || null,
            phone: document.getElementById('customer-phone').value || null,
            address: document.getElementById('customer-address').value || null,
            notes: document.getElementById('customer-notes').value || null
        };
        
        await apiCall('/api/customers/', {
            method: 'POST',
            body: JSON.stringify(customerData)
        });
        
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
        
        await apiCall(`/api/customers/${customerId}`, {
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
        
        const token = localStorage.getItem(AUTH_TOKEN_KEY);
        const response = await fetch(`${API_BASE_URL}/api/customers/${customerId}/photos`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
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

function viewCustomerPhotos(customerId) {
    // TODO: Implementare visualizzazione foto cliente
    alert('Visualizzazione foto cliente - da implementare');
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
window.loadCustomers = loadCustomers;

