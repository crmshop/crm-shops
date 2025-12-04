# Guida Deploy Completo su Render

Questa guida completa descrive come deployare sia il backend che il frontend su Render.

## 📋 Prerequisiti

- Account Render ([registrati qui](https://render.com))
- Repository GitHub con il codice
- Credenziali Supabase configurate
- (Opzionale) API keys per Banana Pro e Gemini

## 🚀 Deploy Backend

### 1. Crea Web Service

1. Vai su [Render Dashboard](https://dashboard.render.com)
2. Clicca **"New +"** → **"Web Service"**
3. Connetti il tuo repository GitHub
4. Seleziona il repository `CRM_shops`

### 2. Configurazione Backend

**Impostazioni Base:**
- **Name**: `crm-shops-backend`
- **Region**: Scegli la regione più vicina (es. `Oregon`)
- **Branch**: `main` (o il tuo branch principale)
- **Root Directory**: `/` (root del progetto)
- **Runtime**: `Python 3`
- **Build Command**: 
  ```bash
  pip install --upgrade pip && pip install -r requirements.txt
  ```
- **Start Command**: 
  ```bash
  uvicorn backend.main:app --host 0.0.0.0 --port $PORT --workers 2
  ```

### 3. Variabili d'Ambiente Backend

Aggiungi queste variabili nella sezione **Environment Variables**:

```bash
# Supabase (Obbligatorie)
SUPABASE_URL=https://tuo-progetto.supabase.co
SUPABASE_KEY=la_tua_anon_key
SUPABASE_SERVICE_KEY=la_tua_service_key  # Opzionale, solo per creare clienti

# Application
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=genera_una_chiave_sicura_lunga_e_casuale
PORT=8000

# CORS (Aggiorna con URL frontend dopo deploy)
# IMPORTANTE: Usa virgole per separare gli URL, senza spazi extra
ALLOWED_ORIGINS=https://crm-shops-frontend.onrender.com,http://localhost:5500

# AI Services (Opzionali)
BANANA_PRO_API_KEY=la_tua_banana_pro_key
GEMINI_API_KEY=la_tua_gemini_key
```

**Genera SECRET_KEY sicura:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Deploy Backend

1. Clicca **"Create Web Service"**
2. Attendi il deploy (5-10 minuti)
3. Verifica che il servizio sia **Live**
4. Testa l'endpoint: `https://crm-shops-backend.onrender.com/health`

## 🌐 Deploy Frontend

### 1. Crea Static Site

1. Vai su [Render Dashboard](https://dashboard.render.com)
2. Clicca **"New +"** → **"Static Site"**
3. Connetti lo stesso repository GitHub

### 2. Configurazione Frontend

**Impostazioni Base:**
- **Name**: `crm-shops-frontend`
- **Branch**: `main`
- **Root Directory**: `/frontend`
- **Build Command**: (lascia vuoto o `echo 'No build needed'`)
- **Publish Directory**: `/frontend` (o `/` se root directory è frontend)

### 3. Variabili d'Ambiente Frontend

Aggiungi:

```bash
API_BASE_URL=https://crm-shops-backend.onrender.com
```

**Nota**: Aggiorna `frontend/config.js` per usare questa variabile in produzione.

### 4. Deploy Frontend

1. Clicca **"Create Static Site"**
2. Attendi il deploy (2-5 minuti)
3. Verifica che il sito sia **Live**
4. Ottieni l'URL del frontend (es. `https://crm-shops-frontend.onrender.com`)

## 🔗 Collegamento Backend-Frontend

### 1. Aggiorna CORS Backend

Dopo aver ottenuto l'URL del frontend, aggiorna `ALLOWED_ORIGINS` nel backend:

```bash
ALLOWED_ORIGINS=https://crm-shops-frontend.onrender.com
```

Riavvia il backend per applicare le modifiche.

### 2. Aggiorna Config Frontend

Modifica `frontend/config.js` per usare l'URL del backend in produzione:

```javascript
API_BASE_URL: isProduction 
    ? 'https://crm-shops-backend.onrender.com' 
    : 'http://localhost:8000'
```

Commit e push le modifiche per triggerare un nuovo deploy.

## ✅ Verifica Deploy

### Test Backend

```bash
# Health check
curl https://crm-shops-backend.onrender.com/health

# API root
curl https://crm-shops-backend.onrender.com/
```

### Test Frontend

1. Apri l'URL del frontend nel browser
2. Verifica che carichi correttamente
3. Testa login/registrazione
4. Verifica chiamate API nella console del browser

## 🔧 Troubleshooting

### Backend non si avvia

- Verifica che tutte le variabili d'ambiente siano configurate
- Controlla i log su Render Dashboard
- Verifica che `requirements.txt` sia corretto
- Assicurati che `PORT` sia configurato correttamente

### Frontend non si connette al backend

- Verifica `API_BASE_URL` nel frontend
- Controlla CORS nel backend (`ALLOWED_ORIGINS`)
- Verifica che il backend sia Live
- Controlla la console del browser per errori

### Errori 500/502

- Controlla i log del backend su Render
- Verifica connessione Supabase
- Assicurati che le API keys siano valide

## 📊 Monitoraggio

### Log Backend

1. Vai su Render Dashboard
2. Seleziona il servizio backend
3. Tab **"Logs"** per vedere i log in tempo reale

### Metriche

Render fornisce metriche base:
- CPU usage
- Memory usage
- Request count
- Response time

## 🔄 Aggiornamenti

Per aggiornare il deploy:

1. Fai commit e push su GitHub
2. Render rileva automaticamente i cambiamenti
3. Triggera un nuovo deploy automaticamente
4. Monitora i log per verificare il successo

## 💰 Costi

- **Free Tier**: 
  - Backend: 750 ore/mese (spins down dopo 15 min di inattività)
  - Frontend: Illimitato
- **Starter Plan**: $7/mese per backend sempre attivo

## 📚 Risorse

- [Render Documentation](https://render.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Supabase Documentation](https://supabase.com/docs)

## 🎉 Deploy Completato!

Una volta completato, avrai:
- ✅ Backend API live su Render
- ✅ Frontend live su Render
- ✅ Database Supabase configurato
- ✅ Storage Supabase configurato
- ✅ Sistema completo funzionante

Buon deploy! 🚀

