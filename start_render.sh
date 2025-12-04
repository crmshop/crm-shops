#!/bin/bash
# Script di avvio per Render
# Questo script assicura che Python possa trovare il modulo backend

# Imposta PYTHONPATH alla directory corrente (root del progetto)
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Debug: mostra variabili d'ambiente (senza valori sensibili)
echo "🔍 Debug avvio backend..."
echo "   PYTHONPATH: $PYTHONPATH"
echo "   PORT: ${PORT:-8000}"
echo "   ENVIRONMENT: ${ENVIRONMENT:-not set}"
echo "   ALLOWED_ORIGINS: ${ALLOWED_ORIGINS:-not set}"

# Avvia uvicorn
exec python -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}

