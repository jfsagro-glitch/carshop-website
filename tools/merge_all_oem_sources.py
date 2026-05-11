#!/usr/bin/env python3
"""Merge all OEM supplier CSVs into one master file."""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def merge_oem_sources(source_dir: Path, output_path: Path) -> dict:
    """Merge all oem_supplier_*.csv files and deduplicate."""
    
    csv_files = sorted(source_dir.glob("oem_supplier_*.csv"))
    print(f"Found {len(csv_files)} OEM source files:")
    for f in csv_files:
        print(f"  - {f.name}")
    
    # Dedup by brand_prefix + part_code + oem_number
    seen = set()
    all_rows = []
    col_names = None
    
    for csv_file in csv_files:
        with csv_file.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if col_names is None:
                col_names = reader.fieldnames
            
            for row in reader:
                prefix = str(row.get("brand_prefix") or "").strip().upper()
                code = str(row.get("part_code") or "").strip().upper()
                oem = str(row.get("oem_number") or "").strip()
                
                key = (prefix, code, oem)
                if key not in seen:
                    seen.add(key)
                    all_rows.append(row)
    
    # Write merged file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=col_names)
        writer.writeheader()
        writer.writerows(all_rows)
    
    # Count by brand
    brands_count = defaultdict(int)
    for row in all_rows:
        prefix = str(row.get("brand_prefix") or "").strip().upper()
        if prefix:
            brands_count[prefix] += 1
    
    print(f"\nMerged {len(all_rows)} unique records:")
    for brand in sorted(brands_count.keys()):
        print(f"  {brand}: {brands_count[brand]}")
    
    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_files": [f.name for f in csv_files],
        "total_records": len(all_rows),
        "unique_records": len(all_rows),
        "brands": len(brands_count),
        "brand_counts": dict(brands_count),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge all OEM supplier CSVs")
    parser.add_argument("--source-dir", default="data", help="Directory containing OEM CSVs")
    parser.add_argument("--output", default="data/oem_supplier_merged_all.csv", help="Output path")
    args = parser.parse_args()
    
    source_dir = Path(args.source_dir)
    output_path = Path(args.output)
    
    stats = merge_oem_sources(source_dir, output_path)
    print(f"\nWrote: {output_path}")
    print(f"Total records: {stats['total_records']}")
    print(f"Brands: {stats['brands']}")


if __name__ == "__main__":
    main()
