# OEM Coverage Expansion Plan: Implementation Guide

**Current State**: 77.5% coverage (7,484 covered pairs / 9,660 total)  
**Target State**: 85-90%+ coverage with structured fitment data by model/year/engine/transmission

---

## Three-Pronged Coverage Expansion Strategy

### 1. TARGETED GAP-DRIVEN IMPORT  
**Tool**: `tools/import_from_oem_gaps.py`

**Purpose**: Close specific unresolved brand×code pairs identified in `data/oem_gap_worklist.csv`

**Current Gap Inventory**:
- **2,266** unresolved brand×code pairs
- **1,437** marked high-priority (CKP, OPS, ODW, EMG, IMG, HGG, CVB, SBF, SBR, RAB, etc.)
- **829** marked low-priority

**How It Works**:
1. Reads `oem_gap_worklist.csv` which contains:
   - brand, brand_prefix, part_code, part_name, category, group, priority
   - **suggested_sources** = pre-mapped domain URLs (manual_check, partner_api_or_export modes)

2. For each gap, searches suggested sources in priority order:
   - acurapartswarehouse.com, hondaworld.ru (Honda/Acura)
   - trshop.audi.de, partsale.eu, elcats.ru (VAG)
   - emex.ru, exist.ru (Russian catalogs)

3. Extracts OEM from search results and exports to CSV with provenance

**Usage**:
```bash
# Quick test on 20 high-priority gaps
python tools/import_from_oem_gaps.py --max-gaps 20 \
  --output data/oem_supplier_targeted_gaps_test.csv

# Full gap closure run (all 2,266 gaps, ~2-3 hours)
python tools/import_from_oem_gaps.py \
  --output data/oem_supplier_targeted_gaps.csv \
  --failed-output data/oem_gap_failed_searches.csv
```

**Expected Results**:
- 400-700 new OEM numbers from gaps
- Coverage improvement: 77.5% → 80-82%
- Prioritized by maintenance-critical part codes

**Integration with Pipeline**:
After running:
```bash
python tools/build_verified_oem_lookup.py \
  --input data/oem_supplier_export.csv \
  --input data/oem_supplier_official_sites.csv \
  --input data/oem_supplier_official_sites_extra.csv \
  --input data/oem_supplier_official_sites_gm_mopar.csv \
  --input data/oem_supplier_targeted_gaps.csv \
  --output data/oem_lookup_verified_with_gaps.json
```

---

### 2. VIN/EPC STRUCTURED FITMENT IMPORT
**Tool**: `tools/import_vin_epc_decoder.py`

**Purpose**: Extract structured fitment (model/year/engine/transmission) for high-quality brands

**Supported Brands** (highest fitment quality):
- BMW (BM) - realoem.com compatible
- Lexus (LX) - Lexus Parts catalogs
- Hyundai (HY) - OEM catalog
- Kia (KI) - OEM catalog
- Nissan (NI) - OEM catalog
- Ford (FO) - Ford Parts catalogs
- Toyota (TY) - Toyota Parts catalogs

**How It Works**:

**Phase 1: Sample Generation** (for testing)
- Generates 10 sample VINs per brand
- Decodes VIN structure: WMI → brand, position 10 → year, position 8 → engine
- Builds model-year-engine mappings from internal database
- Exports structured fitment without actual OEM lookups

**Phase 2: Live EPC Query** (requires API access)
- Queries official brand EPC databases
- Extracts model-year-engine-transmission combinations
- Maps to existing OEM lookup
- Enriches records with structured fitment

**Usage**:

```bash
# Generate sample VIN data for testing
python tools/import_vin_epc_decoder.py --mode sample \
  --output data/oem_supplier_vin_decoded_sample.csv

# Query live EPC databases (requires API setup)
python tools/import_vin_epc_decoder.py --mode live \
  --brands BM,LX,HY,KI,NI,FO \
  --output data/oem_supplier_vin_decoded_live.csv
```

**Expected Results**:
- 1,000-2,000 new fitment-rich records per brand
- Complete model-year-engine-transmission coverage
- Coverage improvement: 82% → 88-92%

**Integration with Pipeline**:
```bash
# Merge VIN/EPC results into verified lookup
python tools/build_verified_oem_lookup.py \
  --input data/oem_supplier_export.csv \
  --input data/oem_supplier_official_sites.csv \
  --input data/oem_supplier_official_sites_gm_mopar.csv \
  --input data/oem_supplier_targeted_gaps.csv \
  --input data/oem_supplier_vin_decoded_live.csv \
  --output data/oem_lookup_verified_complete.json
```

**EPC Database References**:
- **BMW**: realoem.com (VIN search → parts catalog)
- **Lexus**: lexuspartsnow.com (model-year search)
- **Hyundai**: hyundaipartsdeal.com (fitment tables)
- **Kia**: kiapartsnow.com (fitment tables)
- **Nissan**: nissanpartsdeal.com (fitment tables)
- **Ford**: fordpartsgiant.com (fitment tables)
- **Toyota**: toyotapartsdeal.com (fitment tables)

