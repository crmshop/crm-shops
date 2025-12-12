-- Migration 006: Aggiorna categorie prodotti
-- Aggiorna il CHECK constraint per le categorie prodotti con le nuove categorie

-- STEP 1: Rimuovi temporaneamente il vecchio constraint per permettere gli aggiornamenti
ALTER TABLE products DROP CONSTRAINT IF EXISTS products_category_check;

-- STEP 2: Aggiorna i prodotti esistenti con le vecchie categorie alle nuove
-- Mappa le vecchie categorie alle nuove:
-- 'vestiti' -> 'maglieria' (categoria generica più appropriata)
-- 'giacca' -> 'giacche' (singolare a plurale)
-- 'scarpe' -> 'scarpe' (già presente, nessun cambiamento)
-- 'accessori' -> 'accessori' (già presente, nessun cambiamento)

UPDATE products 
SET category = 'maglieria' 
WHERE category = 'vestiti';

UPDATE products 
SET category = 'giacche' 
WHERE category = 'giacca';

-- Aggiorna eventuali altre categorie non valide a 'maglieria' come fallback
UPDATE products 
SET category = 'maglieria' 
WHERE category IS NOT NULL 
AND category NOT IN (
    'giacche', 
    'blazer', 
    'maglieria', 
    'felpe&ibridi', 
    'camicie', 
    'shirty', 
    'pantaloni', 
    'calzini', 
    'short', 
    'scarpe', 
    'copricapi', 
    'accessori'
);

-- STEP 3: Aggiungi il nuovo constraint con le nuove categorie
ALTER TABLE products ADD CONSTRAINT products_category_check 
    CHECK (category IN (
        'giacche', 
        'blazer', 
        'maglieria', 
        'felpe&ibridi', 
        'camicie', 
        'shirty', 
        'pantaloni', 
        'calzini', 
        'short', 
        'scarpe', 
        'copricapi', 
        'accessori'
    ));

-- Nota: I prodotti con categorie non valide sono stati automaticamente aggiornati:
-- - 'vestiti' -> 'maglieria'
-- - 'giacca' -> 'giacche'
-- - Altre categorie non valide -> 'maglieria' (fallback)
-- Se necessario, puoi aggiornare manualmente i prodotti per assegnare categorie più specifiche
