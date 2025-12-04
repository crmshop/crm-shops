# Test Storage Supabase

Questa guida ti aiuta a verificare che lo Storage Supabase sia configurato correttamente.

## Test Automatico

Esegui lo script di test:

```bash
python scripts/test_storage.py
```

Lo script verificherà:
- ✅ Connessione ai bucket
- ✅ Accessibilità dei bucket
- ✅ Permessi base

## Test Manuale

### 1. Verifica Bucket dal Dashboard

1. Vai su Supabase Dashboard → Storage
2. Verifica che questi bucket esistano:
   - `customer-photos` (pubblico)
   - `product-images` (pubblico)
   - `generated-images` (pubblico)

### 2. Test Upload da API

Usa curl o Postman per testare l'upload:

```bash
# Prima fai login per ottenere il token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'

# Poi usa il token per upload
curl -X POST http://localhost:8000/api/customer-photos/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test_image.jpg" \
  -F "shop_id=YOUR_SHOP_ID" \
  -F "angle=front" \
  -F "consent_given=true"
```

### 3. Verifica URL Pubblico

Dopo l'upload, verifica che l'immagine sia accessibile pubblicamente:

```bash
# L'URL dovrebbe essere nel formato:
https://[PROJECT_REF].supabase.co/storage/v1/object/public/customer-photos/[file-path]

# Testa l'URL nel browser o con curl:
curl -I https://[PROJECT_REF].supabase.co/storage/v1/object/public/customer-photos/[file-path]
```

## Troubleshooting

### Errore "Bucket not found"
- Verifica che il bucket sia stato creato dal Dashboard
- Controlla il nome del bucket (deve essere esatto)
- Assicurati di usare le credenziali corrette

### Errore "Permission denied"
- Verifica che il bucket sia pubblico (per download)
- Controlla le policy di Storage
- Verifica che l'utente sia autenticato (per upload)

### Immagini non visibili
- Verifica che il bucket sia pubblico
- Controlla l'URL dell'immagine
- Verifica CORS se necessario

### Upload fallisce
- Verifica autenticazione (token JWT valido)
- Controlla formato file (solo immagini)
- Verifica dimensione file (limiti Supabase)

## Policy Consigliate

Per sicurezza, configura queste policy:

### customer-photos (Pubblico)
- **SELECT**: Pubblico (chiunque può vedere)
- **INSERT**: Solo utenti autenticati
- **UPDATE**: Solo proprietario
- **DELETE**: Solo proprietario

### product-images (Pubblico)
- **SELECT**: Pubblico
- **INSERT**: Solo negozianti
- **UPDATE**: Solo proprietario negozio
- **DELETE**: Solo proprietario negozio

### generated-images (Pubblico)
- **SELECT**: Pubblico
- **INSERT**: Solo utenti autenticati
- **UPDATE**: Solo proprietario
- **DELETE**: Solo proprietario

## Verifica Post-Deploy

Dopo il deploy su Render:

1. Testa upload da frontend deployato
2. Verifica che le immagini siano accessibili pubblicamente
3. Controlla log per errori Storage
4. Monitora uso storage (quota Supabase)

## Risorse

- [Documentazione Storage Supabase](https://supabase.com/docs/guides/storage)
- [Policy Storage](https://supabase.com/docs/guides/storage/security/access-control)
- [Upload Files](https://supabase.com/docs/guides/storage/uploads)


