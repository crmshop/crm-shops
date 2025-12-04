#!/bin/bash

# Script per preparare il frontend per il deploy
# Questo script può essere eseguito durante il build su Render

echo "🔨 Building frontend for production..."

FRONTEND_DIR="frontend"
BUILD_DIR="frontend_build"

# Crea directory build
mkdir -p "$BUILD_DIR"

# Copia file statici
cp -r "$FRONTEND_DIR"/* "$BUILD_DIR/"

# Se esiste una variabile d'ambiente API_BASE_URL, aggiorna config.js
if [ -n "$API_BASE_URL" ]; then
    echo "📝 Aggiornando API_BASE_URL a: $API_BASE_URL"
    sed -i.bak "s|API_BASE_URL.*=.*|API_BASE_URL: '$API_BASE_URL',|g" "$BUILD_DIR/config.js"
    rm "$BUILD_DIR/config.js.bak" 2>/dev/null || true
fi

echo "✅ Frontend build completato in $BUILD_DIR"
echo "📦 File pronti per il deploy:"
ls -lh "$BUILD_DIR"


