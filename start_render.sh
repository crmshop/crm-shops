#!/bin/bash
# Script di avvio per Render
# Questo script assicura che Python possa trovare il modulo backend

set -e  # Exit on error

# Imposta PYTHONPATH alla directory corrente (root del progetto)
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Debug: mostra variabili d'ambiente (senza valori sensibili)
echo "🔍 Debug avvio backend..."
echo "   PYTHONPATH: $PYTHONPATH"
echo "   PORT: ${PORT:-8000}"
echo "   ENVIRONMENT: ${ENVIRONMENT:-not set}"
echo "   ALLOWED_ORIGINS: ${ALLOWED_ORIGINS:-not set}"
echo "   PWD: $(pwd)"
echo "   Python: $(which python3 || which python || echo 'NOT FOUND')"

# Verifica che PORT sia impostato (Render lo imposta automaticamente)
if [ -z "$PORT" ]; then
    echo "⚠️  PORT non impostato, uso default 8000"
    export PORT=8000
else
    echo "✅ PORT impostato: $PORT"
fi

# Trova il comando Python corretto
PYTHON_CMD=$(which python3 || which python)
if [ -z "$PYTHON_CMD" ]; then
    echo "❌ Errore: Python non trovato!"
    echo "   Tentativo di trovare Python..."
    which python3 || which python || echo "   Nessun Python trovato nel PATH"
    exit 1
fi

echo "✅ Python trovato: $PYTHON_CMD"
echo "   Versione: $($PYTHON_CMD --version)"

# Verifica che uvicorn sia installato
echo "🔍 Verifica uvicorn..."
if ! $PYTHON_CMD -m uvicorn --help > /dev/null 2>&1; then
    echo "❌ Errore: uvicorn non trovato!"
    echo "   Installazione dipendenze..."
    pip install uvicorn fastapi || exit 1
fi

# Verifica che il modulo backend.main sia importabile
echo "🔍 Verifica importazione backend.main..."
if ! $PYTHON_CMD -c "import backend.main" 2>&1; then
    echo "❌ Errore: impossibile importare backend.main"
    echo "   Controlla che tutti i moduli siano installati correttamente"
    $PYTHON_CMD -c "import backend.main"  # Mostra l'errore completo
    exit 1
fi

# Avvia uvicorn con binding esplicito alla porta
echo "🚀 Avvio uvicorn su porta $PORT con $PYTHON_CMD..."
echo "   Comando: $PYTHON_CMD -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT"
exec $PYTHON_CMD -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT

