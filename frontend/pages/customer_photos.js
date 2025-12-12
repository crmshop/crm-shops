// Pagina gestione foto clienti
let currentPhotos = [];

async function loadCustomerPhotos() {
    try {
        const data = await apiCall('/api/customer-photos/');
        currentPhotos = data.photos || [];
        renderPhotos();
        updatePhotoLimitInfo();
    } catch (error) {
        showError('Errore nel caricamento foto: ' + error.message);
    }
}

function updatePhotoLimitInfo() {
    // Aggiorna informazioni sul limite foto
    const photoCount = currentPhotos.length;
    const maxPhotos = 3;
    const remaining = maxPhotos - photoCount;
    
    // Cerca o crea elemento per mostrare il limite
    let limitInfo = document.getElementById('photo-limit-info');
    if (!limitInfo) {
        const photosList = document.getElementById('photos-list');
        if (photosList) {
            limitInfo = document.createElement('div');
            limitInfo.id = 'photo-limit-info';
            limitInfo.className = 'photo-limit-info';
            photosList.parentNode.insertBefore(limitInfo, photosList);
        }
    }
    
    if (limitInfo) {
        if (photoCount >= maxPhotos) {
            limitInfo.innerHTML = `
                <div class="alert alert-warning">
                    <strong>Limite raggiunto:</strong> Hai caricato ${photoCount}/${maxPhotos} foto. 
                    Elimina una foto per caricarne una nuova.
                </div>
            `;
        } else {
            limitInfo.innerHTML = `
                <div class="alert alert-info">
                    <strong>Foto caricate:</strong> ${photoCount}/${maxPhotos} 
                    (${remaining} ${remaining === 1 ? 'foto rimanente' : 'foto rimanenti'})
                </div>
            `;
        }
    }
}

