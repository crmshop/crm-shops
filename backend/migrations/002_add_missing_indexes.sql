-- Migrazione 002: Aggiungi indici mancanti per performance
-- Risolve i warning di performance advisor

-- Indici per foreign keys mancanti
CREATE INDEX IF NOT EXISTS idx_customer_photos_shop ON public.customer_photos(shop_id);
CREATE INDEX IF NOT EXISTS idx_generated_images_customer_photo ON public.generated_images(customer_photo_id);
CREATE INDEX IF NOT EXISTS idx_generated_images_outfit ON public.generated_images(outfit_id);
CREATE INDEX IF NOT EXISTS idx_outfit_products_product ON public.outfit_products(product_id);
CREATE INDEX IF NOT EXISTS idx_outfits_shop ON public.outfits(shop_id);
CREATE INDEX IF NOT EXISTS idx_prompts_shop ON public.prompts(shop_id);
CREATE INDEX IF NOT EXISTS idx_purchases_shop ON public.purchases(shop_id);
CREATE INDEX IF NOT EXISTS idx_purchases_product ON public.purchases(product_id);
CREATE INDEX IF NOT EXISTS idx_purchases_outfit ON public.purchases(outfit_id);



