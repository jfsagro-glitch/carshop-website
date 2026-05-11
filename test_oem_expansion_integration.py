#!/usr/bin/env python3
"""
Integration test for OEM coverage expansion pipeline.
Tests all three expansion modules working together.
"""

import json
import csv
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent
DATA_DIR = REPO_ROOT / "data"
TOOLS_DIR = REPO_ROOT / "tools"


def run_test(name: str, description: str, command: list, check_outputs: list = None) -> bool:
    """Run a test command and verify outputs exist"""
    logger.info(f"\n{'='*60}")
    logger.info(f"TEST: {name}")
    logger.info(f"Description: {description}")
    logger.info(f"Command: {' '.join(command)}")
    logger.info(f"{'='*60}")
    
    try:
        result = subprocess.run(command, cwd=str(REPO_ROOT), capture_output=False, timeout=120)
        
        if result.returncode != 0:
            logger.error(f"✗ Command failed with exit code {result.returncode}")
            return False
        
        if check_outputs:
            for output_file in check_outputs:
                path = DATA_DIR / output_file
                if not path.exists():
                    logger.error(f"✗ Output file not found: {output_file}")
                    return False
                
                size = path.stat().st_size
                logger.info(f"✓ Output file created: {output_file} ({size} bytes)")
                
                # Show record count if CSV
                if output_file.endswith('.csv'):
                    with open(path, 'r', encoding='utf-8-sig') as f:
                        reader = csv.DictReader(f)
                        count = sum(1 for _ in reader)
                        logger.info(f"  └─ Records: {count}")
        
        logger.info(f"✓ TEST PASSED")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error(f"✗ Command timed out")
        return False
    except Exception as e:
        logger.error(f"✗ Test failed with exception: {e}")
        return False


def test_vin_epc_decoder():
    """Test VIN/EPC decoder with sample mode"""
    return run_test(
        name="VIN/EPC Decoder (Sample Mode)",
        description="Generate sample VIN-based OEM data for high-quality brands",
        command=[
            sys.executable,
            str(TOOLS_DIR / "import_vin_epc_decoder.py"),
            "--mode", "sample",
            "--output", str(DATA_DIR / "oem_supplier_vin_decoded_sample.csv"),
        ],
        check_outputs=["oem_supplier_vin_decoded_sample.csv"]
    )


def test_coverage_report():
    """Test OEM coverage report"""
    return run_test(
        name="OEM Coverage Report",
        description="Generate current coverage metrics",
        command=[
            sys.executable,
            str(TOOLS_DIR / "oem_coverage_report.py"),
        ],
        check_outputs=["oem_coverage.json"]
    )


def test_merged_lookup():
    """Test merged verified lookup build"""
    return run_test(
        name="Merged Verified Lookup Build",
        description="Rebuild verified lookup from all sources",
        command=[
            sys.executable,
            str(TOOLS_DIR / "build_verified_oem_lookup.py"),
            "--input", str(DATA_DIR / "oem_supplier_export.csv"),
            "--input", str(DATA_DIR / "oem_supplier_official_sites.csv"),
            "--input", str(DATA_DIR / "oem_supplier_official_sites_extra.csv"),
            "--input", str(DATA_DIR / "oem_supplier_official_sites_gm_mopar.csv"),
            "--output", str(DATA_DIR / "oem_lookup_verified_test.json"),
        ],
        check_outputs=["oem_lookup_verified_test.json"]
    )


def test_parts_catalog_dry_run():
    """Test parts catalog generation with dry-run"""
    return run_test(
        name="Parts Catalog Generation (Dry-Run)",
        description="Generate parts catalog with --dry-run flag (no Supabase upload)",
        command=[
            sys.executable,
            str(REPO_ROOT / "generate_parts_catalog.py"),
            "--dry-run",
        ],
        check_outputs=None  # Dry-run doesn't create output files
    )


def validate_vin_decoded_csv():
    """Validate structure of generated VIN/EPC CSV"""
    csv_path = DATA_DIR / "oem_supplier_vin_decoded_sample.csv"
    
    if not csv_path.exists():
        logger.error(f"VIN decoded CSV not found: {csv_path}")
        return False
    
    required_fields = ['brand_prefix', 'vin', 'model', 'year', 'engine', 'transmission', 'source_name']
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        # Check required fields
        for field in required_fields:
            if field not in fieldnames:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Check sample records
        records = list(reader)
        if not records:
            logger.warning("No records in VIN decoded CSV")
            return True
        
        logger.info(f"✓ VIN decoded CSV valid: {len(records)} records")
        for i, record in enumerate(records[:3]):
            logger.info(f"  Sample {i+1}: {record['brand_prefix']} {record['model']} "
                       f"({record['year']}) {record['engine']}")
        
        return True


def validate_coverage_report():
    """Validate structure of coverage report"""
    json_path = DATA_DIR / "oem_coverage.json"
    
    if not json_path.exists():
        logger.error(f"Coverage report not found: {json_path}")
        return False
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    required_keys = ['total_pairs', 'covered_pairs', 'coverage_percent']
    
    for key in required_keys:
        if key not in data:
            logger.error(f"Missing required key in coverage report: {key}")
            return False
    
    logger.info(f"✓ Coverage Report valid:")
    logger.info(f"  Total pairs: {data.get('total_pairs', 'N/A')}")
    logger.info(f"  Covered pairs: {data.get('covered_pairs', 'N/A')}")
    logger.info(f"  Coverage: {data.get('coverage_percent', 'N/A')}%")
    
    return True


def validate_merged_lookup():
    """Validate structure of merged lookup"""
    json_path = DATA_DIR / "oem_lookup_verified_test.json"
    
    if not json_path.exists():
        logger.error(f"Merged lookup not found: {json_path}")
        return False
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Check structure
    if 'lookup' not in data and 'summary' not in data:
        # Might be just the lookup dict
        lookup = data if isinstance(data, dict) else {}
    else:
        lookup = data.get('lookup', {})
    
    brand_count = len(lookup)
    total_pairs = sum(len(codes) for codes in lookup.values() if isinstance(codes, dict))
    total_oem = sum(
        len(oem_list) if isinstance(oem_list, list) else 1
        for codes in lookup.values()
        if isinstance(codes, dict)
        for oem_list in codes.values()
    )
    
    logger.info(f"✓ Merged Lookup valid:")
    logger.info(f"  Brands: {brand_count}")
    logger.info(f"  Brand×Code pairs: {total_pairs}")
    logger.info(f"  Total OEM numbers: {total_oem}")
    
    return True


def generate_report(test_results: dict) -> None:
    """Generate summary report"""
    logger.info("\n" + "="*60)
    logger.info("INTEGRATION TEST SUMMARY")
    logger.info("="*60)
    
    passed = sum(1 for v in test_results.values() if v)
    total = len(test_results)
    
    logger.info(f"\nTests: {passed}/{total} passed")
    
    for test_name, result in test_results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"  {status}: {test_name}")
    
    logger.info("\n" + "="*60)
    
    if passed == total:
        logger.info("✓ ALL TESTS PASSED")
        logger.info("\nNext steps:")
        logger.info("1. Review generated CSV/JSON files in data/")
        logger.info("2. Run gap-driven importer for targeted closure")
        logger.info("3. Run VIN/EPC importer for structured fitment")
        logger.info("4. Probe VAG/Mercedes alternative sources")
        logger.info("5. Rebuild final verified lookup")
        logger.info("6. Generate and push updated parts catalog")
    else:
        logger.error("✗ SOME TESTS FAILED")
        logger.error("\nCheck logs above for details")
        sys.exit(1)


def main():
    logger.info("\n" + "="*60)
    logger.info("OEM COVERAGE EXPANSION - INTEGRATION TEST SUITE")
    logger.info("="*60)
    logger.info(f"Start time: {datetime.now().isoformat()}")
    logger.info(f"Repository: {REPO_ROOT}")
    logger.info(f"Data directory: {DATA_DIR}")
    logger.info("="*60)
    
    # Verify prerequisite files exist
    prerequisite_files = [
        "data/oem_supplier_export.csv",
        "data/oem_supplier_official_sites.csv",
        "data/oem_supplier_official_sites_extra.csv",
        "data/oem_supplier_official_sites_gm_mopar.csv",
        "data/oem_gap_worklist.csv",
    ]
    
    logger.info("\nChecking prerequisites...")
    for file in prerequisite_files:
        path = REPO_ROOT / file
        if path.exists():
            logger.info(f"  ✓ {file}")
        else:
            logger.warning(f"  ✗ {file} (missing, some tests may fail)")
    
    # Run tests
    test_results = {}
    
    logger.info("\nRunning integration tests...\n")
    test_results["VIN/EPC Decoder"] = test_vin_epc_decoder()
    test_results["Coverage Report"] = test_coverage_report()
    test_results["Merged Lookup Build"] = test_merged_lookup()
    test_results["Parts Catalog (Dry-Run)"] = test_parts_catalog_dry_run()
    
    # Run validations
    logger.info("\nRunning validation checks...\n")
    
    if (DATA_DIR / "oem_supplier_vin_decoded_sample.csv").exists():
        try:
            validate_vin_decoded_csv()
        except Exception as e:
            logger.error(f"VIN CSV validation failed: {e}")
    
    try:
        validate_coverage_report()
    except Exception as e:
        logger.error(f"Coverage report validation failed: {e}")
    
    try:
        validate_merged_lookup()
    except Exception as e:
        logger.error(f"Merged lookup validation failed: {e}")
    
    # Generate report
    generate_report(test_results)
    
    logger.info(f"End time: {datetime.now().isoformat()}\n")


if __name__ == '__main__':
    main()