function renderPhotos() {
    const container = document.getElementById('photos-list');
    if (!container) return;
    
    if (currentPhotos.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>Nessuna foto caricata.</p>
                <p>Carica la tua prima foto per iniziare!</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = currentPhotos.map(photo => `
        <div class="photo-card">
            <img src="${photo.image_url}" alt="Foto cliente" class="photo-image" 
                 onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'200\\' height=\\'200\\'%3E%3Crect fill=\\'%23ddd\\' width=\\'200\\' height=\\'200\\'/%3E%3Ctext fill=\\'%23999\\' font-family=\\'sans-serif\\' font-size=\\'14\\' x=\\'50%25\\' y=\\'50%25\\' text-anchor=\\'middle\\' dy=\\'.3em\\'%3EImmagine%3C/text%3E%3C/svg%3E'">
            <div class="photo-info">
                <p class="photo-angle">Angolo: ${photo.angle || 'Non specificato'}</p>
                <p class="photo-date">Caricata: ${new Date(photo.uploaded_at).toLocaleDateString('it-IT')}</p>
                ${photo.consent_given ? '<span class="badge badge-success">Consenso dato</span>' : '<span class="badge badge-warning">Consenso non dato</span>'}
            </div>
            <div class="photo-actions">
                <button onclick="deletePhoto('${photo.id}')" class="btn btn-small btn-danger">Elimina</button>
            </div>
        </div>
    `).join('');
}

function showUploadPhotoForm() {
    // Verifica limite prima di mostrare il form
    if (currentPhotos.length >= 3) {
        showError('Hai già caricato il massimo di 3 foto. Elimina una foto esistente per caricarne una nuova.');
        return;
    }
    
    const remaining = 3 - currentPhotos.length;
    const formHTML = `
        <div class="modal" id="upload-photo-modal">
            <div class="modal-content">
                <span class="close" onclick="closeUploadModal()">&times;</span>
                <h2>Carica Foto Cliente</h2>
                <div class="alert alert-info" style="margin-bottom: 1rem;">
                    <strong>Limite foto:</strong> ${currentPhotos.length}/3 caricate 
                    (${remaining} ${remaining === 1 ? 'foto rimanente' : 'foto rimanenti'})
                </div>
                <form id="upload-photo-form" enctype="multipart/form-data">
                    <div class="form-group">
                        <label>Seleziona Foto *</label>
                        <input type="file" id="photo-file" accept="image/*" required>
                        <small>Formati supportati: JPG, PNG, WEBP (max 10MB)</small>
                    </div>
                    <div class="form-group">
                        <label>Angolo</label>
                        <select id="photo-angle">
                            <option value="">Seleziona...</option>
                            <option value="front">Frontale</option>
                            <option value="side">Laterale</option>
                            <option value="back">Posteriore</option>
                            <option value="three-quarter">Tre quarti</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="photo-consent" checked>
                            Do il consenso per l'utilizzo delle mie foto
                        </label>
                    </div>
                    <div class="form-group">
                        <label>Negozio (opzionale)</label>
                        <select id="photo-shop">
                            <option value="">Nessun negozio</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary" id="upload-btn">
                        <span id="upload-btn-text">Carica Foto</span>
                        <span id="upload-btn-loading" style="display:none;">Caricamento...</span>
                    </button>
                </form>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', formHTML);
    
    // Carica negozi disponibili
    loadShopsForSelect().then(shops => {
        const shopSelect = document.getElementById('photo-shop');
        shopSelect.innerHTML = '<option value="">Nessun negozio</option>' + 
            shops.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
    });
    
    document.getElementById('upload-photo-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await uploadPhoto();
    });
}

async function loadShopsForSelect() {
    try {
        const data = await apiCall('/api/shops/');
        return data.shops || [];
    } catch (error) {
        console.warn('Errore caricamento negozi:', error);
        return [];
    }
}

async function uploadPhoto() {
    // Verifica limite foto prima dell'upload
    if (currentPhotos.length >= 3) {
        showError('Hai già caricato il massimo di 3 foto. Elimina una foto esistente per caricarne una nuova.');
        return;
    }
    
    const fileInput = document.getElementById('photo-file');
    const file = fileInput.files[0];
    
    if (!file) {
        showError('Seleziona un file');
        return;
    }
    
    // Validazione file
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
        showError('Il file è troppo grande. Massimo 10MB.');
        return;
    }
    
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        showError('Formato file non supportato. Usa JPG, PNG o WEBP.');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    const angle = document.getElementById('photo-angle').value;
    if (angle) formData.append('angle', angle);
    
    const consentGiven = document.getElementById('photo-consent').checked;
    formData.append('consent_given', consentGiven);
    
    const shopId = document.getElementById('photo-shop').value;
    if (shopId) formData.append('shop_id', shopId);
    
    const uploadBtn = document.getElementById('upload-btn');
    const uploadBtnText = document.getElementById('upload-btn-text');
    const uploadBtnLoading = document.getElementById('upload-btn-loading');
    
    try {
        uploadBtn.disabled = true;
        uploadBtnText.style.display = 'none';
        uploadBtnLoading.style.display = 'inline';
        
        const token = localStorage.getItem(AUTH_TOKEN_KEY);
        const apiBaseUrl = window.API_BASE_URL || window.CONFIG?.API_BASE_URL || 'http://localhost:8000';
        const response = await fetch(`${apiBaseUrl}/api/customer-photos/`, {
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
        
        const data = await response.json();
        showSuccess('Foto caricata con successo!');
        closeUploadModal();
        loadCustomerPhotos();
        
    } catch (error) {
        showError('Errore durante l\'upload: ' + error.message);
    } finally {
        uploadBtn.disabled = false;
        uploadBtnText.style.display = 'inline';
        uploadBtnLoading.style.display = 'none';
    }
}

async function deletePhoto(photoId) {
    if (!confirm('Sei sicuro di voler eliminare questa foto?')) return;
    
    try {
        await apiCall(`/api/customer-photos/${photoId}`, { method: 'DELETE' });
        showSuccess('Foto eliminata con successo!');
        await loadCustomerPhotos(); // await per assicurarsi che il caricamento sia completato
    } catch (error) {
        showError('Errore nell\'eliminazione foto: ' + error.message);
    }
}

function closeUploadModal() {
    const modal = document.getElementById('upload-photo-modal');
    if (modal) modal.remove();
}

// Esporta funzioni per uso globale
window.showUploadPhotoForm = showUploadPhotoForm;
window.deletePhoto = deletePhoto;
window.closeUploadModal = closeUploadModal;
window.loadCustomerPhotos = loadCustomerPhotos;


