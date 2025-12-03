// Pagina statistiche negozio per negozianti
let currentStats = null;
let currentShopId = null;

async function loadShopStats(shopId, period = '30days') {
    try {
        currentShopId = shopId;
        const data = await apiCall(`/api/shop-stats/${shopId}?period=${period}`);
        currentStats = data;
        renderStats();
    } catch (error) {
        showError('Errore nel caricamento statistiche: ' + error.message);
    }
}

function renderStats() {
    const container = document.getElementById('stats-content');
    if (!container || !currentStats) return;
    
    container.innerHTML = `
        <div class="stats-header">
            <h3>Statistiche Negozio</h3>
            <select id="stats-period" onchange="loadShopStats('${currentShopId}', this.value)">
                <option value="7days" ${currentStats.period === '7days' ? 'selected' : ''}>Ultimi 7 giorni</option>
                <option value="30days" ${currentStats.period === '30days' ? 'selected' : ''}>Ultimi 30 giorni</option>
                <option value="90days" ${currentStats.period === '90days' ? 'selected' : ''}>Ultimi 90 giorni</option>
                <option value="all" ${currentStats.period === 'all' ? 'selected' : ''}>Tutto</option>
            </select>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">👥</div>
                <div class="stat-value">${currentStats.total_customers}</div>
                <div class="stat-label">Clienti Totali</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🛍️</div>
                <div class="stat-value">${currentStats.total_products}</div>
                <div class="stat-label">Prodotti</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📸</div>
                <div class="stat-value">${currentStats.total_photos}</div>
                <div class="stat-label">Foto Caricate</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🎨</div>
                <div class="stat-value">${currentStats.total_generated_images}</div>
                <div class="stat-label">Immagini Generate</div>
            </div>
        </div>
        
        <div class="stats-charts">
            <div class="chart-container">
                <canvas id="stats-overview-chart"></canvas>
            </div>
        </div>
        
        <div class="stats-sections">
            <div class="stats-section">
                <h4>Clienti Recenti</h4>
                <div class="recent-customers-list">
                    ${currentStats.recent_customers.length === 0 
                        ? '<p class="empty-state">Nessun cliente recente</p>'
                        : currentStats.recent_customers.map(customer => `
                            <div class="recent-item">
                                <div class="recent-item-info">
                                    <strong>${customer.full_name || customer.email}</strong>
                                    <span class="recent-item-date">${new Date(customer.created_at).toLocaleDateString('it-IT')}</span>
                                </div>
                            </div>
                        `).join('')
                    }
                </div>
            </div>
            
            <div class="stats-section">
                <h4>Prodotti Recenti</h4>
                <div class="recent-products-list">
                    ${currentStats.top_products.length === 0 
                        ? '<p class="empty-state">Nessun prodotto</p>'
                        : currentStats.top_products.map(product => `
                            <div class="recent-item">
                                <div class="recent-item-info">
                                    <strong>${product.name}</strong>
                                    <span class="recent-item-category">${product.category}</span>
                                </div>
                            </div>
                        `).join('')
                    }
                </div>
            </div>
        </div>
        
        <script>
            // Inizializza grafici dopo il rendering
            setTimeout(() => {
                if (typeof Chart !== 'undefined') {
                    initStatsChart();
                } else {
                    // Carica Chart.js e poi inizializza
                    const script = document.createElement('script');
                    script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js';
                    script.onload = initStatsChart;
                    document.head.appendChild(script);
                }
            }, 100);
        </script>
    `;
}

// Esporta funzioni per uso globale
window.loadShopStats = loadShopStats;

