#!/bin/bash
# Script per configurare GitHub usando GitHub CLI

set -e

echo "🔐 Configurazione GitHub per CRM Shops"
echo ""

# Verifica se gh è installato
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) non trovato!"
    echo "Installa con: brew install gh (macOS) o sudo apt install gh (Linux)"
    exit 1
fi

echo "✅ GitHub CLI trovato"
echo ""

# Verifica autenticazione
if ! gh auth status &> /dev/null; then
    echo "🔑 Autenticazione GitHub richiesta..."
    gh auth login
else
    echo "✅ Già autenticato con GitHub"
    gh auth status
fi

echo ""
read -p "Nome repository (default: crm-shops): " repo_name
repo_name=${repo_name:-crm-shops}

read -p "Descrizione repository (default: Sistema CRM per negozi con AI generativa): " repo_desc
repo_desc=${repo_desc:-Sistema CRM per negozi con AI generativa}

echo ""
read -p "Repository pubblico? (y/n, default: y): " is_public
is_public=${is_public:-y}

if [ "$is_public" = "y" ]; then
    visibility="--public"
else
    visibility="--private"
fi

echo ""
echo "📦 Creazione repository su GitHub..."
gh repo create "$repo_name" $visibility --description "$repo_desc" --source=. --remote=origin --push

echo ""
echo "✅ Repository creato e codice pushato!"
echo ""
echo "🌐 Apertura repository nel browser..."
gh repo view --web

echo ""
echo "🎉 Setup GitHub completato!"



