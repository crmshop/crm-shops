-- Migration 007: Aggiungi scenario_prompts e supporto scenari negli outfit
-- Crea tabella per scenario_prompts (scenari predefiniti con posizione, ambiente, ecc.)

CREATE TABLE IF NOT EXISTS public.scenario_prompts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id UUID REFERENCES public.shops(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL, -- Descrizione posizione, ambiente, illuminazione, ecc.
    position VARCHAR(100), -- Es: "in piedi", "seduto", "camminando"
    environment VARCHAR(100), -- Es: "interno", "esterno", "spiaggia", "città"
    lighting VARCHAR(100), -- Es: "naturale", "artificiale", "serale"
    background TEXT, -- Descrizione sfondo
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_scenario_prompts_shop_id ON public.scenario_prompts(shop_id);
CREATE INDEX IF NOT EXISTS idx_scenario_prompts_name ON public.scenario_prompts(name);

-- Tabella per associare scenari agli outfit con testo libero aggiuntivo
CREATE TABLE IF NOT EXISTS public.outfit_scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    outfit_id UUID REFERENCES public.outfits(id) ON DELETE CASCADE,
    scenario_prompt_id UUID REFERENCES public.scenario_prompts(id) ON DELETE CASCADE,
    custom_text TEXT, -- Testo libero per caratteristiche aggiuntive
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(outfit_id, scenario_prompt_id) -- Un outfit può avere lo stesso scenario solo una volta
);

-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_outfit_scenarios_outfit_id ON public.outfit_scenarios(outfit_id);
CREATE INDEX IF NOT EXISTS idx_outfit_scenarios_scenario_prompt_id ON public.outfit_scenarios(scenario_prompt_id);

-- Aggiungi constraint per limitare a max 3 scenari per outfit
-- Nota: Questo constraint verrà applicato a livello applicativo, non a livello DB
-- perché PostgreSQL non supporta facilmente constraint COUNT

COMMENT ON TABLE public.scenario_prompts IS 'Scenari predefiniti per generazione immagini (posizione, ambiente, illuminazione, ecc.)';
COMMENT ON TABLE public.outfit_scenarios IS 'Associazione scenari agli outfit con testo libero aggiuntivo (max 3 scenari per outfit)';