---

### 3. VAG/MERCEDES ALTERNATIVE SOURCE DISCOVERY
**Tool**: `tools/probe_vag_mercedes_sources.py`

**Purpose**: Find accessible OEM sources for VAG (VW/Audi/Skoda/Seat) and Mercedes

**Known Blockers**:
- audipartsdeal.com: SSL certificate error
- vwpartsdeal.com: SSL certificate error  
- volkswagenpartsdeal.com: SSL certificate error
- parts.mercedes-benz.de: Geolocking/access restrictions

**Alternative Approaches**:

**Option A: Direct Sitemap Discovery**
Test alternative domain patterns:
- parts.volkswagen.de (vs vwpartsdeal.com)
- partsinfo.audi.de (vs audipartsdeal.com)
- parts.skoda.de / parts.seat.de
- parts.mercedes-benz.com (vs de domain)

**Option B: Partner APIs**
- elcats.ru API - VAG parts with OEM
- exist.ru API - Russian OEM lookup  
- rockauto.com API - broad cross-brand OEM

**Option C: SSL Bypass for Discovery**
```bash
# Probe with SSL verification disabled (discovery only)
python tools/probe_vag_mercedes_sources.py --skip-ssl \
  --output data/vag_mercedes_probe_results_no_ssl.json
```

**Usage**:

```bash
# Probe all official sources (with SSL verification)
python tools/probe_vag_mercedes_sources.py \
  --output data/vag_mercedes_probe_results.json

# Check if alternative domains are accessible
python -c "
import requests
domains = [
  'https://parts.volkswagen.de',
  'https://partsinfo.audi.de', 
  'https://parts.skoda.de',
  'https://parts.mercedes-benz.com'
]
for url in domains:
    try:
        r = requests.get(url, timeout=10)
        print(f'{url}: {r.status_code}')
    except Exception as e:
        print(f'{url}: Error - {e}')
"
```

**Expected Results**:
- VAG coverage: 20-30% → 35-50% (if sources found)
- Mercedes coverage: 5-10% → 15-25% (if sources found)
- Overall improvement: 77.5% → 80%+ (even without VAG/Mercedes)

---

## Recommended Execution Sequence

### Week 1: Targeted Gap Closure
```bash
# Step 1: Run gap-driven importer
python tools/import_from_oem_gaps.py \
  --output data/oem_supplier_targeted_gaps.csv \
  --failed-output data/oem_gap_failed_searches.csv

# Step 2: Merge results into verified lookup
python tools/build_verified_oem_lookup.py \
  --input data/oem_supplier_export.csv \
  --input data/oem_supplier_official_sites.csv \
  --input data/oem_supplier_official_sites_extra.csv \
  --input data/oem_supplier_official_sites_gm_mopar.csv \
  --input data/oem_supplier_targeted_gaps.csv \
  --output data/oem_lookup_verified_with_gaps.json

# Step 3: Measure coverage improvement
python tools/oem_coverage_report.py --lookup data/oem_lookup_verified_with_gaps.json

# Step 4: Regenerate parts catalog with new coverage
python generate_parts_catalog.py --dry-run

# Step 5: Commit progress
git add -A
git commit -m "feat: targeted gap-driven OEM import - coverage 77.5% → XX%"
git push
```

### Week 2: VIN/EPC Structured Fitment
```bash
# Step 1: Test with sample data
python tools/import_vin_epc_decoder.py --mode sample \
  --output data/oem_supplier_vin_decoded_sample.csv

# Step 2: Setup live EPC database connectors
# (requires manual setup for each brand's API)

# Step 3: Run live queries for high-priority brands
python tools/import_vin_epc_decoder.py --mode live \
  --brands BM,LX,HY,KI,NI,FO \
  --output data/oem_supplier_vin_decoded_live.csv

# Step 4: Merge into verified lookup
python tools/build_verified_oem_lookup.py \
  --input data/oem_supplier_export.csv \
  --input data/oem_supplier_official_sites.csv \
  --input data/oem_supplier_official_sites_gm_mopar.csv \
  --input data/oem_supplier_targeted_gaps.csv \
  --input data/oem_supplier_vin_decoded_live.csv \
  --output data/oem_lookup_verified_complete.json

# Step 5: Measure final coverage
python tools/oem_coverage_report.py --lookup data/oem_lookup_verified_complete.json

# Step 6: Final commit
git add -A
git commit -m "feat: VIN/EPC structured fitment import - coverage 77.5% → XX%"
git push
```

