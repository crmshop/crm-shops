# CRM Shops

Sistema CRM per negozi con AI generativa per visualizzazione abbigliamento su clienti.

## Descrizione

CRM Shops è un'applicazione web che permette ai negozianti di:
- Gestire il catalogo prodotti
- Permettere ai clienti di caricare foto personali
- Generare immagini AI dei clienti che indossano i capi del negozio
- Creare outfit personalizzati
- Gestire statistiche e promozioni

## Tecnologie

- **Backend**: Python 3.13, FastAPI
- **Frontend**: HTML, CSS, JavaScript vanilla
- **Database**: PostgreSQL (Supabase)
- **Storage**: Supabase Storage
- **AI**: Banana Pro + Google Gemini
- **Deploy**: Render

## Setup Ambiente di Sviluppo

### Prerequisiti

- Python 3.13+
- Git
- Account Supabase (vedi [SETUP_SUPABASE.md](SETUP_SUPABASE.md))
- Account GitHub e GitHub CLI (`gh`) (vedi [SETUP_GITHUB.md](SETUP_GITHUB.md))

### Installazione

1. Clonare il repository:
```bash
git clone <repository-url>
cd CRM_shops
```

2. Creare e attivare virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate
```

3. Installare dipendenze:
```bash
pip install -r requirements.txt
```

4. Configurare variabili d'ambiente:
```bash
cp .env.example .env
# Modificare .env con le tue credenziali
```

5. Avviare il backend:
```bash
# Opzione 1: Usando lo script
./start_backend.sh

# Opzione 2: Manualmente
cd backend
python main.py
```

Il server sarà disponibile su `http://localhost:8000`

### Endpoint disponibili

- `GET /` - Informazioni API
- `GET /health` - Health check con stato Supabase
- `POST /api/auth/login` - Login utente
- `POST /api/auth/register` - Registrazione nuovo utente
- `POST /api/auth/logout` - Logout utente

6. Aprire il frontend:
Aprire `frontend/index.html` nel browser o servire con un server HTTP locale.

## Struttura Progetto

```
CRM_shops/
├── backend/          # API FastAPI
│   ├── main.py      # Entry point backend
│   └── ...
├── frontend/         # Interfaccia utente
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── requirements.txt  # Dipendenze Python
├── .env.example      # Template variabili d'ambiente
└── README.md
```

## Variabili d'Ambiente

Vedi `.env.example` per la lista completa delle variabili necessarie.

## Sviluppo

Il progetto è gestito con Task Master. Per vedere le task:

```bash
npx task-master-ai list
```

Per vedere la prossima task da fare:

```bash
npx task-master-ai next
```

## Licenza

[Da definire]







