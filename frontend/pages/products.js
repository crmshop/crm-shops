// Pagina gestione prodotti per negozianti
// Usa namespace per evitare conflitti se script caricato più volte
(function() {
    'use strict';
    
    // Verifica se già inizializzato
    if (window.productsPageInitialized) {
        return;
    }
    window.productsPageInitialized = true;
    
let currentProducts = [];

async function loadProducts() {
    const container = document.getElementById('products-list');
    if (!container) {
        console.warn('Container products-list non trovato');
        return;
    }
    
    try {
        console.log('📥 Caricamento prodotti...');
        const data = await window.apiCall('/api/products/');
        console.log('✅ Prodotti caricati:', data);
        currentProducts = data.products || [];
        renderProducts();
    } catch (error) {
        console.error('❌ Errore caricamento prodotti:', error);
        container.innerHTML = `<p class="error">Errore nel caricamento prodotti: ${error.message}</p>`;
        if (window.showError) {
            window.showError('Errore nel caricamento prodotti: ' + error.message);
        }
    }
}

function renderProducts() {
    const container = document.getElementById('products-list');
    if (!container) {
        console.warn('Container products-list non trovato per rendering');
        return;
    }
    
    console.log('🎨 Rendering prodotti:', currentProducts.length);
    
    if (currentProducts.length === 0) {
        container.innerHTML = '<p class="empty-state">Nessun prodotto. Crea il primo prodotto!</p>';
        return;
    }
    
    container.innerHTML = currentProducts.map(product => `
        <div class="product-card">
            ${product.image_url ? `<img src="${product.image_url}" alt="${product.name}" class="product-image">` : ''}
            <h3>${product.name}</h3>
            <p class="product-category">${product.category}</p>
            ${product.description ? `<p class="product-description">${product.description}</p>` : ''}
            ${product.price ? `<p class="product-price">€${product.price}</p>` : ''}
            <div class="product-badges">
                ${product.available ? '<span class="badge badge-success">Disponibile</span>' : '<span class="badge badge-danger">Non disponibile</span>'}
                ${product.season ? `<span class="badge badge-info">${product.season}</span>` : ''}
            </div>
            <div class="product-actions">
                <button onclick="editProduct('${product.id}')" class="btn btn-small">Modifica</button>
                <button onclick="deleteProduct('${product.id}')" class="btn btn-small btn-danger">Elimina</button>
            </div>
        </div>
    `).join('');
}

function showCreateProductForm() {
    const formHTML = `
        <div class="modal" id="product-modal">
            <div class="modal-content">
                <span class="close" onclick="closeModal()">&times;</span>
                <h2>Nuovo Prodotto</h2>
                <form id="product-form">
                    <div class="form-group">
                        <label>Negozio</label>
                        <select id="product-shop" required></select>
                    </div>
                    <div class="form-group">
                        <label>Nome *</label>
                        <input type="text" id="product-name" required>
                    </div>
                    <div class="form-group">
                        <label>Descrizione</label>
                        <textarea id="product-description" rows="3"></textarea>
                    </div>
                    <div class="form-group">
                        <label>Categoria *</label>
                        <select id="product-category" required>
                            <option value="vestiti">Vestiti</option>
                            <option value="scarpe">Scarpe</option>
                            <option value="accessori">Accessori</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Stagione</label>
                        <select id="product-season">
                            <option value="">Seleziona...</option>
                            <option value="primavera">Primavera</option>
                            <option value="estate">Estate</option>
                            <option value="autunno">Autunno</option>
                            <option value="inverno">Inverno</option>
                            <option value="tutto">Tutto l'anno</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Occasione</label>
                        <select id="product-occasion">
                            <option value="">Seleziona...</option>
                            <option value="casual">Casual</option>
                            <option value="formale">Formale</option>
                            <option value="sport">Sport</option>
                            <option value="festa">Festa</option>
                            <option value="lavoro">Lavoro</option>
                            <option value="altro">Altro</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Prezzo (€)</label>
                        <input type="number" id="product-price" step="0.01" min="0">
                    </div>
                    <div class="form-group">
                        <label>Immagini Prodotto (max 3 tra upload e URL)</label>
                        <div id="product-images-container">
                            <div class="image-input-group">
                                <input type="file" class="product-image-file" accept="image/*">
                                <input type="url" class="product-image-url" placeholder="Oppure inserisci URL">
                                <button type="button" class="btn btn-small btn-danger remove-image" style="display:none;">Rimuovi</button>
                            </div>
                        </div>
                        <button type="button" class="btn btn-small" id="add-image-input" style="margin-top: 10px;">+ Aggiungi Immagine</button>
                        <small>Puoi aggiungere massimo 3 immagini (file o URL)</small>
                        <div id="product-images-preview" class="photos-preview"></div>
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="product-available" checked>
                            Disponibile
                        </label>
                    </div>
                    <button type="submit" class="btn btn-primary">Crea Prodotto</button>
                </form>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', formHTML);
    
    // Carica negozi dell'utente
    loadUserShops().then(shops => {
        const shopSelect = document.getElementById('product-shop');
        shopSelect.innerHTML = shops.map(s => 
            `<option value="${s.id}">${s.name}</option>`
        ).join('');
    });
    
    document.getElementById('product-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        try {
            // Raccogli immagini (file e URL)
            const imageGroups = document.querySelectorAll('.image-input-group');
            const images = [];
            
            imageGroups.forEach((group) => {
                const fileInput = group.querySelector('.product-image-file');
                const urlInput = group.querySelector('.product-image-url');
                
                if (fileInput.files.length > 0) {
                    images.push({ type: 'file', file: fileInput.files[0] });
                } else if (urlInput.value.trim()) {
                    images.push({ type: 'url', url: urlInput.value.trim() });
                }
            });
            
            if (images.length > 3) {
                if (window.showError) {
                    window.showError('Puoi aggiungere massimo 3 immagini');
                } else {
                    alert('Puoi aggiungere massimo 3 immagini');
                }
                return;
            }
            
            const productData = {
                shop_id: document.getElementById('product-shop').value,
                name: document.getElementById('product-name').value,
                description: document.getElementById('product-description').value || null,
                category: document.getElementById('product-category').value,
                season: document.getElementById('product-season').value || null,
                occasion: document.getElementById('product-occasion').value || null,
                price: parseFloat(document.getElementById('product-price').value) || null,
                available: document.getElementById('product-available').checked,
                images: images.filter(img => img.type === 'url').map(img => img.url) // Solo URL per ora
            };
            
            // Crea prodotto
            const productResponse = await window.apiCall('/api/products/', {
                method: 'POST',
                body: JSON.stringify(productData)
            });
            
            // Carica file se presenti
            const fileImages = images.filter(img => img.type === 'file');
            if (fileImages.length > 0) {
                const productId = productResponse.product?.id || productResponse.id;
                for (const img of fileImages) {
                    const formData = new FormData();
                    formData.append('file', img.file);
                    
                    await window.apiCall(`/api/products/${productId}/images`, {
                        method: 'POST',
                        body: formData,
                        headers: {}
                    });
                }
            }
            
            if (window.showSuccess) {
                window.showSuccess('Prodotto creato con successo!');
            } else {
                alert('Prodotto creato con successo!');
            }
            closeModal();
            loadProducts();
        } catch (error) {
            if (window.showError) {
                window.showError('Errore nella creazione prodotto: ' + error.message);
            } else {
                alert('Errore nella creazione prodotto: ' + error.message);
            }
        }
    });
}

async function loadUserShops() {
    try {
        const data = await apiCall('/api/shops/');
        return data.shops || [];
    } catch (error) {
        showError('Errore nel caricamento negozi: ' + error.message);
        return [];
    }
}

function closeModal() {
    const modal = document.getElementById('product-modal');
    if (modal) modal.remove();
}

function editProduct(productId) {
    // TODO: Implementare modifica prodotto
    alert('Modifica prodotto - da implementare');
}

async function deleteProduct(productId) {
    if (!confirm('Sei sicuro di voler eliminare questo prodotto?')) return;
    
    try {
        await apiCall(`/api/products/${productId}`, { method: 'DELETE' });
        showSuccess('Prodotto eliminato con successo!');
        loadProducts();
    } catch (error) {
        showError('Errore nell\'eliminazione prodotto: ' + error.message);
    }
}

// Esporta funzioni per uso globale
window.showCreateProductForm = showCreateProductForm;
window.editProduct = editProduct;
window.deleteProduct = deleteProduct;
window.closeModal = closeModal;
window.loadProducts = loadProducts;

})(); // Fine IIFE




