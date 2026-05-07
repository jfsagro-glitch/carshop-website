#!/usr/bin/env python3
"""Report real OEM coverage by brand prefix and part code."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from generate_parts_catalog import get_merged_oem_lookup  # noqa: E402


def main() -> None:
    cat = json.load(open(ROOT / "data" / "parts_catalog.json", encoding="utf-8"))
    parts = cat.get("parts_template", [])
    codes = [p["code"] for p in parts]
    lookup = get_merged_oem_lookup()

    rows = []
    for brand in cat.get("brands", []):
        prefix = brand.get("prefix", brand["name"][:2].upper())
        covered = sum(1 for code in codes if (prefix, code) in lookup)
        rows.append((covered / len(codes), covered, len(codes), brand["name"], prefix))

    rows.sort()
    print("OEM coverage by brand:")
    for ratio, covered, total, brand, prefix in rows:
        print(f"{brand:16} {prefix:>2} {covered:3}/{total:<3} {ratio*100:5.1f}%")

    uncovered_codes = []
    for code in codes:
        covered_brands = sum(1 for brand in cat.get("brands", []) if (brand.get("prefix"), code) in lookup)
        if covered_brands == 0:
            part = next(p for p in parts if p["code"] == code)
            uncovered_codes.append((part["category"], part["name"], code))

    print("\nFully uncovered part codes:")
    if uncovered_codes:
        for category, name, code in uncovered_codes:
            print(f"{code:5} {category:18} {name}")
    else:
        print("none")

    total_pairs = len(codes) * len(cat.get("brands", []))
    covered_pairs = sum(1 for brand in cat.get("brands", []) for code in codes if (brand.get("prefix"), code) in lookup)
    print(f"\nTotal pair coverage: {covered_pairs}/{total_pairs} ({covered_pairs / total_pairs * 100:.1f}%)")
    print(f"OEM lookup pairs: {sum(len(v) for v in lookup.values())}")


if __name__ == "__main__":
    main()
