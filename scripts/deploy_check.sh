#!/bin/bash

# Script per verificare che tutto sia pronto per il deploy

echo "🔍 Verifica pre-deploy..."
echo ""

ERRORS=0
WARNINGS=0

# Verifica Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python trovato: $PYTHON_VERSION"
else
    echo "❌ Python3 non trovato"
    ERRORS=$((ERRORS + 1))
fi

# Verifica dipendenze
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt trovato"
    MISSING_DEPS=$(pip3 list | grep -v "Package" | wc -l)
    if [ "$MISSING_DEPS" -lt 5 ]; then
        echo "⚠️  Potrebbero mancare alcune dipendenze. Esegui: pip install -r requirements.txt"
        WARNINGS=$((WARNINGS + 1))
    else
        echo "✅ Dipendenze installate"
    fi
else
    echo "❌ requirements.txt non trovato"
    ERRORS=$((ERRORS + 1))
fi

# Verifica file .env
if [ -f ".env" ]; then
    echo "✅ File .env trovato"
    
    # Verifica variabili essenziali
    if grep -q "SUPABASE_URL" .env && grep -q "SUPABASE_KEY" .env; then
        echo "✅ Variabili Supabase configurate"
    else
        echo "⚠️  Variabili Supabase potrebbero mancare in .env"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo "⚠️  File .env non trovato (potrebbe essere normale in produzione con variabili d'ambiente)"
    WARNINGS=$((WARNINGS + 1))
fi

# Verifica struttura backend
if [ -d "backend" ] && [ -f "backend/main.py" ]; then
    echo "✅ Struttura backend presente"
else
    echo "❌ Struttura backend mancante o incompleta"
    ERRORS=$((ERRORS + 1))
fi

# Verifica struttura frontend
if [ -d "frontend" ] && [ -f "frontend/index.html" ]; then
    echo "✅ Struttura frontend presente"
else
    echo "❌ Struttura frontend mancante o incompleta"
    ERRORS=$((ERRORS + 1))
fi

# Verifica script di avvio
if [ -f "start_backend.sh" ]; then
    echo "✅ Script start_backend.sh presente"
else
    echo "⚠️  Script start_backend.sh non trovato"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""
echo "="*50
if [ $ERRORS -eq 0 ]; then
    echo "✅ Verifica completata: Nessun errore critico"
    if [ $WARNINGS -gt 0 ]; then
        echo "⚠️  Trovati $WARNINGS warning(s)"
    fi
    exit 0
else
    echo "❌ Verifica completata: Trovati $ERRORS errore(i)"
    exit 1
fi

