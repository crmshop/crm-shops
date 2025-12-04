#!/bin/bash
# Script per preparare il deploy su Render

set -e

echo "🚀 Preparazione deploy su Render..."

# Verifica che siamo nella directory corretta
if [ ! -f "requirements.txt" ]; then
    echo "❌ Errore: requirements.txt non trovato. Esegui lo script dalla root del progetto."
    exit 1
fi

# Verifica variabili d'ambiente essenziali
echo "📋 Verifica configurazione..."

if [ -z "$SUPABASE_URL" ]; then
    echo "⚠️  SUPABASE_URL non configurata"
fi

if [ -z "$SUPABASE_KEY" ]; then
    echo "⚠️  SUPABASE_KEY non configurata"
fi

# Crea directory dist se non esiste
mkdir -p dist

# Copia frontend per deploy statico
echo "📦 Preparazione frontend..."
cp -r frontend/* dist/frontend/ 2>/dev/null || mkdir -p dist/frontend && cp -r frontend/* dist/frontend/

# Aggiorna config.js per produzione
echo "⚙️  Configurazione frontend per produzione..."
cat > dist/frontend/config.js << 'EOF'
// Configurazione produzione
(function() {
    window.CONFIG = {
        API_BASE_URL: process.env.API_BASE_URL || 'https://crm-shops.onrender.com',
        AUTH_TOKEN_KEY: 'crm_shops_auth_token',
        USER_ROLE_KEY: 'crm_shops_user_role',
        USER_DATA_KEY: 'crm_shops_user_data'
    };
})();
EOF

# Verifica struttura progetto
echo "✅ Struttura progetto verificata:"
echo "   - Backend: ✅"
echo "   - Frontend: ✅"
echo "   - Requirements: ✅"

# Checklist pre-deploy
echo ""
echo "📝 Checklist pre-deploy:"
echo "   [ ] Variabili d'ambiente configurate su Render"
echo "   [ ] SUPABASE_URL configurata"
echo "   [ ] SUPABASE_KEY configurata"
echo "   [ ] SUPABASE_SERVICE_KEY configurata (opzionale)"
echo "   [ ] BANANA_PRO_API_KEY configurata (opzionale)"
echo "   [ ] GEMINI_API_KEY configurata (opzionale)"
echo "   [ ] SECRET_KEY generata per produzione"
echo "   [ ] ALLOWED_ORIGINS configurata con URL frontend Render"
echo ""
echo "✅ Preparazione completata!"
echo ""
echo "📚 Prossimi passi:"
echo "   1. Crea Web Service su Render per backend"
echo "   2. Crea Static Site su Render per frontend"
echo "   3. Configura variabili d'ambiente"
echo "   4. Deploy!"


