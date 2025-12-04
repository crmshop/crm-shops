# Credenziali Supabase - CRM Shops

## Progetto: Shop

**⚠️ IMPORTANTE**: Questo file contiene informazioni sensibili. Non committarlo su Git!

## Credenziali Progetto

- **Project ID**: `mfcjnzeflvgyjvxprfzz`
- **Project Ref**: `mfcjnzeflvgyjvxprfzz`
- **Region**: `eu-west-1` (Europa Ovest)
- **Status**: `ACTIVE_HEALTHY`
- **Database Version**: PostgreSQL 17.6.1.054

## URL e Chiavi API

### URL Progetto
```
https://mfcjnzeflvgyjvxprfzz.supabase.co
```

### Anon Key (Public)
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1mY2puemVmbHZneWp2eHByZnp6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ3NzgwODYsImV4cCI6MjA4MDM1NDA4Nn0.Oaxw-8VW5N3Q61Bq1ZrL3bNUPVbyc9kmr307MiWLD2Y
```

### Service Role Key
**⚠️ Ottieni questa chiave dal Dashboard Supabase**:
1. Vai su https://app.supabase.com
2. Seleziona il progetto "Shop"
3. Vai su Settings → API
4. Copia la "service_role" key (è segreta, non condividerla!)

## Configurazione .env

Aggiungi queste variabili al tuo file `.env`:

```env
SUPABASE_URL="https://mfcjnzeflvgyjvxprfzz.supabase.co"
SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1mY2puemVmbHZneWp2eHByZnp6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ3NzgwODYsImV4cCI6MjA4MDM1NDA4Nn0.Oaxw-8VW5N3Q61Bq1ZrL3bNUPVbyc9kmr307MiWLD2Y"
SUPABASE_SERVICE_KEY="[OTTENI DAL DASHBOARD]"
```

## Database

- **Host**: `db.mfcjnzeflvgyjvxprfzz.supabase.co`
- **Port**: `5432` (default PostgreSQL)
- **Database**: `postgres`

## Tabelle Create

✅ Tutte le tabelle sono state create con successo:
- `users` - Utenti estesi
- `shops` - Negozi
- `products` - Prodotti/capi
- `customer_photos` - Foto clienti
- `outfits` - Outfit
- `outfit_products` - Relazione outfit-prodotti
- `generated_images` - Immagini generate AI
- `purchases` - Acquisti
- `statistics` - Statistiche
- `prompts` - Prompt predefiniti

## Prossimi Passi

1. ✅ Migrazione applicata
2. ⏳ Configurare Storage buckets per immagini
3. ⏳ Configurare Row Level Security (RLS) se necessario
4. ⏳ Testare connessione dal backend

## Dashboard

Accedi al dashboard: https://app.supabase.com/project/mfcjnzeflvgyjvxprfzz






