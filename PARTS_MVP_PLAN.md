# Parts Catalog MVP Plan for cmsauto.store

## Goal
Build a practical parts catalog that starts small, sells fast, and scales into full OEM/aftermarket coverage.

## MVP Chain (UI + data)
Brand -> Model -> Generation -> Year -> Engine -> Category -> Subcategory -> Part -> OEM number -> Analogs -> Photos -> Applicability -> Price / Preorder -> VIN request button.

## Data source strategy
Phase 1 (fast launch):
- Parts-Catalogs API for OEM hierarchy and part numbers.
- Apify or RapidAPI TecDoc alternative for affordable aftermarket analog tests.

Phase 2 (stability):
- Keep both sources, add quality scoring on analogs.
- Start supplier and pricing sync by schedule.

Phase 3 (production depth):
- Add official TecDoc feed in parallel (do not hard switch on day one).
- Use TecDoc as primary for analogs and fitment, keep other sources as fallback.

## Why this avoids failure
- Do not ingest the full universe at start (too large and expensive).
- Restrict to top brands and high-turnover categories.
- Build normalized tables once; expand only data volume later.

## MVP scope
Top brands:
- Toyota
- Lexus
- BMW
- Mercedes
- Audi
- Volkswagen
- Opel
- Kia
- Hyundai
- Ford
- Chevrolet
- Buick

High-turnover categories first:
- Filters
- Brakes
- Suspension
- Engine service
- Electrical service parts

## Database
Implemented in [database/parts_mvp_schema.sql](database/parts_mvp_schema.sql):
- vehicles hierarchy: vehicle_brands, vehicle_models, vehicle_generations, vehicles
- engines
- categories: part_categories
- parts
- oe_numbers
- cross_references
- applicability: part_applicability
- photos: part_images
- suppliers
- prices
- vin_part_requests
- storefront view: parts_catalog_public

## Suggested API contract for frontend
Endpoint example:
- GET /parts/search?brand=Toyota&model=Camry&year=2021&engine=2AR-FE&category=Brakes

Response essentials:
- part_name
- oem_number
- analogs[]
- photos[]
- applicability
- price_offer {price, currency, order_type, stock_qty, lead_time_days}

## Integration steps in this repo
1. Apply SQL from [database/parts_mvp_schema.sql](database/parts_mvp_schema.sql) in Supabase SQL Editor.
2. Add ETL importer for source payloads into normalized tables.
3. Keep existing [parts-orders.html](parts-orders.html) as UI shell and move data reads to parts_catalog_public.
4. Add VIN button flow writing into vin_part_requests and leads.
5. Roll out by brand batches, not all brands at once.

## Rollout sequence
Week 1:
- Toyota, Lexus, Kia, Hyundai.
- Filters + Brakes only.

Week 2:
- BMW, Mercedes, Audi, Volkswagen.
- Suspension + engine service.

Week 3:
- Opel, Ford, Chevrolet, Buick.
- Expand analogs and supplier pricing coverage.

## KPI to validate MVP
- VIN requests per day.
- Share of parts with at least one valid analog.
- Quote response time.
- Conversion from part page to lead.
- Margin by supplier.
