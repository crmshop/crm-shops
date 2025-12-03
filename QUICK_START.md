# Quick Start Guide - CRM Shops

## 🚀 Avvio Rapido

### Prerequisiti
- Python 3.13+
- Account Supabase configurato
- Variabili d'ambiente configurate nel file `.env`

### 1. Setup Iniziale (solo la prima volta)

```bash
# Clona il repository (se non l'hai già fatto)
git clone https://github.com/crmshop/crm-shops.git
cd crm-shops

# Crea e attiva virtual environment
python3 -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate

# Installa dipendenze
pip install -r requirements.txt

# Configura variabili d'ambiente
cp .env.example .env
# Modifica .env con le tue credenziali Supabase
```

### 2. Avvia il Backend

```bash
# Terminal 1
./start_backend.sh

# Il backend sarà disponibile su http://localhost:8000
# Documentazione API: http://localhost:8000/docs
```

### 3. Avvia il Frontend

```bash
# Terminal 2
./start_frontend.sh

# Il frontend sarà disponibile su http://localhost:5500
```

### 4. Usa l'Applicazione

1. Apri il browser su `http://localhost:5500`
2. Registra un nuovo account (cliente o negoziante)
3. Accedi e inizia a usare l'applicazione

## 📋 Checklist Setup

- [ ] Python 3.13+ installato
- [ ] Virtual environment creato e attivato
- [ ] Dipendenze installate (`pip install -r requirements.txt`)
- [ ] File `.env` configurato con credenziali Supabase
- [ ] Backend avviato su porta 8000
- [ ] Frontend avviato su porta 5500
- [ ] Database Supabase configurato (migrazioni applicate)

## 🔧 Configurazione Supabase

Se non hai ancora configurato Supabase:

1. Vai su https://app.supabase.com
2. Crea un nuovo progetto (o usa quello esistente "Shop")
3. Applica le migrazioni:
   - Vai su SQL Editor
   - Copia il contenuto di `backend/migrations/001_initial_schema.sql`
   - Esegui la query
   - Ripeti per `backend/migrations/002_add_missing_indexes.sql`
4. Crea Storage bucket:
   - Vai su Storage
   - Crea bucket `customer-photos` (pubblico)
   - Crea bucket `product-images` (pubblico)
   - Crea bucket `generated-images` (pubblico)
5. Copia le credenziali nel file `.env`:
   - SUPABASE_URL
   - SUPABASE_KEY
   - SUPABASE_SERVICE_KEY (opzionale)

## 🧪 Test dell'Applicazione

### Test Backend

```bash
# Health check
curl http://localhost:8000/health

# Registrazione
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","role":"cliente"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

### Test Frontend

1. Apri `http://localhost:5500`
2. Verifica che la pagina si carichi
3. Prova a registrarti
4. Prova a fare login
5. Verifica la dashboard

## 📚 Documentazione

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **API Reference**: Vedi `API_DOCUMENTATION.md`
- **Database Schema**: Vedi `DATABASE_SCHEMA.md`
- **Progresso**: Vedi `PROGRESS.md`

## 🐛 Troubleshooting

### Backend non si avvia
- Verifica che la porta 8000 sia libera
- Controlla che tutte le dipendenze siano installate
- Verifica le credenziali Supabase nel `.env`

### Frontend non si connette al backend
- Verifica che il backend sia avviato
- Controlla che `API_BASE_URL` in `frontend/app.js` sia corretto
- Verifica CORS nel backend

### Errori di autenticazione
- Verifica che Supabase Auth sia configurato
- Controlla che le tabelle siano create
- Verifica i token nel localStorage del browser

### Errori database
- Verifica che le migrazioni siano applicate
- Controlla le credenziali Supabase
- Verifica la connessione al database

## 🎯 Prossimi Passi

1. ✅ Setup completato
2. ⏳ Configurare Storage buckets
3. ⏳ Abilitare Row Level Security (RLS)
4. ⏳ Implementare chiamate AI reali
5. ⏳ Aggiungere più funzionalità frontend
6. ⏳ Deploy su Render

## 💡 Tips

- Usa Swagger UI (`/docs`) per testare le API facilmente
- Controlla la console del browser per errori JavaScript
- Usa Network tab nel DevTools per debug API calls
- Verifica i log del backend per errori server-side



