-- ============================================================
-- EXPO MIR / cmsauto.store
-- MVP schema for normalized parts catalog
-- ============================================================

-- 1) Vehicles hierarchy
CREATE TABLE IF NOT EXISTS vehicle_brands (
  id           bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  name         text NOT NULL UNIQUE,
  slug         text NOT NULL UNIQUE,
  is_active    boolean NOT NULL DEFAULT true,
  created_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS vehicle_models (
  id           bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  brand_id     bigint NOT NULL REFERENCES vehicle_brands(id) ON DELETE CASCADE,
  name         text NOT NULL,
  slug         text NOT NULL,
  is_active    boolean NOT NULL DEFAULT true,
  created_at   timestamptz NOT NULL DEFAULT now(),
  UNIQUE (brand_id, slug)
);

CREATE TABLE IF NOT EXISTS vehicle_generations (
  id           bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  model_id     bigint NOT NULL REFERENCES vehicle_models(id) ON DELETE CASCADE,
  code         text,
  name         text NOT NULL,
  year_from    int,
  year_to      int,
  is_active    boolean NOT NULL DEFAULT true,
  created_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS vehicles (
  id                bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  brand_id          bigint NOT NULL REFERENCES vehicle_brands(id) ON DELETE RESTRICT,
  model_id          bigint NOT NULL REFERENCES vehicle_models(id) ON DELETE RESTRICT,
  generation_id     bigint REFERENCES vehicle_generations(id) ON DELETE SET NULL,
  market_region     text,
  year_from         int,
  year_to           int,
  body_type         text,
  notes             text,
  is_active         boolean NOT NULL DEFAULT true,
  created_at        timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_vehicle_models_brand ON vehicle_models(brand_id);
CREATE INDEX IF NOT EXISTS idx_vehicle_generations_model ON vehicle_generations(model_id);
CREATE INDEX IF NOT EXISTS idx_vehicles_brand_model ON vehicles(brand_id, model_id);
CREATE INDEX IF NOT EXISTS idx_vehicles_generation ON vehicles(generation_id);

-- 2) Engines
CREATE TABLE IF NOT EXISTS engines (
  id                 bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  vehicle_id         bigint NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
  engine_code        text,
  displacement_cc    int,
  displacement_l     numeric,
  fuel_type          text,
  power_hp           int,
  power_kw           int,
  aspiration         text,
  drivetrain         text,
  transmission       text,
  is_active          boolean NOT NULL DEFAULT true,
  created_at         timestamptz NOT NULL DEFAULT now(),
  UNIQUE (vehicle_id, engine_code)
);

CREATE INDEX IF NOT EXISTS idx_engines_vehicle ON engines(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_engines_power ON engines(power_hp, power_kw);

-- 3) Category tree
CREATE TABLE IF NOT EXISTS part_categories (
  id                 bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  parent_id          bigint REFERENCES part_categories(id) ON DELETE CASCADE,
  name               text NOT NULL,
  slug               text NOT NULL,
  level              smallint NOT NULL DEFAULT 1,
  sort_order         int NOT NULL DEFAULT 0,
  is_active          boolean NOT NULL DEFAULT true,
  created_at         timestamptz NOT NULL DEFAULT now(),
  UNIQUE (parent_id, slug)
);

CREATE INDEX IF NOT EXISTS idx_part_categories_parent ON part_categories(parent_id);
CREATE INDEX IF NOT EXISTS idx_part_categories_level ON part_categories(level);

-- 4) Parts core
CREATE TABLE IF NOT EXISTS parts (
  id                 bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  category_id        bigint REFERENCES part_categories(id) ON DELETE SET NULL,
  part_name          text NOT NULL,
  manufacturer       text,
  description        text,
  is_oem             boolean NOT NULL DEFAULT false,
  status             text NOT NULL DEFAULT 'active', -- active | hidden | archived
  created_at         timestamptz NOT NULL DEFAULT now(),
  updated_at         timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_parts_category ON parts(category_id);
CREATE INDEX IF NOT EXISTS idx_parts_status ON parts(status);

-- 5) OEM numbers (one part can have multiple OEMs)
CREATE TABLE IF NOT EXISTS oe_numbers (
  id                 bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  part_id            bigint NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
  oem_number         text NOT NULL,
  brand_id           bigint REFERENCES vehicle_brands(id) ON DELETE SET NULL,
  source_system      text, -- parts-catalogs, tecdoc, internal
  is_primary         boolean NOT NULL DEFAULT false,
  created_at         timestamptz NOT NULL DEFAULT now(),
  UNIQUE (oem_number, COALESCE(brand_id, 0))
);

CREATE INDEX IF NOT EXISTS idx_oe_part ON oe_numbers(part_id);
CREATE INDEX IF NOT EXISTS idx_oe_number ON oe_numbers(oem_number);

-- 6) Aftermarket analogs / cross references
CREATE TABLE IF NOT EXISTS cross_references (
  id                     bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  oe_number_id           bigint NOT NULL REFERENCES oe_numbers(id) ON DELETE CASCADE,
  analog_brand           text NOT NULL,
  analog_number          text NOT NULL,
  quality_tier           text, -- budget | standard | premium
  source_system          text,
  created_at             timestamptz NOT NULL DEFAULT now(),
  UNIQUE (oe_number_id, analog_brand, analog_number)
);

CREATE INDEX IF NOT EXISTS idx_cross_oe ON cross_references(oe_number_id);
CREATE INDEX IF NOT EXISTS idx_cross_number ON cross_references(analog_number);

