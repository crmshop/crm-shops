-- Migrazione: Rendere user_id nullable in customer_photos
-- I clienti del negozio (shop_customers) non hanno user_id, quindi user_id deve essere nullable
-- Almeno uno tra user_id e customer_id deve essere presente (vincolo applicato a livello applicativo)

-- Rendere user_id nullable
ALTER TABLE public.customer_photos 
ALTER COLUMN user_id DROP NOT NULL;

-- Commento per chiarezza
COMMENT ON COLUMN public.customer_photos.user_id IS 'ID utente cliente esterno (se caricata dal cliente stesso), altrimenti NULL se è customer_id (cliente negozio)';

