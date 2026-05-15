#!/usr/bin/env python3
"""Audit OEM catalog integrity and optionally enforce full strict coverage."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.oem_validation import is_plausible_oem  # noqa: E402


def load_catalog(path: Path) -> dict:
    return json.load(open(path, encoding="utf-8"))


def brand_prefixes(catalog: dict) -> dict[str, str]:
    out = {}
    for brand in catalog.get("brands", []):
        name = str(brand.get("name") or "").strip()
        prefix = str(brand.get("prefix") or name[:2]).strip().upper()
        if name and prefix:
            out[name] = prefix
    return out


def audit_lookup(catalog: dict) -> dict:
    lookup = catalog.get("oem_lookup", {})
    parts = catalog.get("parts_template", [])
    prefixes = brand_prefixes(catalog)
    valid_pairs = {(prefix, str(part.get("code") or "").upper()) for prefix in prefixes.values() for part in parts}

    bad = []
    internal_like = []
    pair_count = 0
    number_count = 0
    reused_by_prefix_number: dict[tuple[str, str], set[str]] = defaultdict(set)

    for prefix, codes in lookup.items():
        if not isinstance(codes, dict):
            continue
        p = str(prefix).upper()
        for code, values in codes.items():
            c = str(code).upper()
            vals = values if isinstance(values, list) else [values]
            if (p, c) in valid_pairs:
                pair_count += 1
            for value in vals:
                number = str(value or "").strip().upper()
                number_count += 1
                reused_by_prefix_number[(p, number)].add(c)
                if "OEM-" in number or "КАНД" in number or "PLACE" in number:
                    internal_like.append({"prefix": p, "part_code": c, "oem_number": number})
                if not is_plausible_oem(p, number, strict_brand=True):
                    bad.append({"prefix": p, "part_code": c, "oem_number": number})

    total_pairs = len(valid_pairs)
    missing = []
    for brand_name, prefix in prefixes.items():
        brand_lookup = lookup.get(prefix, {})
        for part in parts:
            code = str(part.get("code") or "").upper()
            if code not in brand_lookup:
                missing.append({
                    "brand": brand_name,
                    "brand_prefix": prefix,
                    "part_code": code,
                    "part_name": part.get("name", ""),
                    "category": part.get("category", ""),
                    "group": part.get("group", ""),
                })

    reuse_gt4 = [
        {"prefix": p, "oem_number": number, "part_codes": sorted(codes)}
        for (p, number), codes in reused_by_prefix_number.items()
        if len(codes) > 4
    ]

    coverage = round((total_pairs - len(missing)) / total_pairs * 100, 2) if total_pairs else 0.0
    return {
        "total_pairs": total_pairs,
        "covered_pairs": total_pairs - len(missing),
        "missing_pairs": len(missing),
        "coverage_percent": coverage,
        "lookup_pairs": pair_count,
        "oem_numbers": number_count,
        "invalid_oem_numbers": len(bad),
        "internal_like_oem_numbers": len(internal_like),
        "reused_oem_over_4_codes": len(reuse_gt4),
        "bad_samples": bad[:20],
        "internal_samples": internal_like[:20],
        "reuse_samples": reuse_gt4[:20],
        "missing_samples": missing[:50],
        "missing": missing,
    }


def audit_generated_csv(path: Path, prefix_by_brand: dict[str, str]) -> dict:
    if not path.exists():
        return {"exists": False}
    rows = 0
    bad = []
    internal_like = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            rows += 1
            brand = str(row.get("brand") or "")
            prefix = prefix_by_brand.get(brand, brand[:2].upper())
            number = str(row.get("oem_number") or "").strip().upper()
            if "OEM-" in number or "КАНД" in number or "PLACE" in number:
                internal_like.append({"row": rows, "brand": brand, "oem_number": number})
            if not is_plausible_oem(prefix, number, strict_brand=True):
                bad.append({"row": rows, "brand": brand, "prefix": prefix, "oem_number": number})
    return {
        "exists": True,
        "rows": rows,
        "invalid_rows": len(bad),
        "internal_like_rows": len(internal_like),
        "bad_samples": bad[:20],
        "internal_samples": internal_like[:20],
    }


def write_missing_csv(missing: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["brand", "brand_prefix", "part_code", "part_name", "category", "group"]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows({k: row.get(k, "") for k in fieldnames} for row in missing)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit strict OEM catalog integrity")
    parser.add_argument("--catalog", type=Path, default=ROOT / "data" / "parts_catalog.json")
    parser.add_argument("--generated-csv", type=Path, default=ROOT / "generated_parts_catalog.csv")
    parser.add_argument("--json-output", type=Path, default=ROOT / "data" / "oem_integrity_report.json")
    parser.add_argument("--missing-output", type=Path, default=ROOT / "data" / "oem_missing_strict.csv")
    parser.add_argument("--require-full-coverage", action="store_true")
    args = parser.parse_args()

    catalog = load_catalog(args.catalog)
    lookup_report = audit_lookup(catalog)
    generated_report = audit_generated_csv(args.generated_csv, brand_prefixes(catalog))

    report = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "strict_original_only": True,
        "catalog": str(args.catalog.relative_to(ROOT) if args.catalog.is_relative_to(ROOT) else args.catalog),
        "generated_csv": str(args.generated_csv.relative_to(ROOT) if args.generated_csv.is_relative_to(ROOT) else args.generated_csv),
        "lookup": {k: v for k, v in lookup_report.items() if k != "missing"},
        "generated_rows": generated_report,
    }
    args.json_output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_missing_csv(lookup_report["missing"], args.missing_output)

    print(
        f"coverage={lookup_report['coverage_percent']}% "
        f"covered={lookup_report['covered_pairs']}/{lookup_report['total_pairs']} "
        f"missing={lookup_report['missing_pairs']} "
        f"invalid={lookup_report['invalid_oem_numbers']} "
        f"generated_invalid={generated_report.get('invalid_rows', 0)}"
    )
    print(f"report={args.json_output}")
    print(f"missing_csv={args.missing_output}")

    failed = (
        lookup_report["invalid_oem_numbers"] > 0
        or lookup_report["internal_like_oem_numbers"] > 0
        or generated_report.get("invalid_rows", 0) > 0
        or generated_report.get("internal_like_rows", 0) > 0
    )
    if args.require_full_coverage and lookup_report["missing_pairs"] > 0:
        failed = True
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
