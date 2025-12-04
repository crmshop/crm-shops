// Pagina gestione outfit per negozianti
// Usa namespace per evitare conflitti se script caricato più volte
(function() {
    'use strict';
    
    // Verifica se già inizializzato
    if (window.outfitsPageInitialized) {
        return;
    }
    window.outfitsPageInitialized = true;
    
    let currentOutfits = [];
    let currentShops = [];
    let currentCustomers = [];
    let currentProducts = [];

    async function loadOutfits() {
        const container = document.getElementById('outfits-list');
        if (!container) {
            console.warn('Container outfits-list non trovato');
            return;
        }
        
        try {
            console.log('📥 Caricamento outfit...');
            const data = await window.apiCall('/api/outfits/');
            console.log('✅ Outfit caricati:', data);
            currentOutfits = data.outfits || data || [];
            renderOutfits();
        } catch (error) {
            console.error('❌ Errore caricamento outfit:', error);
            currentOutfits = [];
            container.innerHTML = `<p class="error">Errore nel caricamento outfit: ${error.message}</p>`;
            if (window.showError) {
                window.showError('Errore nel caricamento outfit: ' + error.message);
            }
        }
    }

    function renderOutfits() {
        const container = document.getElementById('outfits-list');
        if (!container) {
            console.warn('Container outfits-list non trovato per rendering');
            return;
        }
        
        console.log('🎨 Rendering outfit:', currentOutfits.length);
        
        if (currentOutfits.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <p>Nessun outfit creato.</p>
                    <p>Crea il tuo primo outfit!</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = currentOutfits.map(outfit => `
            <div class="outfit-card">
                <div class="outfit-header">
                    <h3>${outfit.name || 'Outfit senza nome'}</h3>
                    <span class="outfit-date">Creato: ${new Date(outfit.created_at).toLocaleDateString('it-IT')}</span>
                </div>
                <div class="outfit-info">
                    <p><strong>Prodotti:</strong> ${outfit.product_ids?.length || 0}</p>
                </div>
                <div class="outfit-actions">
                    <button onclick="editOutfit('${outfit.id}')" class="btn btn-small">Modifica</button>
                    <button onclick="deleteOutfit('${outfit.id}')" class="btn btn-small btn-danger">Elimina</button>
                </div>
            </div>
        `).join('');
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

    async function loadCustomersForShop(shopId) {
        try {
            const data = await window.apiCall(`/api/customers/?shop_id=${shopId}`);
            currentCustomers = data.customers || data || [];
            return currentCustomers;
        } catch (error) {
            console.error('Errore caricamento clienti:', error);
            return [];
        }
    }

    async function loadProductsForShop(shopId) {
        try {
            const data = await window.apiCall(`/api/products/?shop_id=${shopId}`);
            const products = data.products || data || [];
            // Filtra solo vestiti e accessori (max 10)
            currentProducts = products.filter(p => 
                p.category === 'vestiti' || p.category === 'accessori'
            );
            return currentProducts;
        } catch (error) {
            console.error('Errore caricamento prodotti:', error);
            return [];
        }
    }

    function showCreateOutfitForm() {
        loadShops().then(shops => {
            if (shops.length === 0) {
                if (window.showError) {
                    window.showError('Devi prima creare un negozio!');
                } else {
                    alert('Devi prima creare un negozio!');
                }
                return;
            }
            
            const formHTML = `
                <div class="modal" id="outfit-modal" style="max-width: 800px;">
                    <div class="modal-content">
                        <span class="close" onclick="closeOutfitModal()">&times;</span>
                        <h2>Nuovo Outfit</h2>
                        <form id="outfit-form">
                            <div class="form-group">
                                <label>Negozio *</label>
                                <select id="outfit-shop" required>
                                    <option value="">Seleziona negozio...</option>
                                    ${shops.map(s => `<option value="${s.id}">${s.name}</option>`).join('')}
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Cliente *</label>
                                <select id="outfit-customer" required disabled>
                                    <option value="">Seleziona prima un negozio...</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Nome Outfit</label>
                                <input type="text" id="outfit-name" placeholder="Es: Outfit Estate 2025">
                            </div>
                            <div class="form-group">
                                <label>Prodotti (max 10 tra vestiti e accessori) *</label>
                                <div id="products-selection" class="products-selection">
                                    <p class="info-text">Seleziona prima un negozio per vedere i prodotti disponibili</p>
                                </div>
                                <div id="selected-products" class="selected-products"></div>
                                <small>Selezionati: <span id="selected-count">0</span>/10</small>
                            </div>
                            <div class="form-actions">
                                <button type="button" class="btn btn-secondary" onclick="generateOutfitImage()" id="generate-image-btn" disabled>
                                    🎨 Crea Immagine
                                </button>
                                <button type="submit" class="btn btn-primary">Crea Outfit</button>
                            </div>
                        </form>
                    </div>
                </div>
            `;
            
            document.body.insertAdjacentHTML('beforeend', formHTML);
            
            const shopSelect = document.getElementById('outfit-shop');
            const customerSelect = document.getElementById('outfit-customer');
            const productsContainer = document.getElementById('products-selection');
            const selectedContainer = document.getElementById('selected-products');
            const selectedCountSpan = document.getElementById('selected-count');
            const generateBtn = document.getElementById('generate-image-btn');
            
            let selectedProducts = [];
            
            // Quando cambia il negozio, carica clienti e prodotti
            shopSelect.addEventListener('change', async function() {
                const shopId = this.value;
                if (!shopId) {
                    customerSelect.innerHTML = '<option value="">Seleziona prima un negozio...</option>';
                    customerSelect.disabled = true;
                    productsContainer.innerHTML = '<p class="info-text">Seleziona prima un negozio per vedere i prodotti disponibili</p>';
                    selectedProducts = [];
                    updateSelectedProducts();
                    return;
                }
                
                // Carica clienti
                customerSelect.disabled = true;
                customerSelect.innerHTML = '<option value="">Caricamento...</option>';
                const customers = await loadCustomersForShop(shopId);
                customerSelect.innerHTML = '<option value="">Seleziona cliente...</option>';
                customers.forEach(c => {
                    customerSelect.innerHTML += `<option value="${c.id}">${c.full_name || c.email}</option>`;
                });
                customerSelect.disabled = false;
                
                // Carica prodotti
                productsContainer.innerHTML = '<p class="info-text">Caricamento prodotti...</p>';
                const products = await loadProductsForShop(shopId);
                if (products.length === 0) {
                    productsContainer.innerHTML = '<p class="info-text">Nessun prodotto disponibile per questo negozio</p>';
                } else {
                    productsContainer.innerHTML = products.map(p => `
                        <div class="product-checkbox">
                            <label>
                                <input type="checkbox" class="product-check" value="${p.id}" data-name="${p.name}" data-image="${p.image_url || ''}">
                                <span>${p.name} (${p.category})</span>
                                ${p.image_url ? `<img src="${p.image_url}" alt="${p.name}" class="product-thumb">` : ''}
                            </label>
                        </div>
                    `).join('');
                    
                    // Aggiungi listener per checkbox
                    document.querySelectorAll('.product-check').forEach(checkbox => {
                        checkbox.addEventListener('change', function() {
                            const productId = this.value;
                            if (this.checked) {
                                if (selectedProducts.length >= 10) {
                                    this.checked = false;
                                    if (window.showError) {
                                        window.showError('Puoi selezionare massimo 10 prodotti');
                                    } else {
                                        alert('Puoi selezionare massimo 10 prodotti');
                                    }
                                    return;
                                }
                                selectedProducts.push({
                                    id: productId,
                                    name: this.dataset.name,
                                    image: this.dataset.image
                                });
                            } else {
                                selectedProducts = selectedProducts.filter(p => p.id !== productId);
                            }
                            updateSelectedProducts();
                        });
                    });
                }
            });
            
            function updateSelectedProducts() {
                selectedCountSpan.textContent = selectedProducts.length;
                if (selectedProducts.length === 0) {
                    selectedContainer.innerHTML = '<p class="info-text">Nessun prodotto selezionato</p>';
                    generateBtn.disabled = true;
                } else {
                    selectedContainer.innerHTML = selectedProducts.map(p => `
                        <div class="selected-product">
                            <span>${p.name}</span>
                            <button type="button" class="btn-remove" onclick="removeProduct('${p.id}')">×</button>
                        </div>
                    `).join('');
                    generateBtn.disabled = false;
                }
            }
            
            // Funzione globale per rimuovere prodotto
            window.removeProduct = function(productId) {
                selectedProducts = selectedProducts.filter(p => p.id !== productId);
                document.querySelector(`.product-check[value="${productId}"]`).checked = false;
                updateSelectedProducts();
            };
            
            document.getElementById('outfit-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                await createOutfit(selectedProducts);
            });
        });
    }

    async function createOutfit(selectedProducts) {
        try {
            if (selectedProducts.length === 0) {
                if (window.showError) {
                    window.showError('Seleziona almeno un prodotto');
                } else {
                    alert('Seleziona almeno un prodotto');
                }
                return;
            }
            
            if (selectedProducts.length > 10) {
                if (window.showError) {
                    window.showError('Puoi selezionare massimo 10 prodotti');
                } else {
                    alert('Puoi selezionare massimo 10 prodotti');
                }
                return;
            }
            
            const outfitData = {
                shop_id: document.getElementById('outfit-shop').value,
                customer_id: document.getElementById('outfit-customer').value,
                name: document.getElementById('outfit-name').value || null,
                product_ids: selectedProducts.map(p => p.id)
            };
            
            await window.apiCall('/api/outfits/', {
                method: 'POST',
                body: JSON.stringify(outfitData)
            });
            
            if (window.showSuccess) {
                window.showSuccess('Outfit creato con successo!');
            } else {
                alert('Outfit creato con successo!');
            }
            closeOutfitModal();
            loadOutfits();
        } catch (error) {
            if (window.showError) {
                window.showError('Errore nella creazione outfit: ' + error.message);
            } else {
                alert('Errore nella creazione outfit: ' + error.message);
            }
        }
    }

    async function generateOutfitImage() {
        const shopId = document.getElementById('outfit-shop').value;
        const customerId = document.getElementById('outfit-customer').value;
        const selectedProducts = Array.from(document.querySelectorAll('.product-check:checked')).map(cb => ({
            id: cb.value,
            name: cb.dataset.name,
            image: cb.dataset.image
        }));
        
        if (!shopId || !customerId) {
            if (window.showError) {
                window.showError('Seleziona negozio e cliente');
            } else {
                alert('Seleziona negozio e cliente');
            }
            return;
        }
        
        if (selectedProducts.length === 0) {
            if (window.showError) {
                window.showError('Seleziona almeno un prodotto');
            } else {
                alert('Seleziona almeno un prodotto');
            }
            return;
        }
        
        try {
            if (window.showSuccess) {
                window.showSuccess('Generazione immagine in corso...');
            }
            
            // Chiama API per generare immagine
            const response = await window.apiCall('/api/generated-images/generate-outfit', {
                method: 'POST',
                body: JSON.stringify({
                    shop_id: shopId,
                    customer_id: customerId,
                    product_ids: selectedProducts.map(p => p.id)
                })
            });
            
            if (window.showSuccess) {
                window.showSuccess('Immagine generata con successo!');
            } else {
                alert('Immagine generata con successo!');
            }
            
            // Mostra l'immagine generata
            if (response.image_url) {
                const preview = document.createElement('div');
                preview.className = 'generated-image-preview';
                preview.innerHTML = `
                    <h3>Immagine Generata</h3>
                    <img src="${response.image_url}" alt="Outfit generato" style="max-width: 100%; border-radius: 8px;">
                `;
                document.getElementById('outfit-form').appendChild(preview);
            }
        } catch (error) {
            if (window.showError) {
                window.showError('Errore nella generazione immagine: ' + error.message);
            } else {
                alert('Errore nella generazione immagine: ' + error.message);
            }
        }
    }

    function editOutfit(outfitId) {
        // TODO: Implementare modifica outfit
        if (window.showError) {
            window.showError('Modifica outfit - da implementare');
        } else {
            alert('Modifica outfit - da implementare');
        }
    }

    async function deleteOutfit(outfitId) {
        if (!confirm('Sei sicuro di voler eliminare questo outfit?')) return;
        
        try {
            await window.apiCall(`/api/outfits/${outfitId}`, { method: 'DELETE' });
            if (window.showSuccess) {
                window.showSuccess('Outfit eliminato con successo!');
            } else {
                alert('Outfit eliminato con successo!');
            }
            loadOutfits();
        } catch (error) {
            if (window.showError) {
                window.showError('Errore nell\'eliminazione outfit: ' + error.message);
            } else {
                alert('Errore nell\'eliminazione outfit: ' + error.message);
            }
        }
    }

    function closeOutfitModal() {
        const modal = document.getElementById('outfit-modal');
        if (modal) modal.remove();
    }

    // Esporta funzioni per uso globale
    window.showCreateOutfitForm = showCreateOutfitForm;
    window.editOutfit = editOutfit;
    window.deleteOutfit = deleteOutfit;
    window.closeOutfitModal = closeOutfitModal;
    window.loadOutfits = loadOutfits;
    window.generateOutfitImage = generateOutfitImage;

    // Carica outfit all'avvio se siamo nella pagina outfits
    if (window.location.pathname === '/outfits' || window.location.pathname.includes('outfit')) {
        setTimeout(() => {
            loadOutfits();
        }, 500);
    }
})();



