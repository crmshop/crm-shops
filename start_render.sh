#!/bin/bash
# Script di avvio ottimizzato per Render
# Versione semplificata per deploy più veloce

set -e

# Imposta PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Verifica PORT (Render lo imposta automaticamente)
export PORT=${PORT:-8000}

# Avvia direttamente uvicorn (le dipendenze sono già installate dal build)
# Usa workers multipli per migliori performance
exec python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT --workers 2

