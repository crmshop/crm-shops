#!/bin/bash
# Script di avvio per Render
# Questo script assicura che Python possa trovare il modulo backend

# Imposta PYTHONPATH alla directory corrente (root del progetto)
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Avvia uvicorn
exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}

