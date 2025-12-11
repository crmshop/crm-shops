# Guida Sicurezza API Keys

## Problema: API Key Compromessa

Se ricevi questo errore:
```
403 PERMISSION_DENIED: Your API key was reported as leaked. Please use another API key.
```

Significa che la tua API key di Google è stata compromessa e deve essere sostituita immediatamente.

## Soluzione Immediata

### 1. Revoca la Vecchia API Key

1. Vai su [Google AI Studio](https://aistudio.google.com/)
2. Accedi con il tuo account Google
3. Vai su **Settings** → **API Keys**
4. Trova la chiave compromessa e clicca **Delete** o **Revoke**
5. ⚠️ **IMPORTANTE**: Revoca immediatamente per prevenire uso non autorizzato

### 2. Genera una Nuova API Key

1. Sempre su [Google AI Studio](https://aistudio.google.com/)
2. Vai su **Settings** → **API Keys**
3. Clicca **Create API Key**
4. Scegli il progetto Google Cloud (o creane uno nuovo)
5. Copia la nuova API key generata

### 3. Aggiorna la Configurazione

#### Opzione A: Variabile d'Ambiente (Consigliato per Produzione)

**Su Render:**
1. Vai su Render Dashboard → Il tuo servizio → **Environment**
2. Trova `BANANA_PRO_API_KEY`
3. Clicca **Edit** e incolla la nuova API key
4. Salva e riavvia il servizio

**Locale (.env):**
```bash
# Apri il file .env nella root del progetto
BANANA_PRO_API_KEY=la_tua_nuova_api_key_qui
```

#### Opzione B: File di Configurazione (Solo per Sviluppo)

⚠️ **NON fare questo in produzione!**

Se stai usando un file di configurazione locale, aggiorna:
```python
# backend/config.py (SOLO per sviluppo locale)
BANANA_PRO_API_KEY = "la_tua_nuova_api_key_qui"
```

### 4. Verifica che Funzioni

Dopo aver aggiornato l'API key:
1. Riavvia l'applicazione
2. Prova a generare un'immagine
3. Verifica che non ci siano più errori 403

## Best Practices per Sicurezza API Keys

### ✅ DO (Fai)

1. **Usa Variabili d'Ambiente**
   - ✅ Salva API keys in `.env` (locale) o variabili d'ambiente (produzione)
   - ✅ Aggiungi `.env` a `.gitignore`
   - ✅ Non committare mai API keys nel codice

2. **Limita Permessi API Key**
   - ✅ Usa API keys con permessi minimi necessari
   - ✅ Configura restrizioni IP se possibile
   - ✅ Abilita solo le API necessarie

3. **Monitora Uso**
   - ✅ Controlla regolarmente l'uso delle API keys su Google Cloud Console
   - ✅ Configura alert per uso anomalo
   - ✅ Revoca immediatamente chiavi compromesse

4. **Rotazione Periodica**
   - ✅ Cambia API keys periodicamente (es. ogni 3-6 mesi)
   - ✅ Usa chiavi diverse per sviluppo e produzione

### ❌ DON'T (Non Fare)

1. **NON Committare API Keys**
   ```bash
   # ❌ SBAGLIATO - Mai fare questo!
   git add .env
   git commit -m "Add API keys"
   ```

2. **NON Condividere API Keys**
   - ❌ Non inviare API keys via email
   - ❌ Non pubblicare API keys su GitHub/GitLab
   - ❌ Non condividere API keys su chat pubbliche

3. **NON Usare Chiavi Hardcoded**
   ```python
   # ❌ SBAGLIATO - Mai fare questo!
   API_KEY = "AIzaSyC-example-key-here"
   ```

4. **NON Usare Stesse Chiavi per Dev/Prod**
   - ❌ Non riutilizzare la stessa API key per sviluppo e produzione
   - ❌ Crea chiavi separate per ogni ambiente

## Configurazione Corretta

### File .env (Locale)
```bash
# .env - NON committare questo file!
BANANA_PRO_API_KEY=AIzaSyC-la-tua-api-key-qui
GEMINI_API_KEY=AIzaSyC-la-tua-api-key-qui
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGc...
```

### .gitignore
```gitignore
# Environment variables
.env
.env.local
.env.*.local
```

### backend/config.py
```python
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Carica da variabili d'ambiente
    BANANA_PRO_API_KEY: str = os.getenv("BANANA_PRO_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    class Config:
        env_file = ".env"  # Carica da .env se presente
```

## Verifica Configurazione

### Controlla che .env sia in .gitignore
```bash
git check-ignore .env
# Dovrebbe restituire: .env
```

### Verifica che .env non sia tracciato da Git
```bash
git ls-files .env
# Non dovrebbe restituire nulla
```

### Test API Key (Locale)
```bash
# Attiva virtual environment
source venv/bin/activate

# Testa che l'API key funzioni
python -c "from backend.config import settings; print('API Key configurata:', bool(settings.BANANA_PRO_API_KEY))"
```

## Troubleshooting

### "API key not found"
- Verifica che la variabile d'ambiente sia impostata correttamente
- Controlla che il nome della variabile sia esatto: `BANANA_PRO_API_KEY`
- Riavvia l'applicazione dopo aver modificato le variabili d'ambiente

### "403 PERMISSION_DENIED"
- La API key potrebbe essere stata revocata
- Verifica che la API key abbia i permessi corretti su Google Cloud Console
- Controlla che la fatturazione sia attiva sul progetto Google Cloud

### "Quota exceeded"
- Verifica i limiti di quota su Google Cloud Console
- Controlla che la fatturazione sia configurata correttamente
- Considera di aumentare i limiti se necessario

## Risorse Utili

- [Google AI Studio](https://aistudio.google.com/) - Gestione API Keys
- [Google Cloud Console](https://console.cloud.google.com/) - Gestione progetti e fatturazione
- [Supabase Dashboard](https://app.supabase.com/) - Gestione credenziali Supabase

## Checklist Post-Compromissione

Dopo aver sostituito una API key compromessa:

- [ ] Vecchia API key revocata su Google AI Studio
- [ ] Nuova API key generata
- [ ] Nuova API key configurata su Render (produzione)
- [ ] Nuova API key configurata in `.env` (locale)
- [ ] Applicazione riavviata e testata
- [ ] Verificato che non ci siano più errori 403
- [ ] Controllato uso API su Google Cloud Console
- [ ] Configurati alert per uso anomalo (opzionale ma consigliato)
