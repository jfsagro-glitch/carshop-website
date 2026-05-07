#!/usr/bin/env python3
"""Report real OEM coverage by brand prefix and part code."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from generate_parts_catalog import get_merged_oem_lookup  # noqa: E402


def build_report() -> dict:
    cat = json.load(open(ROOT / "data" / "parts_catalog.json", encoding="utf-8"))
    parts = cat.get("parts_template", [])
    codes = [p["code"] for p in parts]
    lookup = get_merged_oem_lookup()

    brand_rows = []
    for brand in cat.get("brands", []):
        prefix = brand.get("prefix", brand["name"][:2].upper())
        covered = sum(1 for code in codes if (prefix, code) in lookup)
        brand_rows.append({
            "brand": brand["name"],
            "prefix": prefix,
            "covered": covered,
            "total": len(codes),
            "coverage": round(covered / len(codes) * 100, 1),
        })

    fully_uncovered = []
    for code in codes:
        covered_brands = sum(1 for brand in cat.get("brands", []) if (brand.get("prefix"), code) in lookup)
        if covered_brands == 0:
            part = next(p for p in parts if p["code"] == code)
            fully_uncovered.append({"code": code, "category": part["category"], "name": part["name"]})

    total_pairs = len(codes) * len(cat.get("brands", []))
    covered_pairs = sum(1 for brand in cat.get("brands", []) for code in codes if (brand.get("prefix"), code) in lookup)

    priority_groups = {"ТО", "Тормоза", "Подвеска", "Двигатель", "Охлаждение", "Трансмиссия"}
    gaps = []
    for part in parts:
        code = part["code"]
        missing = [brand["name"] for brand in cat.get("brands", []) if (brand.get("prefix"), code) not in lookup]
        if missing and (part.get("category") in priority_groups or part.get("group") in priority_groups):
            gaps.append({
                "missing_count": len(missing),
                "category": part["category"],
                "group": part["group"],
                "name": part["name"],
                "code": code,
                "examples": missing[:8],
            })

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "brands": len(cat.get("brands", [])),
        "part_codes": len(codes),
        "total_pairs": total_pairs,
        "covered_pairs": covered_pairs,
        "coverage": round(covered_pairs / total_pairs * 100, 1) if total_pairs else 0,
        "oem_lookup_pairs": sum(len(v) for v in lookup.values()),
        "brand_coverage": sorted(brand_rows, key=lambda row: (row["coverage"], row["brand"])),
        "fully_uncovered": fully_uncovered,
        "priority_gaps": sorted(gaps, key=lambda row: row["missing_count"], reverse=True)[:60],
    }


def print_report(report: dict) -> None:
    print("OEM coverage by brand:")
    for row in report["brand_coverage"]:
        print(f"{row['brand']:16} {row['prefix']:>2} {row['covered']:3}/{row['total']:<3} {row['coverage']:5.1f}%")

    print("\nFully uncovered part codes:")
    if report["fully_uncovered"]:
        for row in report["fully_uncovered"]:
            print(f"{row['code']:5} {row['category']:18} {row['name']}")
    else:
        print("none")

    print(f"\nTotal pair coverage: {report['covered_pairs']}/{report['total_pairs']} ({report['coverage']:.1f}%)")
    print(f"OEM lookup pairs: {report['oem_lookup_pairs']}")

    print("\nPriority OEM gaps for supplier/API import:")
    for row in report["priority_gaps"][:40]:
        print(
            f"{row['code']:5} missing {row['missing_count']:2} brands | "
            f"{row['category']}/{row['group']} | {row['name']} | e.g. {', '.join(row['examples'])}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Report real OEM coverage")
    parser.add_argument("--json", dest="json_output", default="", help="Write machine-readable report")
    args = parser.parse_args()

    report = build_report()
    if args.json_output:
        out = Path(args.json_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"wrote={out}")
    else:
        print_report(report)


if __name__ == "__main__":
    main()
