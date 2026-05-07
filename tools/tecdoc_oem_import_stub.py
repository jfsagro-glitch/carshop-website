#!/usr/bin/env python3
"""
TecDoc/TecAlliance-style OEM import adapter.

This file is intentionally a connector skeleton: full OEM data requires a
licensed provider token and provider-specific endpoints. The script reads a
normalized export from a provider response and writes rows compatible with
tools/import_oem_lookup.py.

Expected normalized JSON input:
[
  {
    "brand": "Toyota",
    "part_code": "OF",
    "oem_numbers": ["04152-YZZA6", "90915-YZZD4"],
    "source": "TecDoc export 2026-05-07"
  }
]
"""
import argparse
import csv
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert licensed OEM export to importer CSV")
    parser.add_argument("--input", required=True, help="Normalized provider JSON export")
    parser.add_argument("--output", default="supplier_oem_import.csv", help="CSV for tools/import_oem_lookup.py")
    args = parser.parse_args()

    raw = json.load(open(args.input, encoding="utf-8"))
    if not isinstance(raw, list):
        raise SystemExit("Input must be a JSON array")

    out = Path(args.output)
    with open(out, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["brand", "prefix", "part_code", "oem_number", "source"])
        writer.writeheader()
        count = 0
        for row in raw:
            numbers = row.get("oem_numbers") or row.get("oem_number") or []
            if isinstance(numbers, str):
                numbers = [numbers]
            for number in numbers:
                writer.writerow({
                    "brand": row.get("brand", ""),
                    "prefix": row.get("prefix", ""),
                    "part_code": row.get("part_code") or row.get("code", ""),
                    "oem_number": number,
                    "source": row.get("source", ""),
                })
                count += 1

    print(f"wrote {count} OEM rows to {out}")
    print(f"next: python tools\\import_oem_lookup.py --input {out} --source \"licensed provider export\"")


if __name__ == "__main__":
    main()
