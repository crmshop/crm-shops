#!/bin/bash

# Script per avviare un server HTTP locale per il frontend

echo "🚀 Avvio server frontend..."

# Verifica se Python è disponibile
if command -v python3 &> /dev/null; then
    echo "Usando Python HTTP server..."
    cd frontend
    python3 -m http.server 5500
elif command -v python &> /dev/null; then
    echo "Usando Python HTTP server..."
    cd frontend
    python -m http.server 5500
elif command -v php &> /dev/null; then
    echo "Usando PHP server..."
    cd frontend
    php -S localhost:5500
else
    echo "❌ Nessun server HTTP trovato. Installa Python o PHP."
    echo "Oppure usa un server HTTP locale come Live Server in VS Code"
    exit 1
fi



