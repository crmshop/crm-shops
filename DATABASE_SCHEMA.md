# Schema Database CRM Shops

Questo documento descrive lo schema del database PostgreSQL per il progetto CRM Shops.

## Tabelle Principali

### 1. `users`
Estende le informazioni utente di Supabase Auth.

**Colonne:**
- `id` (UUID, PK) - Riferimento a `auth.users.id`
- `email` (VARCHAR) - Email utente (unique)
- `role` (VARCHAR) - Ruolo: 'cliente' o 'negoziante'
- `full_name` (VARCHAR) - Nome completo
- `phone` (VARCHAR) - Telefono
- `created_at`, `updated_at` (TIMESTAMP)

### 2. `shops`
Gestisce i negozi del sistema.

**Colonne:**
- `id` (UUID, PK)
- `owner_id` (UUID, FK → users.id)
- `name` (VARCHAR) - Nome negozio
- `description` (TEXT)
- `address`, `phone`, `email`, `website`
- `created_at`, `updated_at`

### 3. `products`
Catalogo prodotti/capi dei negozi.

**Colonne:**
- `id` (UUID, PK)
- `shop_id` (UUID, FK → shops.id)
- `name`, `description`
- `category` - 'vestiti', 'scarpe', 'accessori'
- `season` - 'primavera', 'estate', 'autunno', 'inverno', 'tutto'
- `occasion` - 'casual', 'formale', 'sport', 'festa', 'lavoro', 'altro'
- `style`, `price`, `image_url`
- `available` (BOOLEAN)
- `created_at`, `updated_at`

### 4. `customer_photos`
Foto dei clienti caricate per la simulazione.

**Colonne:**
- `id` (UUID, PK)
- `user_id` (UUID, FK → users.id)
- `shop_id` (UUID, FK → shops.id, nullable)
- `image_url` (TEXT) - URL su Supabase Storage
- `angle` - 'frontale', 'laterale', 'posteriore'
- `consent_given` (BOOLEAN)
- `uploaded_at`

### 5. `outfits`
Outfit creati combinando prodotti.

**Colonne:**
- `id` (UUID, PK)
- `user_id` (UUID, FK → users.id)
- `shop_id` (UUID, FK → shops.id)
- `name` (VARCHAR)
- `created_at`

### 6. `outfit_products`
Relazione many-to-many tra outfit e prodotti.

**Colonne:**
- `outfit_id` (UUID, FK → outfits.id, PK)
- `product_id` (UUID, FK → products.id, PK)

### 7. `generated_images`
Immagini generate dall'AI.

**Colonne:**
- `id` (UUID, PK)
- `customer_photo_id` (UUID, FK → customer_photos.id)
- `product_id` (UUID, FK → products.id)
- `outfit_id` (UUID, FK → outfits.id)
- `image_url` (TEXT)
- `prompt_used` (TEXT)
- `scenario` (VARCHAR)
- `ai_service` (VARCHAR) - 'banana_pro', 'gemini'
- `generated_at`

### 8. `purchases`
Acquisti effettuati.

**Colonne:**
- `id` (UUID, PK)
- `user_id` (UUID, FK → users.id)
- `shop_id` (UUID, FK → shops.id)
- `product_id` (UUID, FK → products.id, nullable)
- `outfit_id` (UUID, FK → outfits.id, nullable)
- `purchase_date`
- `amount` (DECIMAL)
- `status` - 'pending', 'completed', 'cancelled'

### 9. `statistics`
Statistiche per i negozi.

**Colonne:**
- `id` (UUID, PK)
- `shop_id` (UUID, FK → shops.id)
- `metric_name` (VARCHAR)
- `metric_value` (DECIMAL)
- `date` (DATE)
- `metadata` (JSONB)
- `created_at`

### 10. `prompts`
Prompt predefiniti per la generazione AI.

**Colonne:**
- `id` (UUID, PK)
- `shop_id` (UUID, FK → shops.id, nullable)
- `category` (VARCHAR)
- `base_prompt` (TEXT)
- `variables` (JSONB)
- `is_default` (BOOLEAN)
- `created_at`, `updated_at`

## Indici

Sono stati creati indici per ottimizzare le query più comuni:
- `idx_users_role` - Ricerca per ruolo
- `idx_shops_owner` - Negozi per proprietario
- `idx_products_shop` - Prodotti per negozio
- `idx_products_category` - Prodotti per categoria
- `idx_customer_photos_user` - Foto per utente
- `idx_outfits_user` - Outfit per utente
- `idx_generated_images_product` - Immagini per prodotto
- `idx_purchases_user` - Acquisti per utente
- `idx_purchases_date` - Acquisti per data
- `idx_statistics_shop_date` - Statistiche per negozio e data

## Trigger

Funzione `update_updated_at_column()` aggiorna automaticamente il campo `updated_at` quando una riga viene modificata.

## Applicazione Migrazioni

Vedi `backend/migrations/README.md` per istruzioni su come applicare le migrazioni.

