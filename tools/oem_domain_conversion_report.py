#!/usr/bin/env python3
"""Build per-domain conversion statistics for OEM gap sourcing.

Conversion is estimated from two artifacts:
- success CSV (rows with discovered OEM and source_url)
- worklist CSV (rows with suggested_sources per brand_prefix+part_code)

For each domain, this script computes:
- opportunities: how many unresolved pairs included this domain in suggested_sources
- hits: how many successful rows were attributed to this domain
- unique_pair_hits: successful distinct (brand_prefix, part_code) pairs
- conversion: unique_pair_hits / opportunities

Outputs JSON with global and per-brand domain rankings.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUCCESS = ROOT / "data" / "oem_supplier_low_overlap_high_medium.csv"
DEFAULT_WORKLIST = ROOT / "data" / "oem_gap_worklist_low_overlap.csv"
DEFAULT_OUT = ROOT / "data" / "oem_domain_conversion.json"


def parse_sources(value: str) -> list[str]:
    out: list[str] = []
    for item in (value or "").split(";"):
        item = item.strip()
        if not item:
            continue
        domain = item.split("(", 1)[0].strip().lower()
        if domain:
            out.append(domain)
    return out


def normalize_domain(value: str) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""
    if "://" not in text:
        text = f"https://{text}"
    try:
        host = urlparse(text).netloc.lower()
    except Exception:
        return ""
    if host.startswith("www."):
        host = host[4:]
    return host


def ratio(num: int, den: int) -> float:
    return round((num / den), 6) if den else 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description="Build OEM per-domain conversion report")
    parser.add_argument("--success", default=str(DEFAULT_SUCCESS), help="CSV with successful OEM rows")
    parser.add_argument("--worklist", default=str(DEFAULT_WORKLIST), help="CSV with suggested_sources")
    parser.add_argument("--output", default=str(DEFAULT_OUT), help="Output JSON report")
    parser.add_argument("--min-opportunities", type=int, default=1, help="Hide domains below this opportunities count")
    args = parser.parse_args()

    success_path = Path(args.success)
    worklist_path = Path(args.worklist)
    output_path = Path(args.output)

    if not success_path.exists():
        raise SystemExit(f"Missing success CSV: {success_path}")
    if not worklist_path.exists():
        raise SystemExit(f"Missing worklist CSV: {worklist_path}")

    opportunities_global: dict[str, int] = defaultdict(int)
    opportunities_brand: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    with worklist_path.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            prefix = str(row.get("brand_prefix") or "").strip().upper()
            seen = set(parse_sources(str(row.get("suggested_sources") or "")))
            for d in seen:
                opportunities_global[d] += 1
                opportunities_brand[prefix][d] += 1

    hits_global: dict[str, int] = defaultdict(int)
    hits_brand: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    pair_hits_global: dict[str, set[tuple[str, str]]] = defaultdict(set)
    pair_hits_brand: dict[str, dict[str, set[tuple[str, str]]]] = defaultdict(lambda: defaultdict(set))

    with success_path.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            prefix = str(row.get("brand_prefix") or "").strip().upper()
            part_code = str(row.get("part_code") or "").strip().upper()
            domain = normalize_domain(row.get("source_url") or row.get("source_name") or "")
            if not domain:
                continue
            key = (prefix, part_code)
            hits_global[domain] += 1
            hits_brand[prefix][domain] += 1
            pair_hits_global[domain].add(key)
            pair_hits_brand[prefix][domain].add(key)

    def build_domain_stats(hits: dict[str, int], opportunities: dict[str, int], pair_hits: dict[str, set[tuple[str, str]]]):
        stats = []
        domains = set(opportunities) | set(hits)
        for d in domains:
            opp = int(opportunities.get(d, 0))
            if opp < args.min_opportunities:
                continue
            pair_count = len(pair_hits.get(d, set()))
            stat = {
                "domain": d,
                "opportunities": opp,
                "hits": int(hits.get(d, 0)),
                "unique_pair_hits": pair_count,
                "conversion": ratio(pair_count, opp),
            }
            stats.append(stat)
        stats.sort(key=lambda x: (x["conversion"], x["unique_pair_hits"], x["hits"]), reverse=True)
        return stats

    global_stats = build_domain_stats(hits_global, opportunities_global, pair_hits_global)

    by_brand = {}
    for prefix in sorted(set(opportunities_brand) | set(hits_brand)):
        brand_stats = build_domain_stats(
            hits_brand.get(prefix, {}),
            opportunities_brand.get(prefix, {}),
            pair_hits_brand.get(prefix, {}),
        )
        by_brand[prefix] = brand_stats

    report = {
        "success_csv": str(success_path),
        "worklist_csv": str(worklist_path),
        "generated_at": __import__("datetime").datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "min_opportunities": args.min_opportunities,
        "global": global_stats,
        "by_brand": by_brand,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"written={output_path} global_domains={len(global_stats)} brands={len(by_brand)}")


if __name__ == "__main__":
    main()
