# Note di Sicurezza - CRM Shops

## ⚠️ Problemi di Sicurezza Identificati

### 1. Row Level Security (RLS) Non Abilitato

**Problema**: Tutte le tabelle pubbliche non hanno RLS abilitato, il che significa che chiunque con l'anon key può accedere a tutti i dati.

**Tabelle interessate**:
- `users`
- `shops`
- `products`
- `customer_photos`
- `outfits`
- `outfit_products`
- `generated_images`
- `purchases`
- `statistics`
- `prompts`

**Soluzione**: Abilitare RLS e creare policy appropriate per ogni tabella.

**Esempio Policy**:
```sql
-- Abilita RLS
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Policy: Gli utenti possono vedere solo i propri dati
CREATE POLICY "Users can view own data" ON public.users
    FOR SELECT USING (auth.uid() = id);

-- Policy: Gli utenti possono aggiornare solo i propri dati
CREATE POLICY "Users can update own data" ON public.users
    FOR UPDATE USING (auth.uid() = id);
```

### 2. Funzione con Search Path Mutabile

**Problema**: La funzione `update_updated_at_column()` ha un search_path mutabile, che può essere un rischio di sicurezza.

**Soluzione**: Impostare il search_path esplicitamente nella funzione.

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER 
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;
```

## 🔒 Raccomandazioni per Produzione

1. **Abilitare RLS** su tutte le tabelle prima del deploy in produzione
2. **Creare policy specifiche** per ogni tipo di operazione (SELECT, INSERT, UPDATE, DELETE)
3. **Usare Service Role Key** solo nel backend, mai nel frontend
4. **Limitare accessi** basati sui ruoli utente (cliente vs negoziante)
5. **Implementare audit logging** per operazioni sensibili
6. **Configurare Storage buckets** con policy di accesso appropriate

## 📝 Prossimi Passi

1. Creare migrazione per abilitare RLS
2. Definire policy per ogni tabella
3. Testare le policy con utenti di test
4. Documentare le policy nel README

## 🔗 Risorse

- [Supabase RLS Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [Database Linter](https://supabase.com/docs/guides/database/database-linter)

