#!/usr/bin/env python3
"""
Brand-specific EPC importer for unresolved OEM gaps.
Runs targeted search only for selected source domains and unresolved brand x code pairs.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.import_from_oem_gaps import GapTargetedImporter

DATA_DIR = REPO_ROOT / "data"

GROUP_DOMAINS = {
    "bmw": {"realoem.com", "bmwcats.com"},
    "honda_acura": {"acurapartswarehouse.com", "hondaworld.ru"},
    "vag": {"partsale.eu", "elcats.ru"},
    "all_epc": {
        "realoem.com",
        "bmwcats.com",
        "acurapartswarehouse.com",
        "hondaworld.ru",
        "partsale.eu",
        "elcats.ru",
    },
}


def parse_sources(sources_str: str) -> List[Tuple[str, str]]:
    if not sources_str:
        return []
    result: List[Tuple[str, str]] = []
    for item in sources_str.split(";"):
        item = item.strip()
        if "(" in item and ")" in item:
            domain = item[: item.index("(")].strip()
            mode = item[item.index("(") + 1 : item.index(")")].strip()
            result.append((domain, mode))
        elif item:
            result.append((item, "direct"))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Import OEM from brand-specific EPC sources")
    parser.add_argument("--gap-worklist", type=Path, default=DATA_DIR / "oem_gap_worklist.csv")
    parser.add_argument("--output", type=Path, default=DATA_DIR / "oem_supplier_brand_epc.csv")
    parser.add_argument("--failed-output", type=Path, default=DATA_DIR / "oem_brand_epc_failed.csv")
    parser.add_argument("--source-group", choices=sorted(GROUP_DOMAINS.keys()), default="all_epc")
    parser.add_argument("--top-gaps", type=int, default=400)
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--timeout", type=int, default=8)
    args = parser.parse_args()

    allowed_domains = GROUP_DOMAINS[args.source_group]
    importer = GapTargetedImporter(timeout=args.timeout)

    selected_rows: List[Dict[str, str]] = []
    seen_pairs = set()

    with args.gap_worklist.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pair = (
                str(row.get("brand_prefix") or "").strip().upper(),
                str(row.get("part_code") or "").strip().upper(),
            )
            if not all(pair):
                continue
            if pair in importer._lookup_pairs:
                continue
            if pair in seen_pairs:
                continue

            sources = parse_sources(str(row.get("suggested_sources") or ""))
            filtered = [src for src in sources if src[0] in allowed_domains]
            if not filtered:
                continue

            row["_filtered_sources"] = "; ".join(f"{d} ({m})" for d, m in filtered)
            seen_pairs.add(pair)
            selected_rows.append(row)
            if args.top_gaps and len(selected_rows) >= args.top_gaps:
                break

    found = 0
    for idx, row in enumerate(selected_rows, start=1):
        sources = parse_sources(str(row.get("_filtered_sources") or ""))
        result = importer.search_gap(
            brand=str(row.get("brand") or ""),
            brand_prefix=str(row.get("brand_prefix") or "").upper(),
            part_code=str(row.get("part_code") or "").upper(),
            part_name=str(row.get("part_name") or ""),
            sources=sources,
            priority=str(row.get("priority") or "low"),
        )
        if result:
            importer.results.append(result)
            importer._lookup_pairs.add((result.get("brand_prefix", ""), result.get("part_code", "")))
            found += 1
        if idx % 25 == 0:
            print(f"progress={idx}/{len(selected_rows)} found={found}")

    if importer.results:
        importer.export_results(args.output)
    if importer.failed_searches:
        importer.export_failed_searches(args.failed_output)

    print(f"selected={len(selected_rows)} found={found} output={args.output}")


if __name__ == "__main__":
    main()
