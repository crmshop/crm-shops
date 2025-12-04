#!/bin/bash
# Script per verificare lo stato dei deploy su Render

echo "🔍 Verifica Deploy Render - CRM Shops"
echo "======================================"
echo ""

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# URL dei servizi (aggiorna se diversi)
BACKEND_URL="${BACKEND_URL:-https://crm-shops.onrender.com}"
FRONTEND_URL="${FRONTEND_URL:-https://crm-shops-frontend.onrender.com}"

echo "📡 URL Configurati:"
echo "   Backend:  $BACKEND_URL"
echo "   Frontend: $FRONTEND_URL"
echo ""

# Funzione per testare endpoint
test_endpoint() {
    local url=$1
    local name=$2
    local expected_status=${3:-200}
    
    echo -n "Test $name... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url" 2>&1)
    exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        echo -e "${RED}❌ ERRORE${NC} (non raggiungibile)"
        return 1
    fi
    
    if [ "$response" = "$expected_status" ] || [ "$response" = "200" ]; then
        echo -e "${GREEN}✅ OK${NC} (HTTP $response)"
        return 0
    else
        echo -e "${YELLOW}⚠️  HTTP $response${NC}"
        return 1
    fi
}

# Test Backend
echo "🔧 Test Backend:"
echo "----------------"
test_endpoint "$BACKEND_URL/" "Root endpoint"
test_endpoint "$BACKEND_URL/health" "Health check"
test_endpoint "$BACKEND_URL/docs" "API Docs"

# Test dettagliato health check
echo ""
echo "📊 Dettagli Health Check:"
health_response=$(curl -s --max-time 10 "$BACKEND_URL/health" 2>&1)
if [ $? -eq 0 ] && [ -n "$health_response" ]; then
    echo "$health_response" | python3 -m json.tool 2>/dev/null || echo "$health_response"
else
    echo -e "${RED}❌ Health endpoint non raggiungibile${NC}"
fi

echo ""
echo ""

# Test Frontend
echo "🌐 Test Frontend:"
echo "-----------------"
test_endpoint "$FRONTEND_URL" "Frontend homepage"

# Test dettagliato frontend
echo ""
echo "📄 Contenuto Frontend:"
frontend_response=$(curl -s --max-time 10 "$FRONTEND_URL" 2>&1 | head -5)
if [ -n "$frontend_response" ] && [[ ! "$frontend_response" =~ "not found" ]]; then
    echo -e "${GREEN}✅ Frontend raggiungibile${NC}"
    echo "Prime righe:"
    echo "$frontend_response"
else
    echo -e "${RED}❌ Frontend non raggiungibile o non deployato${NC}"
fi

echo ""
echo "======================================"
echo "✅ Verifica completata"
echo ""
echo "💡 Suggerimenti:"
echo "   - Se tutti i test falliscono, verifica che i servizi siano deployati su Render"
echo "   - Controlla i log su Render Dashboard"
echo "   - Verifica le variabili d'ambiente configurate"
echo "   - Assicurati che i servizi siano in stato 'Live'"

