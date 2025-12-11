# Ottimizzazioni Deploy Render

Questo documento descrive le ottimizzazioni implementate per velocizzare i deploy su Render.

## Problema Iniziale

I deploy su Render erano troppo lenti perché:
- Installazione completa delle dipendenze ad ogni deploy
- Nessun caching delle dipendenze Python
- Script di start troppo verboso con molte verifiche
- Nessun worker multiplo per uvicorn

## Soluzioni Implementate

### 1. File render.yaml

Creato file `render.yaml` nella root del progetto con:
- **Build Command Ottimizzato**: Usa cache pip per velocizzare installazioni successive
- **Workers Multipli**: 2 workers per uvicorn per migliori performance
- **Health Checks**: Configurato endpoint `/health` per monitoraggio automatico
- **Python Version**: Specificata versione 3.11.0 per consistenza

```yaml
buildCommand: |
  pip install --upgrade pip setuptools wheel &&
  pip install --cache-dir ~/.cache/pip -r requirements.txt
startCommand: python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT --workers 2
```

### 2. Script start_render.sh Ottimizzato

Semplificato lo script di avvio:
- Rimossi controlli verbosi non necessari
- Rimossa doppia verifica di uvicorn (già installato nel build)
- Avvio diretto con workers multipli
- Mantenuto solo il necessario per il funzionamento

**Prima**: ~20 righe con molti controlli  
**Dopo**: ~8 righe essenziali

### 3. File .python-version

Aggiunto file `.python-version` per garantire che Render usi Python 3.11.0.

## Risultati Attesi

### Tempi di Deploy

- **Primo Deploy**: 5-8 minuti (normale, installazione completa)
- **Deploy Successivi**: 2-4 minuti (con cache pip attiva)
- **Hot Reload**: 30-60 secondi (solo riavvio servizio)

### Performance Runtime

- **Workers Multipli**: Miglior gestione del carico con 2 workers
- **Health Checks**: Monitoraggio automatico dello stato del servizio
- **Caching**: Build più veloci grazie al caching pip

## Come Usare

### Deploy Automatico (Consigliato)

1. Pusha il file `render.yaml` su GitHub
2. Vai su Render Dashboard → "New +" → "Blueprint"
3. Connetti il repository
4. Render configurerà tutto automaticamente

### Deploy Manuale

Se preferisci configurare manualmente, usa questi comandi:

**Build Command:**
```bash
pip install --upgrade pip setuptools wheel && pip install --cache-dir ~/.cache/pip -r requirements.txt
```

**Start Command:**
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT --workers 2
```

**Health Check Path:**
```
/health
```

## Variabili d'Ambiente Importanti

Assicurati di configurare queste variabili su Render:

```bash
PYTHON_VERSION=3.11.0
PYTHONUNBUFFERED=1
PIP_NO_CACHE_DIR=0  # Abilita cache pip
```

## Monitoraggio

Dopo il deploy, verifica:
- ✅ Health check funzionante: `https://tuo-servizio.onrender.com/health`
- ✅ Log senza errori su Render Dashboard
- ✅ Tempi di deploy migliorati nei log

## Ulteriori Ottimizzazioni Possibili

Se i deploy sono ancora lenti, considera:

1. **Upgrade Piano**: Passa a Standard o Pro per più risorse CPU/RAM
2. **Dockerfile**: Usa Dockerfile con layer caching più efficiente
3. **Dipendenze**: Rimuovi dipendenze non necessarie da `requirements.txt`
4. **Build Separato**: Considera build separato per dipendenze pesanti

## Troubleshooting

### Cache pip non funziona
- Verifica che `PIP_NO_CACHE_DIR=0` sia impostato
- Controlla che il build command usi `--cache-dir ~/.cache/pip`

### Workers causano errori
- Riduci a 1 worker: `--workers 1`
- Verifica che l'app sia thread-safe

### Deploy ancora lento
- Controlla i log di build per vedere dove si blocca
- Verifica la dimensione di `requirements.txt`
- Considera di usare `requirements-prod.txt` con solo dipendenze essenziali
