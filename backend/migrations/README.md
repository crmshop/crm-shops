# Migrazioni Database

Questa cartella contiene le migrazioni SQL per il database PostgreSQL (Supabase).

## Struttura

- `001_initial_schema.sql` - Schema iniziale con tutte le tabelle

## Come applicare le migrazioni

### Opzione 1: Tramite Supabase Dashboard

1. Vai su [Supabase Dashboard](https://app.supabase.com)
2. Seleziona il tuo progetto
3. Vai su **SQL Editor**
4. Copia e incolla il contenuto di `001_initial_schema.sql`
5. Esegui la query

### Opzione 2: Tramite Supabase CLI

```bash
# Installa Supabase CLI se non l'hai già
npm install -g supabase

# Login
supabase login

# Link al progetto
supabase link --project-ref your-project-ref

# Applica migrazione
supabase db push
```

### Opzione 3: Tramite Python script

```bash
python backend/migrations/apply_migrations.py
```

## Ordine di applicazione

Le migrazioni devono essere applicate in ordine numerico:
1. `001_initial_schema.sql` - Prima migrazione, crea tutte le tabelle base

## Rollback

Per fare rollback di una migrazione, usa il file corrispondente nella cartella `rollback/`.

## Note

- ⚠️ Le migrazioni sono idempotenti (usano `IF NOT EXISTS`)
- ✅ Puoi eseguirle multiple volte senza problemi
- 🔒 Assicurati di avere i permessi corretti sul database