-- 7) Applicability (vehicle/engine fitment)
CREATE TABLE IF NOT EXISTS part_applicability (
  id                     bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  part_id                bigint NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
  vehicle_id             bigint REFERENCES vehicles(id) ON DELETE CASCADE,
  engine_id              bigint REFERENCES engines(id) ON DELETE CASCADE,
  year_from              int,
  year_to                int,
  fitment_note           text,
  source_system          text,
  created_at             timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_fitment_part ON part_applicability(part_id);
CREATE INDEX IF NOT EXISTS idx_fitment_vehicle ON part_applicability(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_fitment_engine ON part_applicability(engine_id);

-- 8) Media
CREATE TABLE IF NOT EXISTS part_images (
  id                     bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  part_id                bigint NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
  image_url              text NOT NULL,
  sort_order             int NOT NULL DEFAULT 0,
  is_primary             boolean NOT NULL DEFAULT false,
  created_at             timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_part_images_part ON part_images(part_id);

-- 9) Suppliers and prices/stock
CREATE TABLE IF NOT EXISTS suppliers (
  id                     bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  supplier_name          text NOT NULL UNIQUE,
  country                text,
  contact_payload        jsonb NOT NULL DEFAULT '{}'::jsonb,
  is_active              boolean NOT NULL DEFAULT true,
  created_at             timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS prices (
  id                     bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  part_id                bigint NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
  supplier_id            bigint REFERENCES suppliers(id) ON DELETE SET NULL,
  currency               text NOT NULL DEFAULT 'USD',
  price_value            numeric,
  lead_time_days         int,
  stock_qty              int,
  order_type             text NOT NULL DEFAULT 'in_stock', -- in_stock | preorder
  updated_at             timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_prices_part ON prices(part_id);
CREATE INDEX IF NOT EXISTS idx_prices_supplier ON prices(supplier_id);
CREATE INDEX IF NOT EXISTS idx_prices_order_type ON prices(order_type);

-- 10) VIN requests to back "Запросить подбор по VIN"
CREATE TABLE IF NOT EXISTS vin_part_requests (
  id                     bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  vin                    text NOT NULL,
  customer_name          text,
  customer_phone         text,
  customer_email         text,
  comment                text,
  status                 text NOT NULL DEFAULT 'new', -- new | in_progress | answered | closed
  created_at             timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_vin_requests_status ON vin_part_requests(status);
CREATE INDEX IF NOT EXISTS idx_vin_requests_created ON vin_part_requests(created_at DESC);

-- 11) Public view for storefront API
CREATE OR REPLACE VIEW parts_catalog_public AS
SELECT
  p.id,
  b.name                          AS brand,
  m.name                          AS model,
  g.name                          AS generation,
  pa.year_from,
  pa.year_to,
  e.engine_code,
  e.displacement_l,
  e.fuel_type,
  c1.name                         AS category,
  c2.name                         AS subcategory,
  p.part_name,
  o.oem_number,
  jsonb_agg(DISTINCT jsonb_build_object('brand', cr.analog_brand, 'number', cr.analog_number))
    FILTER (WHERE cr.id IS NOT NULL) AS analogs,
  jsonb_agg(DISTINCT img.image_url)
    FILTER (WHERE img.id IS NOT NULL) AS photos,
  jsonb_build_object(
    'price', pr.price_value,
    'currency', pr.currency,
    'order_type', pr.order_type,
    'stock_qty', pr.stock_qty,
    'lead_time_days', pr.lead_time_days
  ) AS price_offer
FROM parts p
LEFT JOIN oe_numbers o ON o.part_id = p.id AND o.is_primary = true
LEFT JOIN cross_references cr ON cr.oe_number_id = o.id
LEFT JOIN part_applicability pa ON pa.part_id = p.id
LEFT JOIN vehicles v ON v.id = pa.vehicle_id
LEFT JOIN vehicle_brands b ON b.id = v.brand_id
LEFT JOIN vehicle_models m ON m.id = v.model_id
LEFT JOIN vehicle_generations g ON g.id = v.generation_id
LEFT JOIN engines e ON e.id = pa.engine_id
LEFT JOIN part_categories c2 ON c2.id = p.category_id
LEFT JOIN part_categories c1 ON c1.id = c2.parent_id
LEFT JOIN part_images img ON img.part_id = p.id
LEFT JOIN prices pr ON pr.part_id = p.id
WHERE p.status = 'active'
GROUP BY p.id, b.name, m.name, g.name, pa.year_from, pa.year_to,
         e.engine_code, e.displacement_l, e.fuel_type,
         c1.name, c2.name, p.part_name, o.oem_number,
         pr.price_value, pr.currency, pr.order_type, pr.stock_qty, pr.lead_time_days;

-- 12) Update trigger for parts.updated_at
CREATE OR REPLACE FUNCTION update_parts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_parts_updated_at ON parts;
CREATE TRIGGER trg_parts_updated_at
BEFORE UPDATE ON parts
FOR EACH ROW EXECUTE FUNCTION update_parts_updated_at();

-- 13) Seed top brands for MVP scope
INSERT INTO vehicle_brands (name, slug)
VALUES
('Toyota', 'toyota'),
('Lexus', 'lexus'),
('BMW', 'bmw'),
('Mercedes', 'mercedes'),
('Audi', 'audi'),
('Volkswagen', 'volkswagen'),
('Opel', 'opel'),
('Kia', 'kia'),
('Hyundai', 'hyundai'),
('Ford', 'ford'),
('Chevrolet', 'chevrolet'),
('Buick', 'buick')
ON CONFLICT (name) DO NOTHING;
