-- Migrazione: Tabella clienti negozio
-- I clienti creati dal negoziante NON hanno account Supabase Auth
-- Rimangono solo nell'area del negozio senza email di conferma

-- Tabella clienti negozio (separata da users per clienti esterni)
CREATE TABLE IF NOT EXISTS public.shop_customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id UUID NOT NULL REFERENCES public.shops(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    phone VARCHAR(20),
    address TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    -- Evita duplicati email nello stesso negozio
    UNIQUE(shop_id, email)
);

-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_shop_customers_shop_id ON public.shop_customers(shop_id);
CREATE INDEX IF NOT EXISTS idx_shop_customers_email ON public.shop_customers(email);

-- Trigger per updated_at automatico
CREATE OR REPLACE FUNCTION update_shop_customers_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_shop_customers_updated_at
    BEFORE UPDATE ON public.shop_customers
    FOR EACH ROW
    EXECUTE FUNCTION update_shop_customers_updated_at();

-- Modifica tabella customer_photos per supportare sia user_id (clienti esterni)
-- che customer_id (clienti negozio)
ALTER TABLE public.customer_photos 
ADD COLUMN IF NOT EXISTS customer_id UUID REFERENCES public.shop_customers(id) ON DELETE CASCADE;

-- Commenti per chiarezza
COMMENT ON TABLE public.shop_customers IS 'Clienti interni del negozio - creati dal negoziante, senza account Auth, senza email';
COMMENT ON COLUMN public.customer_photos.customer_id IS 'ID cliente negozio (se caricata dal negoziante), altrimenti NULL se è user_id (cliente esterno)';

