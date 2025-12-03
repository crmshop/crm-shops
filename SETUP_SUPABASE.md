# Guida Setup Supabase

Questa guida ti aiuterà a configurare Supabase per il progetto CRM Shops.

## Passi per configurare Supabase

### 1. Creare account Supabase

1. Vai su [https://supabase.com](https://supabase.com)
2. Clicca su "Start your project" o "Sign Up"
3. Crea un account (puoi usare GitHub, Google, o email)

### 2. Creare un nuovo progetto

1. Dopo il login, clicca su "New Project"
2. Compila i campi:
   - **Name**: `crm-shops` (o un nome a tua scelta)
   - **Database Password**: Scegli una password sicura (salvala!)
   - **Region**: Scegli la regione più vicina a te
   - **Pricing Plan**: Scegli il piano gratuito per iniziare
3. Clicca su "Create new project"
4. Attendi che il progetto sia pronto (circa 2 minuti)

### 3. Ottenere le credenziali

1. Nel dashboard del progetto, vai su **Settings** (icona ingranaggio)
2. Vai su **API** nella sidebar
3. Troverai:
   - **Project URL**: Copia questo valore (sarà `SUPABASE_URL`)
   - **anon public key**: Copia questo valore (sarà `SUPABASE_KEY`)
   - **service_role key**: Copia questo valore (sarà `SUPABASE_SERVICE_KEY`) - ⚠️ Mantieni segreto!

### 4. Configurare Storage

1. Nel dashboard, vai su **Storage** nella sidebar
2. Clicca su **New bucket**
3. Crea i seguenti bucket:
   - **customer-photos**: Per le foto dei clienti
     - Pubblico: No (privato)
   - **product-images**: Per le immagini dei prodotti
     - Pubblico: Sì
   - **generated-images**: Per le immagini generate dall'AI
     - Pubblico: Sì

### 5. Configurare variabili d'ambiente

1. Copia il file `.env.example` in `.env`:
   ```bash
   cp .env.example .env
   ```

2. Apri `.env` e inserisci le tue credenziali:
   ```env
   SUPABASE_URL=https://tuo-progetto.supabase.co
   SUPABASE_KEY=la_tua_anon_key
   SUPABASE_SERVICE_KEY=la_tua_service_key
   ```

3. ⚠️ **IMPORTANTE**: Non committare mai il file `.env` su Git!

### 6. Verificare la connessione

Dopo aver configurato le variabili d'ambiente, avvia il backend:

```bash
cd backend
python main.py
```

Poi visita `http://localhost:8000/health` per verificare che la connessione funzioni.

## Prossimi passi

Dopo aver configurato Supabase, puoi procedere con:
- Task 2: Creare lo schema del database
- Task 3: Implementare autenticazione

## Risorse utili

- [Documentazione Supabase](https://supabase.com/docs)
- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)

