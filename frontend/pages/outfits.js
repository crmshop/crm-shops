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
            // Limita a max 10 prodotti (tutte le categorie sono valide per outfit)
            currentProducts = products.slice(0, 10);
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
                            <div class="form-group">
                                <label>Scenari (max 3, opzionale)</label>
                                <div id="scenarios-selection" style="margin-bottom: 1rem;">
                                    <p class="info-text">Seleziona prima un negozio per vedere gli scenari disponibili</p>
                                </div>
                                <div id="selected-scenarios"></div>
                                <small>Selezionati: <span id="selected-scenarios-count">0</span>/3</small>
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
            const scenariosContainer = document.getElementById('scenarios-selection');
            const selectedScenariosContainer = document.getElementById('selected-scenarios');
            const selectedScenariosCountSpan = document.getElementById('selected-scenarios-count');
            const generateBtn = document.getElementById('generate-image-btn');
            
            let selectedProducts = [];
            let selectedScenarios = [];
            
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
                
                // Carica scenari
                scenariosContainer.innerHTML = '<p class="info-text">Caricamento scenari...</p>';
                try {
                    const scenariosData = await window.apiCall(`/api/scenario-prompts/?shop_id=${shopId}`);
                    const scenarios = scenariosData.scenarios || [];
                    if (scenarios.length === 0) {
                        scenariosContainer.innerHTML = '<p class="info-text">Nessuno scenario disponibile. Crea scenari nella sezione "Scenario Prompts"</p>';
                    } else {
                        scenariosContainer.innerHTML = scenarios.map(s => `
                            <div class="scenario-checkbox" style="margin-bottom: 0.5rem; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px;">
                                <label style="display: flex; align-items: center; gap: 0.5rem;">
                                    <input type="checkbox" class="scenario-check" value="${s.id}" data-name="${s.name}" data-description="${s.description || ''}">
                                    <div style="flex: 1;">
                                        <strong>${s.name}</strong>
                                        ${s.description ? `<p style="margin: 0.25rem 0; font-size: 0.9rem; color: #666;">${s.description}</p>` : ''}
                                    </div>
                                </label>
                            </div>
                        `).join('');
                        
                        // Aggiungi listener per checkbox scenari
                        document.querySelectorAll('.scenario-check').forEach(checkbox => {
                            checkbox.addEventListener('change', function() {
                                const scenarioId = this.value;
                                if (this.checked) {
                                    if (selectedScenarios.length >= 3) {
                                        this.checked = false;
                                        if (window.showError) {
                                            window.showError('Puoi selezionare massimo 3 scenari');
                                        } else {
                                            alert('Puoi selezionare massimo 3 scenari');
                                        }
                                        return;
                                    }
                                    selectedScenarios.push({
                                        scenario_prompt_id: scenarioId,
                                        name: this.dataset.name,
                                        custom_text: ''
                                    });
                                } else {
                                    selectedScenarios = selectedScenarios.filter(s => s.scenario_prompt_id !== scenarioId);
                                }
                                updateSelectedScenarios();
                            });
                        });
                    }
                } catch (error) {
                    console.error('Errore caricamento scenari:', error);
                    scenariosContainer.innerHTML = '<p class="info-text">Errore nel caricamento scenari</p>';
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
            
            function updateSelectedScenarios() {
                selectedScenariosCountSpan.textContent = selectedScenarios.length;
                if (selectedScenarios.length === 0) {
                    selectedScenariosContainer.innerHTML = '<p class="info-text">Nessuno scenario selezionato</p>';
                } else {
                    selectedScenariosContainer.innerHTML = selectedScenarios.map((s, index) => `
                        <div class="selected-scenario" style="margin-bottom: 1rem; padding: 1rem; border: 1px solid #ddd; border-radius: 4px; background: #f9f9f9;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                <strong>${s.name}</strong>
                                <button type="button" class="btn-remove" onclick="removeScenario('${s.scenario_prompt_id}')">×</button>
                            </div>
                            <div class="form-group" style="margin: 0;">
                                <label style="font-size: 0.9rem;">Caratteristiche aggiuntive (testo libero):</label>
                                <textarea class="scenario-custom-text" data-scenario-id="${s.scenario_prompt_id}" rows="2" placeholder="Aggiungi dettagli specifici per questo scenario...">${s.custom_text || ''}</textarea>
                            </div>
                        </div>
                    `).join('');
                    
                    // Aggiungi listener per textarea
                    document.querySelectorAll('.scenario-custom-text').forEach(textarea => {
                        textarea.addEventListener('input', function() {
                            const scenarioId = this.dataset.scenarioId;
                            const scenario = selectedScenarios.find(s => s.scenario_prompt_id === scenarioId);
                            if (scenario) {
                                scenario.custom_text = this.value;
                            }
                        });
                    });
                }
            }
            
            // Funzione globale per rimuovere scenario
            window.removeScenario = function(scenarioId) {
                selectedScenarios = selectedScenarios.filter(s => s.scenario_prompt_id !== scenarioId);
                document.querySelector(`.scenario-check[value="${scenarioId}"]`).checked = false;
                updateSelectedScenarios();
            };
            
            // Funzione globale per rimuovere prodotto
            window.removeProduct = function(productId) {
                selectedProducts = selectedProducts.filter(p => p.id !== productId);
                document.querySelector(`.product-check[value="${productId}"]`).checked = false;
                updateSelectedProducts();
            };
            
            // Salva riferimento alle variabili per accesso globale
            window._outfitFormData = {
                selectedProducts: selectedProducts,
                selectedScenarios: selectedScenarios,
                updateSelectedProducts: updateSelectedProducts,
                updateSelectedScenarios: updateSelectedScenarios
            };
            
            document.getElementById('outfit-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                await createOutfit(selectedProducts, selectedScenarios);
            });
        });
    }

    async function createOutfit(selectedProducts, selectedScenarios = []) {
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
            
            // Se selectedScenarios non è fornito, recuperalo dal DOM
            if (!selectedScenarios || selectedScenarios.length === 0) {
                selectedScenarios = [];
                const checkedScenarios = document.querySelectorAll('.scenario-check:checked');
                checkedScenarios.forEach(checkbox => {
                    const scenarioId = checkbox.value;
                    const customTextArea = document.querySelector(`.scenario-custom-text[data-scenario-id="${scenarioId}"]`);
                    selectedScenarios.push({
                        scenario_prompt_id: scenarioId,
                        custom_text: customTextArea ? customTextArea.value.trim() || null : null
                    });
                });
            }
            
            const outfitData = {
                shop_id: document.getElementById('outfit-shop').value,
                customer_id: document.getElementById('outfit-customer').value,
                name: document.getElementById('outfit-name').value || null,
                product_ids: selectedProducts.map(p => p.id),
                scenarios: selectedScenarios.map(s => ({
                    scenario_prompt_id: s.scenario_prompt_id,
                    custom_text: s.custom_text || null
                }))
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
        const shopId = document.getElementById('outfit-shop')?.value;
        const customerId = document.getElementById('outfit-customer')?.value;
        const selectedProducts = Array.from(document.querySelectorAll('.product-check:checked')).map(cb => ({
            id: cb.value,
            name: cb.dataset.name,
            image: cb.dataset.image
        }));
        
        // Recupera scenari selezionati con testo libero dal DOM
        const selectedScenariosForGeneration = [];
        const checkedScenarios = document.querySelectorAll('.scenario-check:checked');
        checkedScenarios.forEach(checkbox => {
            const scenarioId = checkbox.value;
            const customTextArea = document.querySelector(`.scenario-custom-text[data-scenario-id="${scenarioId}"]`);
            selectedScenariosForGeneration.push({
                scenario_prompt_id: scenarioId,
                custom_text: customTextArea ? customTextArea.value.trim() || null : null
            });
        });
        
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
            
            // Chiama API per generare immagine con scenari
            const requestBody = {
                shop_id: shopId,
                customer_id: customerId,
                product_ids: selectedProducts.map(p => p.id)
            };
            
            // Aggiungi scenari solo se ce ne sono
            if (selectedScenariosForGeneration.length > 0) {
                requestBody.scenarios = selectedScenariosForGeneration;
            }
            
            const response = await window.apiCall('/api/generated-images/generate-outfit', {
                method: 'POST',
                body: JSON.stringify(requestBody)
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

    async function editOutfit(outfitId) {
        try {
            const outfitData = await window.apiCall(`/api/outfits/${outfitId}`);
            const outfit = outfitData.outfit;
            
            // Carica immagini generate per questo outfit
            let generatedImages = [];
            try {
                const imagesData = await window.apiCall(`/api/generated-images/?outfit_id=${outfitId}`);
                generatedImages = imagesData.images || [];
            } catch (error) {
                console.warn('Errore caricamento immagini generate:', error);
            }
            
            const modalHTML = `
                <div class="modal" id="edit-outfit-modal" style="max-width: 900px;">
                    <div class="modal-content">
                        <span class="close" onclick="closeEditOutfitModal()">&times;</span>
                        <h2>Modifica Outfit: ${outfit.name || 'Senza nome'}</h2>
                        
                        <div style="margin-bottom: 2rem;">
                            <h3>Informazioni Outfit</h3>
                            <p><strong>Prodotti:</strong> ${outfit.product_ids?.length || 0}</p>
                            ${outfit.scenarios && outfit.scenarios.length > 0 ? `
                                <p><strong>Scenari:</strong> ${outfit.scenarios.length}</p>
                                <ul>
                                    ${outfit.scenarios.map(s => `<li>Scenario ID: ${s.scenario_prompt_id}${s.custom_text ? ` - ${s.custom_text}` : ''}</li>`).join('')}
                                </ul>
                            ` : ''}
                        </div>
                        
                        ${generatedImages.length > 0 ? `
                            <div style="margin-bottom: 2rem;">
                                <h3>Immagini Generate (${generatedImages.length})</h3>
                                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 1rem; margin-top: 1rem;">
                                    ${generatedImages.map(img => `
                                        <div class="generated-image-card">
                                            <img src="${img.image_url}" alt="Immagine generata" class="generated-image-preview" 
                                                 onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'200\\' height=\\'200\\'%3E%3Crect fill=\\'%23ddd\\' width=\\'200\\' height=\\'200\\'/%3E%3Ctext fill=\\'%23999\\' font-family=\\'sans-serif\\' font-size=\\'14\\' x=\\'50%25\\' y=\\'50%25\\' text-anchor=\\'middle\\' dy=\\'.3em\\'%3EImmagine%3C/text%3E%3C/svg%3E'">
                                            <div class="generated-image-info">
                                                ${img.scenario ? `<p><strong>Scenario:</strong> ${img.scenario}</p>` : ''}
                                                ${img.prompt_used ? `<p style="font-size: 0.85rem; color: #666; margin-top: 0.5rem;">${img.prompt_used.substring(0, 100)}...</p>` : ''}
                                                <p style="font-size: 0.8rem; color: #999; margin-top: 0.5rem;">
                                                    ${new Date(img.generated_at).toLocaleDateString('it-IT')}
                                                </p>
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        ` : `
                            <div style="margin-bottom: 2rem;">
                                <p class="info-text">Nessuna immagine generata per questo outfit.</p>
                                <p class="info-text">Usa il pulsante "Crea Immagine" durante la creazione dell'outfit per generare immagini.</p>
                            </div>
                        `}
                        
                        <div class="form-actions">
                            <button type="button" class="btn btn-secondary" onclick="closeEditOutfitModal()">Chiudi</button>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.insertAdjacentHTML('beforeend', modalHTML);
        } catch (error) {
            if (window.showError) {
                window.showError('Errore nel caricamento outfit: ' + error.message);
            } else {
                alert('Errore nel caricamento outfit: ' + error.message);
            }
        }
    }
    
    function closeEditOutfitModal() {
        const modal = document.getElementById('edit-outfit-modal');
        if (modal) modal.remove();
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
    window.closeEditOutfitModal = closeEditOutfitModal;
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



