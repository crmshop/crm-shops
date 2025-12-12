// Pagina gestione scenario prompts
(function() {
    'use strict';
    
    if (window.scenarioPromptsPageInitialized) {
        return;
    }
    window.scenarioPromptsPageInitialized = true;
    
    let currentScenarios = [];
    let currentShops = [];

    async function loadScenarioPrompts() {
        const container = document.getElementById('scenarios-list');
        if (!container) {
            console.warn('Container scenarios-list non trovato');
            return;
        }
        
        try {
            const data = await window.apiCall('/api/scenario-prompts/');
            currentScenarios = data.scenarios || [];
            renderScenarios();
        } catch (error) {
            console.error('Errore caricamento scenario prompts:', error);
            if (window.showError) {
                window.showError('Errore nel caricamento scenari: ' + error.message);
            }
        }
    }

    function renderScenarios() {
        const container = document.getElementById('scenarios-list');
        if (!container) return;
        
        if (currentScenarios.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <p>Nessuno scenario creato.</p>
                    <p>Crea il tuo primo scenario per iniziare!</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = currentScenarios.map(scenario => `
            <div class="scenario-card" style="border: 1px solid #ddd; border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; background: white;">
                <h3>${scenario.name}</h3>
                <p><strong>Descrizione:</strong> ${scenario.description}</p>
                ${scenario.position ? `<p><strong>Posizione:</strong> ${scenario.position}</p>` : ''}
                ${scenario.environment ? `<p><strong>Ambiente:</strong> ${scenario.environment}</p>` : ''}
                ${scenario.lighting ? `<p><strong>Illuminazione:</strong> ${scenario.lighting}</p>` : ''}
                ${scenario.background ? `<p><strong>Sfondo:</strong> ${scenario.background}</p>` : ''}
                <div style="margin-top: 1rem;">
                    <button onclick="editScenarioPrompt('${scenario.id}')" class="btn btn-small">Modifica</button>
                    <button onclick="deleteScenarioPrompt('${scenario.id}')" class="btn btn-small btn-danger">Elimina</button>
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

    function showCreateScenarioForm() {
        loadShops().then(shops => {
            if (shops.length === 0) {
                if (window.showError) {
                    window.showError('Devi prima creare un negozio!');
                }
                return;
            }
            
            const formHTML = `
                <div class="modal" id="scenario-modal">
                    <div class="modal-content" style="max-width: 700px;">
                        <span class="close" onclick="closeScenarioModal()">&times;</span>
                        <h2>Nuovo Scenario Prompt</h2>
                        <form id="scenario-form">
                            <div class="form-group">
                                <label>Negozio *</label>
                                <select id="scenario-shop" required>
                                    <option value="">Seleziona negozio...</option>
                                    ${shops.map(s => `<option value="${s.id}">${s.name}</option>`).join('')}
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Nome Scenario *</label>
                                <input type="text" id="scenario-name" required placeholder="Es: Spiaggia Estate">
                            </div>
                            <div class="form-group">
                                <label>Descrizione *</label>
                                <textarea id="scenario-description" rows="3" required placeholder="Descrizione dettagliata della posizione, ambiente, illuminazione, ecc."></textarea>
                            </div>
                            <div class="form-group">
                                <label>Posizione</label>
                                <input type="text" id="scenario-position" placeholder="Es: in piedi, seduto, camminando">
                            </div>
                            <div class="form-group">
                                <label>Ambiente</label>
                                <input type="text" id="scenario-environment" placeholder="Es: interno, esterno, spiaggia, città">
                            </div>
                            <div class="form-group">
                                <label>Illuminazione</label>
                                <input type="text" id="scenario-lighting" placeholder="Es: naturale, artificiale, serale">
                            </div>
                            <div class="form-group">
                                <label>Sfondo</label>
                                <textarea id="scenario-background" rows="2" placeholder="Descrizione dello sfondo"></textarea>
                            </div>
                            <button type="submit" class="btn btn-primary">Crea Scenario</button>
                        </form>
                    </div>
                </div>
            `;
            
            document.body.insertAdjacentHTML('beforeend', formHTML);
            
            document.getElementById('scenario-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                await createScenarioPrompt();
            });
        });
    }

    async function createScenarioPrompt() {
        const scenarioData = {
            shop_id: document.getElementById('scenario-shop').value,
            name: document.getElementById('scenario-name').value,
            description: document.getElementById('scenario-description').value,
            position: document.getElementById('scenario-position').value || null,
            environment: document.getElementById('scenario-environment').value || null,
            lighting: document.getElementById('scenario-lighting').value || null,
            background: document.getElementById('scenario-background').value || null
        };
        
        try {
            await window.apiCall('/api/scenario-prompts/', {
                method: 'POST',
                body: JSON.stringify(scenarioData)
            });
            
            if (window.showSuccess) {
                window.showSuccess('Scenario creato con successo!');
            }
            closeScenarioModal();
            loadScenarioPrompts();
        } catch (error) {
            if (window.showError) {
                window.showError('Errore nella creazione scenario: ' + error.message);
            }
        }
    }

    function editScenarioPrompt(scenarioId) {
        const scenario = currentScenarios.find(s => s.id === scenarioId);
        if (!scenario) {
            if (window.showError) {
                window.showError('Scenario non trovato');
            }
            return;
        }
        
        loadShops().then(shops => {
            const formHTML = `
                <div class="modal" id="scenario-modal">
                    <div class="modal-content" style="max-width: 700px;">
                        <span class="close" onclick="closeScenarioModal()">&times;</span>
                        <h2>Modifica Scenario Prompt</h2>
                        <form id="scenario-form">
                            <div class="form-group">
                                <label>Negozio *</label>
                                <select id="scenario-shop" required disabled>
                                    ${shops.map(s => `<option value="${s.id}" ${s.id === scenario.shop_id ? 'selected' : ''}>${s.name}</option>`).join('')}
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Nome Scenario *</label>
                                <input type="text" id="scenario-name" required value="${scenario.name}">
                            </div>
                            <div class="form-group">
                                <label>Descrizione *</label>
                                <textarea id="scenario-description" rows="3" required>${scenario.description || ''}</textarea>
                            </div>
                            <div class="form-group">
                                <label>Posizione</label>
                                <input type="text" id="scenario-position" value="${scenario.position || ''}">
                            </div>
                            <div class="form-group">
                                <label>Ambiente</label>
                                <input type="text" id="scenario-environment" value="${scenario.environment || ''}">
                            </div>
                            <div class="form-group">
                                <label>Illuminazione</label>
                                <input type="text" id="scenario-lighting" value="${scenario.lighting || ''}">
                            </div>
                            <div class="form-group">
                                <label>Sfondo</label>
                                <textarea id="scenario-background" rows="2">${scenario.background || ''}</textarea>
                            </div>
                            <button type="submit" class="btn btn-primary">Salva Modifiche</button>
                        </form>
                    </div>
                </div>
            `;
            
            document.body.insertAdjacentHTML('beforeend', formHTML);
            
            document.getElementById('scenario-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                await updateScenarioPrompt(scenarioId);
            });
        });
    }

    async function updateScenarioPrompt(scenarioId) {
        const scenarioData = {
            name: document.getElementById('scenario-name').value,
            description: document.getElementById('scenario-description').value,
            position: document.getElementById('scenario-position').value || null,
            environment: document.getElementById('scenario-environment').value || null,
            lighting: document.getElementById('scenario-lighting').value || null,
            background: document.getElementById('scenario-background').value || null
        };
        
        try {
            await window.apiCall(`/api/scenario-prompts/${scenarioId}`, {
                method: 'PUT',
                body: JSON.stringify(scenarioData)
            });
            
            if (window.showSuccess) {
                window.showSuccess('Scenario aggiornato con successo!');
            }
            closeScenarioModal();
            loadScenarioPrompts();
        } catch (error) {
            if (window.showError) {
                window.showError('Errore nell\'aggiornamento scenario: ' + error.message);
            }
        }
    }

    async function deleteScenarioPrompt(scenarioId) {
        if (!confirm('Sei sicuro di voler eliminare questo scenario?')) return;
        
        try {
            await window.apiCall(`/api/scenario-prompts/${scenarioId}`, { method: 'DELETE' });
            if (window.showSuccess) {
                window.showSuccess('Scenario eliminato con successo!');
            }
            loadScenarioPrompts();
        } catch (error) {
            if (window.showError) {
                window.showError('Errore nell\'eliminazione scenario: ' + error.message);
            }
        }
    }

    function closeScenarioModal() {
        const modal = document.getElementById('scenario-modal');
        if (modal) modal.remove();
    }

    // Esporta funzioni per uso globale
    window.loadScenarioPrompts = loadScenarioPrompts;
    window.showCreateScenarioForm = showCreateScenarioForm;
    window.editScenarioPrompt = editScenarioPrompt;
    window.deleteScenarioPrompt = deleteScenarioPrompt;
    window.closeScenarioModal = closeScenarioModal;

})();
