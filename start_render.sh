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
echo "   PWD: $(pwd)"
echo "   Python: $(which python || which python3)"

# Verifica che PORT sia impostato
if [ -z "$PORT" ]; then
    echo "⚠️  PORT non impostato, uso default 8000"
    export PORT=8000
fi

# Trova il comando Python corretto
PYTHON_CMD=$(which python3 || which python)
if [ -z "$PYTHON_CMD" ]; then
    echo "❌ Errore: Python non trovato!"
    exit 1
fi

# Avvia uvicorn con binding esplicito alla porta
echo "🚀 Avvio uvicorn su porta $PORT con $PYTHON_CMD..."
exec $PYTHON_CMD -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT

