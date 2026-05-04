-- ============================================================
-- EXPO MIR — Supabase Database Schema
-- Выполнить в: Supabase Dashboard → SQL Editor
-- ============================================================

-- ── Таблица автомобилей (Georgia + Europe + Korea + USA) ──────────────────
CREATE TABLE IF NOT EXISTS cars (
  id            bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  external_id   text   UNIQUE NOT NULL,   -- URL объявления (уникальный ключ для upsert)
  source        text   NOT NULL,          -- 'myauto_ge', 'autoscout24', 'mobilede'
  region        text   NOT NULL,          -- 'georgia', 'europe', 'korea', 'usa', 'china'
  brand         text,
  model         text,
  year          int,
  price         numeric,
  price_eur     numeric,
  currency      text   DEFAULT 'USD',
  mileage       int,
  engine        numeric,                  -- объём в л (1.8, 2.0, ...)
  fuel_type     text,
  transmission  text,
  power_kw      int,
  power_hp      int,
  color         text,
  drive         text,
  vin           text,
  url           text,
  images        jsonb  DEFAULT '[]'::jsonb,
  specs         jsonb  DEFAULT '{}'::jsonb, -- доп. поля (first_registration, equipment, ...)
  is_active     boolean DEFAULT true,
  first_seen    timestamptz DEFAULT now(),
  last_seen     timestamptz DEFAULT now(),
  updated_at    timestamptz DEFAULT now()
);

-- Индексы для быстрых фильтров каталога
CREATE INDEX IF NOT EXISTS idx_cars_region       ON cars(region)       WHERE is_active;
CREATE INDEX IF NOT EXISTS idx_cars_brand        ON cars(brand)        WHERE is_active;
CREATE INDEX IF NOT EXISTS idx_cars_year         ON cars(year)         WHERE is_active;
CREATE INDEX IF NOT EXISTS idx_cars_price        ON cars(price)        WHERE is_active;
CREATE INDEX IF NOT EXISTS idx_cars_source       ON cars(source);
CREATE INDEX IF NOT EXISTS idx_cars_region_brand ON cars(region, brand) WHERE is_active;

-- Full-text search по марке и модели
ALTER TABLE cars ADD COLUMN IF NOT EXISTS fts tsvector
  GENERATED ALWAYS AS (to_tsvector('russian', coalesce(brand,'') || ' ' || coalesce(model,''))) STORED;
CREATE INDEX IF NOT EXISTS idx_cars_fts ON cars USING gin(fts);

-- Триггер: автоматически обновляет updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS cars_updated_at ON cars;
CREATE TRIGGER cars_updated_at
  BEFORE UPDATE ON cars
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ── Таблица запчастей ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS parts (
  id            bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  oem_number    text,
  name          text NOT NULL,
  name_ru       text,
  category      text,   -- 'engine', 'suspension', 'brakes', 'body', 'electrical', 'other'
  brand         text,   -- Toyota, BMW, Mercedes-Benz, ...
  models        text[], -- ARRAY['Camry', 'RAV4']
  years_from    int,
  years_to      int,
  price_usd     numeric,
  price_kgs     numeric,
  stock_qty     int     DEFAULT 0,
  images        jsonb   DEFAULT '[]'::jsonb,
  description   text,
  source_url    text,
  is_available  boolean DEFAULT true,
  created_at    timestamptz DEFAULT now(),
  updated_at    timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_parts_brand    ON parts(brand)    WHERE is_available;
CREATE INDEX IF NOT EXISTS idx_parts_category ON parts(category) WHERE is_available;
CREATE INDEX IF NOT EXISTS idx_parts_oem      ON parts(oem_number);
CREATE INDEX IF NOT EXISTS idx_parts_models   ON parts USING gin(models);

DROP TRIGGER IF EXISTS parts_updated_at ON parts;
CREATE TRIGGER parts_updated_at
  BEFORE UPDATE ON parts
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ── Таблица заявок (CRM) ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS leads (
  id            bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  type          text   NOT NULL DEFAULT 'car_order',
                -- 'car_order' | 'parts_request' | 'vin_search' | 'callback' | 'price_check'
  status        text   NOT NULL DEFAULT 'new',
                -- 'new' | 'contacted' | 'deal' | 'closed' | 'cancelled'
  name          text,
  phone         text,
  email         text,
  message       text,
  car_id        bigint REFERENCES cars(id) ON DELETE SET NULL,
  car_info      jsonb,    -- snapshot авто на момент заявки
  source_page   text,     -- 'georgia-stock', 'europe-orders', 'parts', ...
  utm_source    text,
  utm_medium    text,
  utm_campaign  text,
  created_at    timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_leads_status     ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_type       ON leads(type);
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at DESC);

-- ── Таблица событий поиска (аналитика) ───────────────────────────────────
CREATE TABLE IF NOT EXISTS search_events (
  id            bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  page          text,
  filters       jsonb,
  results_cnt   int,
  session_id    text,
  created_at    timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_search_page ON search_events(page);
CREATE INDEX IF NOT EXISTS idx_search_created ON search_events(created_at DESC);

-- ── Row Level Security ────────────────────────────────────────────────────
ALTER TABLE cars          ENABLE ROW LEVEL SECURITY;
ALTER TABLE parts         ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads         ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_events ENABLE ROW LEVEL SECURITY;

-- Публичное чтение активных авто
DROP POLICY IF EXISTS "public_read_active_cars" ON cars;
CREATE POLICY "public_read_active_cars"
  ON cars FOR SELECT
  USING (is_active = true);

-- Публичное чтение доступных запчастей
DROP POLICY IF EXISTS "public_read_available_parts" ON parts;
CREATE POLICY "public_read_available_parts"
  ON parts FOR SELECT
  USING (is_available = true);

-- Публичная вставка заявок (но не чтение!)
DROP POLICY IF EXISTS "public_insert_leads" ON leads;
CREATE POLICY "public_insert_leads"
  ON leads FOR INSERT
  WITH CHECK (true);

-- Публичная вставка поисковых событий
DROP POLICY IF EXISTS "public_insert_search_events" ON search_events;
CREATE POLICY "public_insert_search_events"
  ON search_events FOR INSERT
  WITH CHECK (true);

-- ── Realtime для уведомлений менеджеру ───────────────────────────────────
-- Включить в Supabase Dashboard → Database → Replication → leads
-- ALTER PUBLICATION supabase_realtime ADD TABLE leads;

-- ── Комментарии ───────────────────────────────────────────────────────────
COMMENT ON TABLE cars  IS 'Каталог автомобилей (авто-синк через GitHub Actions)';
COMMENT ON TABLE parts IS 'Каталог запчастей';
COMMENT ON TABLE leads IS 'CRM: заявки от покупателей';
COMMENT ON TABLE search_events IS 'Аналитика поисковых запросов';