### Week 3: VAG/Mercedes Resolution
```bash
# Step 1: Probe alternative sources
python tools/probe_vag_mercedes_sources.py \
  --output data/vag_mercedes_probe_results.json

# Step 2: If accessible sources found, add to sitemap importer
# and run targeted import for VAG/Mercedes

# Step 3: If VAG still blocked, use partner APIs
# (elcats.ru, exist.ru for Russian market coverage)

# Step 4: Final verified lookup rebuild
python tools/build_verified_oem_lookup.py \
  --input data/oem_supplier_export.csv \
  --input data/oem_supplier_official_sites.csv \
  --input data/oem_supplier_official_sites_gm_mopar.csv \
  --input data/oem_supplier_targeted_gaps.csv \
  --input data/oem_supplier_vin_decoded_live.csv \
  --input data/oem_supplier_vag_mercedes.csv \
  --output data/oem_lookup_verified_final.json

# Step 5: Commit final state
git add -A
git commit -m "feat: VAG/Mercedes alternative sources - coverage 77.5% → XX%"
git push
```

---

## Quality Metrics & Validation

### Coverage Calculation
```bash
python tools/oem_coverage_report.py --lookup data/oem_lookup_verified.json
```

**Output Format**:
```
OEM Coverage Report
===================
Total catalog pairs: 9,660
Covered pairs: 7,484
Coverage %: 77.5%

By Brand:
  Honda (HO): 98.2% (245/250)
  Lexus (LX): 85.3% (128/150)
  Audi (AU): 62.1% (93/150)
  VAG (VW): 35.8% (50/140)
```

### Fitment Quality Metrics
```bash
# Check how many records have structured fitment
python -c "
import csv
from pathlib import Path

files = ['oem_supplier_vin_decoded_live.csv']
for f in files:
    p = Path(f'data/{f}')
    if p.exists():
        rows = list(csv.DictReader(p.open('r', encoding='utf-8-sig')))
        with_year = sum(1 for r in rows if r.get('year_from') or r.get('year_to'))
        with_engine = sum(1 for r in rows if r.get('engine'))
        with_trans = sum(1 for r in rows if r.get('transmission'))
        print(f'{f}:')
        print(f'  Total: {len(rows)}')
        print(f'  With year: {with_year} ({100*with_year/len(rows):.1f}%)')
        print(f'  With engine: {with_engine} ({100*with_engine/len(rows):.1f}%)')
        print(f'  With transmission: {with_trans} ({100*with_trans/len(rows):.1f}%)')
"
```

---

## Implementation Notes

### Gap-Driven Importer
- Uses suggested_sources from worklist (pre-mapped in export_oem_gap_worklist.py)
- Searches domain-by-domain, stops at first successful hit
- Supports multiple search types: manual_check, partner_api_or_export
- Rate-limited to 1 request/second per domain
- Exports failed searches for manual follow-up

### VIN/EPC Decoder
- Supports industry-standard VIN position mappings
- Model database includes generations with year ranges and engine variants
- Can generate test data without live API access
- Designed to integrate multiple EPC sources
- Outputs complete fitment tuple (model, year_from, year_to, engine, transmission)

### VAG/Mercedes Probe
- Tests alternative domain patterns for each brand
- Checks both sitemaps and API endpoints
- Supports SSL bypass for discovery phase (testing only)
- Generates detailed JSON report with accessibility status
- Identifies which sources are accessible vs blocked

---

## Success Criteria

✓ **Phase 1 Complete**: Gap-driven import closes 400-700 pairs → 80-82% coverage  
✓ **Phase 2 Complete**: VIN/EPC adds 1,000-2,000 fitment-rich records → 88-92% coverage  
✓ **Phase 3 Complete**: VAG/Mercedes identified/integrated → 92%+ coverage  

**Final Target**: All brand×code×model×year×engine combinations verified by real external source  
**Quality Gate**: 100% of records contain provenance (source_url, source_name, retrieved_at)

---

## Data Files Reference

| File | Records | Purpose |
|------|---------|---------|
| `oem_gap_worklist.csv` | 2,266 | Unresolved gaps with suggested sources |
| `oem_supplier_export.csv` | 19,798 | Public catalog verification results |
| `oem_supplier_official_sites.csv` | 982 | Sitemap wave 1 (Acura, Honda, etc.) |
| `oem_supplier_official_sites_extra.csv` | 238 | Sitemap wave 2 (BMW, Subaru) |
| `oem_supplier_official_sites_gm_mopar.csv` | 761 | Sitemap wave 3 (GM, Mopar) |
| `oem_supplier_targeted_gaps.csv` | TBD | Gap-driven import results |
| `oem_supplier_vin_decoded_live.csv` | TBD | VIN/EPC structured fitment |
| `oem_supplier_vag_mercedes.csv` | TBD | VAG/Mercedes alternative sources |
| `oem_lookup_verified.json` | 7,708 pairs | Current merged lookup (77.5%) |
| `oem_coverage.json` | 1 record | Coverage metrics |

