# CRM Shops

Sistema CRM per negozi con AI generativa per visualizzazione abbigliamento su clienti.

## 🚀 Quick Start

```bash
# 1. Clona il repository
git clone <repository-url>
cd CRM_shops

# 2. Crea e attiva virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Installa dipendenze
pip install -r requirements.txt

# 4. Configura variabili d'ambiente
cp .env.example .env
# Modifica .env con le tue credenziali

# 5. Avvia backend (terminale 1)
./start_backend.sh

# 6. Avvia frontend (terminale 2)
./start_frontend.sh

# 7. Apri browser
# Frontend: http://localhost:5500
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## 📋 Prerequisiti

- Python 3.11+
- Git
- Account Supabase ([Guida Setup](SETUP_SUPABASE.md))
- Account GitHub ([Guida Setup](SETUP_GITHUB.md))
- (Opzionale) Account Render per deploy

## 🏗️ Architettura

```
CRM_shops/
├── backend/              # API FastAPI
│   ├── routes/          # Endpoint API
│   ├── middleware/      # Autenticazione JWT
│   ├── services/        # Servizi AI
│   ├── models/          # Modelli database
│   └── utils/           # Utility
├── frontend/            # Interfaccia utente
│   ├── pages/          # Pagine dinamiche
│   ├── index.html
│   ├── app.js
│   ├── config.js       # Configurazione
│   └── styles.css
├── scripts/            # Script utilità
└── docs/               # Documentazione
```

## 🎯 Funzionalità

### Per Negozianti
- ✅ Gestione negozi e prodotti
- ✅ Creazione outfit personalizzati
- ✅ Visualizzazione statistiche clienti
- ✅ Generazione immagini AI promozionali

### Per Clienti
- ✅ Upload foto personali
- ✅ Creazione outfit personalizzati
- ✅ Visualizzazione simulazioni AI
- ✅ Gestione consenso GDPR

## 📚 Documentazione

- [Quick Start Guide](QUICK_START.md) - Guida rapida
- [API Documentation](API_DOCUMENTATION.md) - Documentazione API completa
- [Database Schema](DATABASE_SCHEMA.md) - Schema database
- [Deploy Guide](DEPLOY.md) - Guida deploy Render
- [Deploy Checklist](DEPLOY_CHECKLIST.md) - Checklist pre-deploy
- [Setup Supabase](SETUP_SUPABASE.md) - Configurazione Supabase
- [Setup Storage](SETUP_STORAGE.md) - Configurazione Storage buckets
- [Setup GitHub](SETUP_GITHUB.md) - Configurazione GitHub

## 🔧 Tecnologie

- **Backend**: Python 3.11, FastAPI, Uvicorn
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Database**: PostgreSQL (Supabase)
- **Storage**: Supabase Storage
- **AI**: Banana Pro + Google Gemini (da integrare)
- **Deploy**: Render
- **CI/CD**: GitHub Actions

## 📊 Statistiche Progetto

- **80+ file** totali
- **2063+ linee** codice Python
- **577+ linee** codice JavaScript
- **12 file** documentazione
- **25+ endpoint** API
- **10 tabelle** database

## 🧪 Testing

```bash
# Verifica variabili d'ambiente
python scripts/check_env.py

# Verifica struttura progetto
./scripts/deploy_check.sh

# Test backend
curl http://localhost:8000/health
```

## 🚢 Deploy

Vedi [DEPLOY.md](DEPLOY.md) per la guida completa al deploy su Render.

### Quick Deploy

1. Configura variabili d'ambiente su Render
2. Connetti repository GitHub
3. Render rileverà automaticamente `render.yaml`
4. Deploy automatico ad ogni push su `main`

## 🔒 Sicurezza

- Autenticazione JWT con Supabase Auth
- Row Level Security (RLS) su database
- Validazione input con Pydantic
- CORS configurato
- Variabili d'ambiente per credenziali

## 📝 Licenza

Questo progetto è privato e proprietario.

## 🤝 Contribuire

1. Fork il repository
2. Crea branch feature (`git checkout -b feature/AmazingFeature`)
3. Commit modifiche (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri Pull Request

## 📞 Supporto

Per domande o supporto:
- Apri una Issue su GitHub
- Consulta la documentazione in `/docs`

## 🎉 Stato Progetto

✅ **Backend**: Completo e funzionante
✅ **Frontend**: Completo con routing e autenticazione
✅ **Database**: Schema completo e migrato
✅ **Documentazione**: Completa
⏳ **AI Integration**: Struttura pronta, da integrare
⏳ **Deploy**: Pronto per produzione

---

**Versione**: 0.1.0  
**Ultimo aggiornamento**: 2025
