# Guida Deploy - CRM Shops

Questa guida descrive come fare il deploy del progetto CRM Shops su Render.

## Prerequisiti

- Account Render (https://render.com)
- Repository GitHub configurato
- Credenziali Supabase configurate
- Variabili d'ambiente pronte

## Deploy Backend su Render

### 1. Crea Web Service

1. Accedi a Render Dashboard
2. Clicca **"New +"** → **"Web Service"**
3. Connetti il repository GitHub `crm-shops`
4. Configura il servizio:
   - **Name**: `crm-shops-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

### 2. Configura Variabili d'Ambiente

Aggiungi tutte le variabili dal file `.env`:

```
SUPABASE_URL=https://[PROJECT_REF].supabase.co
SUPABASE_KEY=[ANON_KEY]
SUPABASE_SERVICE_KEY=[SERVICE_KEY]
BANANA_PRO_API_KEY=[KEY]
GEMINI_API_KEY=[KEY]
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=[GENERA_UNA_CHIAVE_SICURA]
ALLOWED_ORIGINS=https://crm-shops-frontend.onrender.com
```

### 3. Configura CORS

Nel file `backend/main.py`, aggiungi l'URL di Render agli allowed origins:

```python
ALLOWED_ORIGINS = [
    "https://crm-shops-frontend.onrender.com",
    # Altri domini se necessario
]
```

## Deploy Frontend su Render

### 1. Crea Static Site

1. Clicca **"New +"** → **"Static Site"**
2. Connetti il repository GitHub
3. Configura:
   - **Name**: `crm-shops-frontend`
   - **Build Command**: (vuoto, è già HTML statico)
   - **Publish Directory**: `frontend`

### 2. Configura Variabili d'Ambiente

Aggiungi:

```
API_BASE_URL=https://crm-shops-backend.onrender.com
```

**Nota**: Dovrai aggiornare `frontend/app.js` per usare questa variabile invece di hardcoded `localhost:8000`.

## Deploy Database (Opzionale)

Se vuoi usare un database Render invece di Supabase:

1. Crea **PostgreSQL** su Render
2. Aggiorna `DATABASE_URL` nelle variabili d'ambiente
3. Applica le migrazioni SQL

## Post-Deploy Checklist

- [ ] Backend deployato e raggiungibile
- [ ] Frontend deployato e raggiungibile
- [ ] Variabili d'ambiente configurate
- [ ] CORS configurato correttamente
- [ ] Health check funzionante
- [ ] Storage buckets configurati su Supabase
- [ ] Test autenticazione funzionante
- [ ] Test upload immagini funzionante

## URL di Produzione

Dopo il deploy avrai:

- **Backend**: `https://crm-shops-backend.onrender.com`
- **Frontend**: `https://crm-shops-frontend.onrender.com`
- **API Docs**: `https://crm-shops-backend.onrender.com/docs`

## Monitoring

Render fornisce:
- Log in tempo reale
- Metriche performance
- Alert automatici
- SSL automatico

## Costi

- **Web Service**: Da $7/mese (Starter plan)
- **Static Site**: Gratis
- **PostgreSQL**: Da $7/mese (se usato)

## Alternative: Deploy Manuale

Se preferisci deploy manuale:

1. **Backend**: VPS con Nginx + Gunicorn
2. **Frontend**: Netlify, Vercel, o GitHub Pages
3. **Database**: Mantieni Supabase (consigliato)

## Troubleshooting

### Backend non si avvia
- Verifica variabili d'ambiente
- Controlla i log su Render
- Verifica che il comando start sia corretto

### CORS errors
- Verifica ALLOWED_ORIGINS nel backend
- Controlla che includa l'URL del frontend

### Database connection errors
- Verifica SUPABASE_URL e SUPABASE_KEY
- Controlla che Supabase permetta connessioni da Render IPs

### Static files non serviti
- Verifica Publish Directory nel Static Site
- Controlla che i file siano nel branch corretto

