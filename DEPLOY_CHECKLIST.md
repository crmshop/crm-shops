# Checklist Pre-Deploy

Usa questa checklist prima di fare il deploy su Render.

## ✅ Preparazione Repository

- [ ] Repository GitHub configurato e sincronizzato
- [ ] Branch principale (main/master) aggiornato
- [ ] Tutti i file committati
- [ ] `.gitignore` configurato correttamente (esclude `.env`, `venv/`, etc.)

## ✅ Backend

- [ ] `requirements.txt` aggiornato con tutte le dipendenze
- [ ] `backend/main.py` funziona localmente
- [ ] Variabili d'ambiente documentate in `.env.example`
- [ ] Health check endpoint `/health` funzionante
- [ ] CORS configurato per il dominio frontend
- [ ] Logging configurato correttamente

## ✅ Frontend

- [ ] `frontend/config.js` configurato per produzione
- [ ] URL API backend aggiornato in `config.js`
- [ ] Tutti i file statici presenti
- [ ] Testato localmente con backend

## ✅ Database Supabase

- [ ] Progetto Supabase creato
- [ ] Migrazioni applicate
- [ ] Storage buckets creati:
  - [ ] `customer-photos` (pubblico)
  - [ ] `product-images` (pubblico)
  - [ ] `generated-images` (pubblico)
- [ ] Row Level Security configurata (opzionale ma consigliato)
- [ ] Credenziali API salvate in modo sicuro

## ✅ Variabili d'Ambiente Render

Configura queste variabili nel Dashboard Render per il backend:

- [ ] `SUPABASE_URL` - URL del progetto Supabase
- [ ] `SUPABASE_KEY` - Anon key di Supabase
- [ ] `SUPABASE_SERVICE_KEY` - Service role key (per operazioni admin)
- [ ] `ENVIRONMENT=production`
- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` - Chiave segreta sicura (genera con: `openssl rand -hex 32`)
- [ ] `ALLOWED_ORIGINS` - URL del frontend su Render (es: `https://crm-shops-frontend.onrender.com`)
- [ ] `BANANA_PRO_API_KEY` - Se usi Banana Pro
- [ ] `GEMINI_API_KEY` - Se usi Google Gemini

## ✅ Test Pre-Deploy

Esegui questi comandi localmente:

```bash
# Verifica variabili d'ambiente
python scripts/check_env.py

# Verifica struttura progetto
./scripts/deploy_check.sh

# Test backend locale
./start_backend.sh
# In un altro terminale:
curl http://localhost:8000/health

# Test frontend locale
./start_frontend.sh
# Apri http://localhost:5500 nel browser
```

## ✅ Deploy Render

### Backend

1. [ ] Crea nuovo Web Service su Render
2. [ ] Connetti repository GitHub
3. [ ] Configura:
   - Name: `crm-shops-backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
4. [ ] Aggiungi tutte le variabili d'ambiente
5. [ ] Avvia deploy
6. [ ] Verifica log per errori
7. [ ] Testa endpoint: `https://[SERVICE-URL]/health`

### Frontend

1. [ ] Crea nuovo Static Site su Render
2. [ ] Connetti repository GitHub
3. [ ] Configura:
   - Name: `crm-shops-frontend`
   - Build Command: (vuoto o `./scripts/build_frontend.sh`)
   - Publish Directory: `frontend`
4. [ ] Aggiungi variabile `API_BASE_URL` se necessario
5. [ ] Avvia deploy
6. [ ] Verifica che il sito sia accessibile

## ✅ Post-Deploy

- [ ] Testa login/registrazione
- [ ] Testa creazione negozio (negoziante)
- [ ] Testa creazione prodotto
- [ ] Testa upload foto cliente
- [ ] Verifica che le immagini siano accessibili pubblicamente
- [ ] Controlla log per errori
- [ ] Verifica performance

## ✅ Monitoring

- [ ] Configura alert su Render per downtime
- [ ] Monitora log per errori
- [ ] Verifica uso risorse (CPU, RAM)
- [ ] Controlla costi mensili stimati

## 🔧 Troubleshooting

### Backend non si avvia
- Verifica variabili d'ambiente
- Controlla log su Render
- Verifica che il comando start sia corretto
- Controlla che tutte le dipendenze siano in `requirements.txt`

### CORS errors
- Verifica `ALLOWED_ORIGINS` include l'URL del frontend
- Controlla che il frontend usi l'URL corretto del backend

### Database connection errors
- Verifica `SUPABASE_URL` e `SUPABASE_KEY`
- Controlla che Supabase permetta connessioni da Render IPs
- Verifica che il progetto Supabase sia attivo

### Static files non serviti
- Verifica `Publish Directory` nel Static Site
- Controlla che i file siano nel branch corretto
- Verifica che `config.js` sia presente

## 📚 Risorse

- [Documentazione Render](https://render.com/docs)
- [Documentazione Supabase](https://supabase.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

