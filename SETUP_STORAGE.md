# Setup Storage Supabase

Questa guida ti aiuta a configurare i bucket Storage necessari per il progetto CRM Shops.

## Bucket Necessari

Il progetto richiede 3 bucket Storage:

1. **customer-photos** - Foto dei clienti
2. **product-images** - Immagini dei prodotti
3. **generated-images** - Immagini generate dall'AI

## Configurazione Manuale

### Passo 1: Accedi al Dashboard Supabase

1. Vai su https://app.supabase.com
2. Seleziona il progetto "Shop" (o il tuo progetto)
3. Vai su **Storage** nel menu laterale

### Passo 2: Crea i Bucket

Per ogni bucket:

1. Clicca su **"New bucket"**
2. Inserisci il nome del bucket (es. `customer-photos`)
3. Seleziona **"Public bucket"** (importante per accesso pubblico alle immagini)
4. Opzionalmente aggiungi una descrizione
5. Clicca **"Create bucket"**

### Passo 3: Configura Policy (Opzionale)

Per sicurezza, puoi configurare policy di accesso:

1. Vai su **Storage** → **Policies**
2. Crea policy per ogni bucket:
   - **SELECT**: Permetti lettura pubblica
   - **INSERT**: Solo utenti autenticati
   - **UPDATE**: Solo proprietario
   - **DELETE**: Solo proprietario

## Configurazione Automatica (Script)

Puoi usare lo script Python per verificare i bucket:

```bash
python backend/scripts/setup_storage.py
```

**Nota**: Lo script verifica solo l'esistenza dei bucket. La creazione deve essere fatta manualmente dal Dashboard.

## Verifica Configurazione

Dopo aver creato i bucket, puoi verificare con:

```python
from supabase import create_client
import os

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Verifica bucket
try:
    files = supabase.storage.from_("customer-photos").list()
    print("✅ Bucket customer-photos configurato")
except Exception as e:
    print(f"❌ Errore: {e}")
```

## URL Pubblici

Dopo la configurazione, le immagini saranno accessibili tramite URL pubblici:

```
https://[PROJECT_REF].supabase.co/storage/v1/object/public/customer-photos/[file-path]
```

## Troubleshooting

### Errore "Bucket not found"
- Verifica che il bucket sia stato creato
- Controlla il nome del bucket (deve essere esatto)
- Assicurati che il bucket sia pubblico

### Errore "Permission denied"
- Verifica le policy del bucket
- Controlla che SUPABASE_KEY sia configurata correttamente
- Per upload, potrebbe essere necessaria SUPABASE_SERVICE_KEY

### Immagini non visibili
- Verifica che il bucket sia pubblico
- Controlla l'URL dell'immagine
- Verifica CORS se necessario

## Prossimi Passi

Dopo aver configurato i bucket:
1. ✅ Testa l'upload di una foto cliente
2. ✅ Testa l'upload di un'immagine prodotto
3. ✅ Verifica che le immagini siano accessibili pubblicamente
4. ⏳ Configura policy di sicurezza se necessario

