#!/usr/bin/env python3
"""Merge all OEM supplier CSVs into one master file."""
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.oem_validation import is_plausible_oem as is_plausible_oem_for_brand
from tools.oem_validation import split_oem_candidates


BASE_FIELDNAMES = [
    "brand",
    "brand_prefix",
    "part_code",
    "part_name",
    "priority",
    "oem_number",
    "source_name",
    "source_url",
    "retrieved_at",
]


def is_plausible_oem_number(value: str, prefix: str = "") -> bool:
    """Reject common HTML/JS tokens accidentally captured as part numbers."""
    if prefix:
        return is_plausible_oem_for_brand(prefix, value, strict_brand=True)
    token = str(value or "").strip().upper()
    if not token:
        return False
    if token.startswith("0X"):
        return False
    if len(token) < 6:
        return False
    if token in {"CONTENT", "SCRIPT", "WINDOW", "SEARCH", "VALUE", "FALSE", "TRUE"}:
        return False
    if token.startswith(("WP-", "JS-")):
        return False
    if token.startswith("G-") and len(token) > 8:
        return False
    return True


def merged_fieldnames(rows: list[dict]) -> list[str]:
    seen = set()
    fieldnames: list[str] = []
    for name in BASE_FIELDNAMES:
        if any(name in row for row in rows):
            seen.add(name)
            fieldnames.append(name)
    for row in rows:
        for name in row:
            if name not in seen:
                seen.add(name)
                fieldnames.append(name)
    return fieldnames


def merge_oem_sources(source_dir: Path, output_path: Path) -> dict:
    """Merge all oem_supplier_*.csv files and deduplicate."""
    
    csv_files = [
        p for p in sorted(source_dir.glob("oem_supplier_*.csv"))
        if p.resolve() != output_path.resolve()
    ]
    print(f"Found {len(csv_files)} OEM source files:")
    for f in csv_files:
        print(f"  - {f.name}")
    
    # Dedup by brand_prefix + part_code + oem_number
    seen = set()
    all_rows = []
    for csv_file in csv_files:
        with csv_file.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)

            for row in reader:
                prefix = str(row.get("brand_prefix") or "").strip().upper()
                code = str(row.get("part_code") or "").strip().upper()
                oem = str(row.get("oem_number") or "").strip()
                if not (prefix and code and oem):
                    continue
                for candidate in split_oem_candidates(oem):
                    if not is_plausible_oem_number(candidate, prefix):
                        continue

                    key = (prefix, code, candidate)
                    if key not in seen:
                        seen.add(key)
                        out = dict(row)
                        out["brand_prefix"] = prefix
                        out["part_code"] = code
                        out["oem_number"] = candidate
                        all_rows.append(out)
    
    # Write merged file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=merged_fieldnames(all_rows), extrasaction="ignore")
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
