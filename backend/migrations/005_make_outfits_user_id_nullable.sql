-- Migrazione: Rendere user_id nullable in outfits
-- Gli outfit possono essere creati per clienti shop_customers che non hanno user_id
-- Almeno uno tra user_id e customer_id deve essere presente (vincolo applicato a livello applicativo)

-- Rendere user_id nullable
ALTER TABLE public.outfits 
ALTER COLUMN user_id DROP NOT NULL;

-- Commento per chiarezza
COMMENT ON COLUMN public.outfits.user_id IS 'ID utente cliente esterno (se outfit creato dal cliente stesso), altrimenti NULL se è per customer_id (cliente negozio)';

