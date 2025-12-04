// Pagina gestione immagini generate dall'AI
let currentGeneratedImages = [];
let availableProducts = [];
let availableCustomerPhotos = [];

async function loadGeneratedImages() {
    try {
        // Carica immagini generate (filtrate per utente corrente)
        // Nota: l'API richiede filtri specifici
        const data = await apiCall('/api/generated-images/');
        currentGeneratedImages = data.images || [];
        renderGeneratedImages();
    } catch (error) {
        console.warn('Errore caricamento immagini generate:', error);
        currentGeneratedImages = [];
        renderGeneratedImages();
    }
}

async function loadDataForGeneration() {
    try {
        // Carica foto cliente disponibili
        const photosData = await apiCall('/api/customer-photos/');
        availableCustomerPhotos = photosData.photos || [];
        
        // Carica prodotti disponibili (tutti i negozi)
        const productsData = await apiCall('/api/products/');
        availableProducts = productsData.products || [];
        
        updateGenerationForm();
    } catch (error) {
        console.error('Errore caricamento dati:', error);
    }
}

function renderGeneratedImages() {
    const container = document.getElementById('generated-images-list');
    if (!container) return;
    
    if (currentGeneratedImages.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>Nessuna immagine generata.</p>
                <p>Genera la tua prima immagine AI!</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = currentGeneratedImages.map(img => `
        <div class="generated-image-card">
            <img src="${img.image_url}" alt="Immagine generata" class="generated-image-preview"
                 onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'400\\' height=\\'400\\'%3E%3Crect fill=\\'%23ddd\\' width=\\'400\\' height=\\'400\\'/%3E%3Ctext fill=\\'%23999\\' font-family=\\'sans-serif\\' font-size=\\'16\\' x=\\'50%25\\' y=\\'50%25\\' text-anchor=\\'middle\\' dy=\\'.3em\\'%3EImmagine AI%3C/text%3E%3C/svg%3E'">
            <div class="generated-image-info">
                ${img.scenario ? `<p><strong>Scenario:</strong> ${img.scenario}</p>` : ''}
                ${img.prompt_used ? `<p><strong>Prompt:</strong> ${img.prompt_used.substring(0, 50)}...</p>` : ''}
                <p class="generated-date">Generata: ${new Date(img.generated_at).toLocaleDateString('it-IT')}</p>
            </div>
            <div class="generated-image-actions">
                <a href="${img.image_url}" target="_blank" class="btn btn-small">Apri</a>
                <button onclick="deleteGeneratedImage('${img.id}')" class="btn btn-small btn-danger">Elimina</button>
            </div>
        </div>
    `).join('');
}

function showGenerateImageForm() {
    const formHTML = `
        <div class="modal" id="generate-image-modal">
            <div class="modal-content large-modal">
                <span class="close" onclick="closeGenerateModal()">&times;</span>
                <h2>Genera Immagine AI</h2>
                <form id="generate-image-form">
                    <div class="form-group">
                        <label>Foto Cliente *</label>
                        <select id="generate-customer-photo" required>
                            <option value="">Seleziona una foto...</option>
                        </select>
                        <small>Seleziona una delle tue foto caricate</small>
                    </div>
                    <div class="form-group">
                        <label>Prodotto *</label>
                        <select id="generate-product" required>
                            <option value="">Seleziona un prodotto...</option>
                        </select>
                        <small>Seleziona il prodotto da visualizzare</small>
                    </div>
                    <div class="form-group">
                        <label>Scenario</label>
                        <select id="generate-scenario">
                            <option value="">Seleziona scenario...</option>
                            <option value="montagna">Montagna</option>
                            <option value="spiaggia">Spiaggia</option>
                            <option value="città">Città</option>
                            <option value="bosco">Bosco</option>
                            <option value="festa">Festa</option>
                            <option value="lavoro">Lavoro</option>
                            <option value="casual">Casual</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Prompt Personalizzato (opzionale)</label>
                        <textarea id="generate-prompt" rows="3" 
                                  placeholder="Es: 'Cliente che indossa il prodotto in un ambiente elegante con luce naturale'"></textarea>
                    </div>
                    <div class="form-group">
                        <label>Servizio AI</label>
                        <select id="generate-ai-service">
                            <option value="gemini">Google Gemini (consigliato)</option>
                            <option value="banana_pro">Banana Pro</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary" id="generate-btn">
                        <span id="generate-btn-text">Genera Immagine</span>
                        <span id="generate-btn-loading" style="display:none;">Generazione in corso...</span>
                    </button>
                </form>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', formHTML);
    
    // Carica dati necessari
    loadDataForGeneration();
    
    document.getElementById('generate-image-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await generateImage();
    });
}

function updateGenerationForm() {
    const photoSelect = document.getElementById('generate-customer-photo');
    const productSelect = document.getElementById('generate-product');
    
    if (photoSelect) {
        photoSelect.innerHTML = '<option value="">Seleziona una foto...</option>' +
            availableCustomerPhotos.map(p => 
                `<option value="${p.id}">Foto ${p.angle || 'senza angolo'} - ${new Date(p.uploaded_at).toLocaleDateString('it-IT')}</option>`
            ).join('');
    }
    
    if (productSelect) {
        productSelect.innerHTML = '<option value="">Seleziona un prodotto...</option>' +
            availableProducts.map(p => 
                `<option value="${p.id}">${p.name} - ${p.category}</option>`
            ).join('');
    }
}

async function generateImage() {
    const customerPhotoId = document.getElementById('generate-customer-photo').value;
    const productId = document.getElementById('generate-product').value;
    const scenario = document.getElementById('generate-scenario').value;
    const prompt = document.getElementById('generate-prompt').value;
    const aiService = document.getElementById('generate-ai-service').value;
    
    if (!customerPhotoId || !productId) {
        showError('Seleziona sia una foto cliente che un prodotto');
        return;
    }
    
    const generateBtn = document.getElementById('generate-btn');
    const generateBtnText = document.getElementById('generate-btn-text');
    const generateBtnLoading = document.getElementById('generate-btn-loading');
    
    try {
        generateBtn.disabled = true;
        generateBtnText.style.display = 'none';
        generateBtnLoading.style.display = 'inline';
        
        const requestData = {
            customer_photo_id: customerPhotoId,
            product_id: productId,
            scenario: scenario || null,
            prompt_used: prompt || null,
            ai_service: aiService
        };
        
        const data = await apiCall('/api/generated-images/generate', {
            method: 'POST',
            body: JSON.stringify(requestData)
        });
        
        showSuccess('Immagine generata con successo!');
        closeGenerateModal();
        loadGeneratedImages();
        
    } catch (error) {
        showError('Errore durante la generazione: ' + error.message);
    } finally {
        generateBtn.disabled = false;
        generateBtnText.style.display = 'inline';
        generateBtnLoading.style.display = 'none';
    }
}

async function deleteGeneratedImage(imageId) {
    if (!confirm('Sei sicuro di voler eliminare questa immagine generata?')) return;
    
    try {
        await apiCall(`/api/generated-images/${imageId}`, { method: 'DELETE' });
        showSuccess('Immagine eliminata con successo!');
        loadGeneratedImages();
    } catch (error) {
        showError('Errore nell\'eliminazione immagine: ' + error.message);
    }
}

function closeGenerateModal() {
    const modal = document.getElementById('generate-image-modal');
    if (modal) modal.remove();
}

// Esporta funzioni per uso globale
window.showGenerateImageForm = showGenerateImageForm;
window.deleteGeneratedImage = deleteGeneratedImage;
window.closeGenerateModal = closeGenerateModal;
window.loadGeneratedImages = loadGeneratedImages;




