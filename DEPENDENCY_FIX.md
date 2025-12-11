# Risoluzione Conflitti Dipendenze

## Problema

Durante l'installazione di `requirements.txt` si verificava questo errore:

```
ERROR: Cannot install -r requirements.txt (line 2), -r requirements.txt (line 23), -r requirements.txt (line 7), anyio==3.7.1, httpx==0.24.1, uvicorn[standard]==0.24.0 and websockets==12.0 because these package versions have conflicting dependencies.
```

## Causa

Il problema era causato da versioni esplicite e incompatibili di:
- `httpx==0.24.1`
- `anyio==3.7.1` 
- `websockets==12.0`

Queste versioni entravano in conflitto con i requisiti di:
- `supabase==2.0.0` (che richiede versioni specifiche di httpx/anyio)
- `uvicorn[standard]==0.24.0` (che richiede versioni specifiche di websockets/anyio)

## Soluzione Applicata

### 1. Rimosse dipendenze transitive esplicite
- ❌ Rimosso: `anyio==3.7.1`
- ❌ Rimosso: `websockets==12.0`

Queste sono **dipendenze transitive** (installate automaticamente da altri pacchetti), quindi non devono essere specificate esplicitamente.

### 2. Aggiornato httpx con range flessibile
- ✅ Cambiato: `httpx==0.24.1` → `httpx>=0.24.0,<0.28.0`

`httpx` è usato direttamente nel codice (`backend/services/gemini.py`, `backend/services/banana_pro.py`), quindi deve rimanere, ma con un range flessibile che permette a pip di risolvere automaticamente i conflitti.

### 3. Risultato finale

```python
# HTTP Client - Versioni compatibili con supabase 2.0.0
# httpx è usato direttamente nel codice (gemini.py, banana_pro.py)
# Usiamo un range flessibile per permettere a pip di risolvere conflitti
httpx>=0.24.0,<0.28.0
requests==2.31.0
# NOTA: anyio e websockets sono dipendenze transitive di httpx/uvicorn/supabase
# NON specificare versioni esplicite - pip le risolverà automaticamente
```

## Come Funziona Ora

Quando installi `requirements.txt`:

1. **pip installa supabase==2.0.0**
   - Supabase richiede automaticamente versioni compatibili di `httpx`, `anyio`, `websockets`

2. **pip installa uvicorn[standard]==0.24.0**
   - Uvicorn richiede automaticamente versioni compatibili di `websockets`, `anyio`

3. **pip installa httpx>=0.24.0,<0.28.0**
   - Pip trova una versione compatibile con entrambi supabase e uvicorn
   - Installa automaticamente le versioni corrette di `anyio` e `websockets`

4. **Risultato**: Nessun conflitto! ✅

## Testare la Soluzione

```bash
# 1. Crea/attiva virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# oppure: venv\Scripts\activate  # Windows

# 2. Installa dipendenze
pip install -r requirements.txt

# 3. Verifica che tutto sia installato correttamente
pip check

# 4. Testa l'applicazione
python -m backend.main
```

## Best Practices per il Futuro

### ✅ DO (Fai)
- Specifica versioni esplicite solo per pacchetti usati **direttamente** nel codice
- Usa range flessibili (`>=x,<y`) quando possibile per permettere risoluzione automatica
- Lascia che pip risolva automaticamente le dipendenze transitive

### ❌ DON'T (Non Fare)
- Non specificare versioni esplicite per dipendenze transitive (`anyio`, `websockets`, `httpcore`, ecc.)
- Non fissare versioni troppo specifiche se non necessario (`==` invece di `>=`)
- Non duplicare dipendenze già gestite da altri pacchetti

## Dipendenze Transitive Comuni

Questi pacchetti sono spesso dipendenze transitive e **non dovrebbero** essere nel `requirements.txt`:

- `anyio` (gestito da httpx/uvicorn)
- `websockets` (gestito da uvicorn)
- `httpcore` (gestito da httpx)
- `h11` (gestito da httpcore)
- `sniffio` (gestito da anyio)

## Conflitti Risolti

### Conflitto 1: FastAPI vs google-genai (anyio)

#### Problema
- `fastapi==0.104.1` richiede `anyio<4.0.0 and >=3.7.1`
- `google-genai>=1.9.0` richiede `anyio<5.0.0 and >=4.8.0`
- **Incompatibili!** ❌

#### Soluzione
Aggiornato FastAPI a `>=0.108.0` che supporta `anyio 4.x.x`:
- ✅ FastAPI 0.108.0+ supporta anyio 4.x.x
- ✅ Compatibile con google-genai 1.9.0+
- ✅ Uvicorn >=0.24.0 è compatibile

### Conflitto 2: httpx vs google-genai

#### Problema
- `httpx>=0.24.0,<0.28.0` (range precedente)
- `google-genai 1.33.0+` richiede `httpx>=0.28.1,<1.0.0`
- **Incompatibili!** ❌

#### Soluzione
Aggiornato httpx a `>=0.28.1,<1.0.0`:
- ✅ Compatibile con google-genai 1.33.0+
- ✅ Compatibile con supabase 2.0.0 (richiede httpx >= 0.28)
- ✅ Range flessibile permette a pip di risolvere automaticamente

#### Modifiche Applicate
```python
# Prima
httpx>=0.24.0,<0.28.0  # Troppo vecchio per google-genai 1.33.0+

# Dopo
httpx>=0.28.1,<1.0.0  # Compatibile con google-genai e supabase
```

### Problema
- `fastapi==0.104.1` richiede `anyio<4.0.0 and >=3.7.1`
- `google-genai>=1.9.0` richiede `anyio<5.0.0 and >=4.8.0`
- **Incompatibili!** ❌

### Soluzione
Aggiornato FastAPI a `>=0.108.0` che supporta `anyio 4.x.x`:
- ✅ FastAPI 0.108.0+ supporta anyio 4.x.x
- ✅ Compatibile con google-genai 1.9.0+
- ✅ Uvicorn >=0.24.0 è compatibile

### Modifiche Applicate
```python
# Prima
fastapi==0.104.1  # Supporta solo anyio < 4.0.0

# Dopo
fastapi>=0.108.0  # Supporta anyio 4.x.x
```

## Se Incontri Ancora Problemi

1. **Verifica conflitti:**
   ```bash
   pip check
   ```

2. **Vedi l'albero delle dipendenze:**
   ```bash
   pipdeptree
   ```

3. **Installa con risoluzione verbosa:**
   ```bash
   pip install -r requirements.txt -v
   ```

4. **Considera di aggiornare tutto:**
   ```bash
   pip install --upgrade pip
   pip install --upgrade -r requirements.txt
   ```

## Note

- Le versioni risolte automaticamente da pip saranno compatibili con tutti i pacchetti
- Se hai bisogno di versioni specifiche per motivi di sicurezza/compatibilità, documentale nel codice
- Considera di usare `pip-tools` per generare un `requirements.txt` con versioni fisse dopo la risoluzione
