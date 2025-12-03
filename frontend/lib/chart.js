// Chart.js CDN fallback se non disponibile
// Versione semplificata per grafici base
if (typeof Chart === 'undefined') {
    // Carica Chart.js da CDN
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js';
    script.onload = () => {
        console.log('Chart.js caricato');
        if (window.initCharts) window.initCharts();
    };
    document.head.appendChild(script);
}

