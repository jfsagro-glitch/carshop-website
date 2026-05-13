#!/usr/bin/env python3
"""Verify OEM candidates against public catalog pages and export provenance CSV.

This script is intentionally conservative:
- Accept when OEM token is present and brand hint is present on the same page, OR
- Accept when OEM token is present on at least 2 independent sources.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict, deque
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from generate_parts_catalog import OEM_LOOKUP  # noqa: E402

INPUT = ROOT / "data" / "oem_lookup_overrides.json"
CACHE_PATH = ROOT / "data" / "oem_verification_cache.json"
OUTPUT_CSV = ROOT / "data" / "oem_supplier_export.csv"

BRAND_BY_PREFIX = {
    "TY": "Toyota", "VW": "Volkswagen", "BM": "BMW", "MB": "Mercedes", "AU": "Audi",
    "HY": "Hyundai", "KI": "Kia", "NI": "Nissan", "HO": "Honda", "FO": "Ford",
    "CH": "Chevrolet", "MA": "Mazda", "LX": "Lexus", "SU": "Subaru", "MI": "Mitsubishi",
    "PE": "Peugeot", "RE": "Renault", "OP": "Opel", "SK": "Skoda", "VO": "Volvo",
    "SZ": "Suzuki", "IN": "Infiniti", "JP": "Jeep", "LR": "Land Rover", "PO": "Porsche",
    "DG": "Dodge", "CR": "Chrysler", "GM": "GMC", "CA": "Cadillac", "BU": "Buick",
    "MN": "Mini", "FI": "Fiat", "CI": "Citroen", "SE": "Seat", "GE": "Genesis",
    "AC": "Acura", "BY": "BYD", "GL": "Geely", "CY": "Chery", "HV": "Haval",
    "CG": "Changan", "TS": "Tesla", "TK": "Tanktuk", "SP": "Spark",
}

SOURCE_TEMPLATES = {
    "emex": "https://emex.ru/products/{oem}",
    "exist": "https://www.exist.ru/Price/?pcode={oem}",
    "rockauto": "https://www.rockauto.com/en/partsearch/?partnum={oem}",
    "autoparts24": "https://www.autoparts24.eu/search/1/?type=all&q={oem}",
    "japan-parts": "https://www.japan-parts.eu/search?keyword={oem}",
}

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


@dataclass
class Hit:
    source: str
    url: str
    status: int
    oem_hit: bool
    brand_hit: bool


def norm_oem(value: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(value or "").upper())


def load_candidates(path: Path) -> list[tuple[str, str, str]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    lookup = raw.get("lookup", raw)
    rows: list[tuple[str, str, str]] = []
    for prefix, codes in lookup.items():
        if not isinstance(codes, dict):
            continue
        for code, numbers in codes.items():
            values = numbers if isinstance(numbers, list) else [numbers]
            for number in values:
                oem = str(number).strip()
                if oem:
                    rows.append((str(prefix).upper(), str(code).upper(), oem))
    return rows


def load_base_lookup_candidates() -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for (prefix, code), numbers in OEM_LOOKUP.items():
        values = numbers if isinstance(numbers, list) else [numbers]
        for number in values:
            oem = str(number).strip()
            if oem:
                rows.append((str(prefix).upper(), str(code).upper(), oem))
    return rows


def fetch_hit(session: requests.Session, source: str, url: str, oem: str, brand: str, timeout: int) -> Hit:
    try:
        r = session.get(url, timeout=timeout)
        text = r.text[:250000].upper() if r.status_code < 500 else ""
        oem_token = norm_oem(oem)
        compressed = norm_oem(text)
        oem_hit = oem_token in compressed
        brand_hit = bool(brand and brand.upper() in text)
        return Hit(source=source, url=r.url, status=r.status_code, oem_hit=oem_hit, brand_hit=brand_hit)
    except Exception:
        return Hit(source=source, url=url, status=0, oem_hit=False, brand_hit=False)


def verify_one(prefix: str, code: str, oem: str, timeout: int) -> dict[str, Any]:
    brand = BRAND_BY_PREFIX.get(prefix, "")
    session = requests.Session()
    session.headers.update({"User-Agent": UA})

    hits: list[Hit] = []
    for source, template in SOURCE_TEMPLATES.items():
        url = template.format(oem=oem)
        hits.append(fetch_hit(session, source, url, oem, brand, timeout))

    oem_sources = [h for h in hits if h.oem_hit]
    has_brand_bound = any(h.oem_hit and h.brand_hit for h in hits)
    accepted = has_brand_bound or len(oem_sources) >= 2

    evidence = next((h for h in hits if h.oem_hit and h.brand_hit), None)
    if evidence is None and oem_sources:
        evidence = oem_sources[0]

    return {
        "prefix": prefix,
        "part_code": code,
        "oem_number": oem,
        "brand": brand,
        "accepted": accepted,
        "accepted_reason": "brand+oem" if has_brand_bound else ("multi-source-oem" if accepted else "insufficient"),
        "evidence_source": evidence.source if evidence else "",
        "evidence_url": evidence.url if evidence else "",
        "checked_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "hits": [
            {
                "source": h.source,
                "url": h.url,
                "status": h.status,
                "oem_hit": h.oem_hit,
                "brand_hit": h.brand_hit,
            }
            for h in hits
        ],
    }


def load_cache(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_cache(path: Path, cache: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def cache_key(prefix: str, code: str, oem: str) -> str:
    return f"{prefix}|{code}|{oem}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify OEM candidates from lookup sources against public catalogs")
    parser.add_argument("--input", default=str(INPUT), help="Input JSON with lookup")
    parser.add_argument("--cache", default=str(CACHE_PATH), help="Verification cache JSON")
    parser.add_argument("--output", default=str(OUTPUT_CSV), help="Output verified CSV")
    parser.add_argument("--limit", type=int, default=2000, help="Max candidate rows to process this run")
    parser.add_argument("--workers", type=int, default=12, help="Parallel workers")
    parser.add_argument("--timeout", type=int, default=12, help="HTTP timeout seconds")
    parser.add_argument("--include-base-lookup", action="store_true", default=True, help="Include base OEM_LOOKUP candidates")
    parser.add_argument("--no-include-base-lookup", action="store_false", dest="include_base_lookup", help="Skip base OEM_LOOKUP candidates")
    args = parser.parse_args()

    candidates = load_candidates(Path(args.input))
    if args.include_base_lookup:
        candidates.extend(load_base_lookup_candidates())
    candidates = sorted(set(candidates))
    cache = load_cache(Path(args.cache))

    # Keep one verified OEM per (prefix, part_code) in this run to maximize pair coverage.
    already_verified_pair = {
        (v.get("prefix"), v.get("part_code"))
        for v in cache.values()
        if isinstance(v, dict) and v.get("accepted")
    }

    by_prefix: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for prefix, code, oem in candidates:
        key = cache_key(prefix, code, oem)
        if key in cache:
            continue
        if (prefix, code) in already_verified_pair:
            continue
        by_prefix[prefix].append((prefix, code, oem))

    queue: list[tuple[str, str, str]] = []
    prefix_order = deque(sorted(by_prefix.keys()))
    idx_by_prefix: dict[str, int] = {p: 0 for p in by_prefix}
    while prefix_order and len(queue) < args.limit:
        prefix = prefix_order.popleft()
        idx = idx_by_prefix[prefix]
        group = by_prefix[prefix]
        if idx < len(group):
            queue.append(group[idx])
            idx_by_prefix[prefix] = idx + 1
            if idx + 1 < len(group):
                prefix_order.append(prefix)

    print(f"candidates_total={len(candidates)} queued={len(queue)} cache={len(cache)}")

    processed = accepted = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(verify_one, p, c, o, args.timeout) for (p, c, o) in queue]
        for fut in as_completed(futures):
            result = fut.result()
            key = cache_key(result["prefix"], result["part_code"], result["oem_number"])
            cache[key] = result
            processed += 1
            if result.get("accepted"):
                accepted += 1
                already_verified_pair.add((result["prefix"], result["part_code"]))
            if processed % 100 == 0:
                print(f"processed={processed} accepted={accepted}")

    save_cache(Path(args.cache), cache)

    rows = [
        v for v in cache.values()
        if isinstance(v, dict) and v.get("accepted") and v.get("evidence_url")
    ]
    rows.sort(key=lambda r: (r.get("prefix", ""), r.get("part_code", ""), r.get("oem_number", "")))

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "brand_prefix", "part_code", "oem_number", "source_name", "source_url", "retrieved_at",
                "brand", "model", "year_from", "year_to", "engine", "restyle", "vin_pattern",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "brand_prefix": row.get("prefix", ""),
                "part_code": row.get("part_code", ""),
                "oem_number": row.get("oem_number", ""),
                "source_name": row.get("evidence_source", ""),
                "source_url": row.get("evidence_url", ""),
                "retrieved_at": row.get("checked_at", ""),
                "brand": row.get("brand", ""),
                "model": "",
                "year_from": "",
                "year_to": "",
                "engine": "",
                "restyle": "",
                "vin_pattern": "",
            })

    pair_count = len({(r.get("prefix"), r.get("part_code")) for r in rows})
    print(f"cache_saved={args.cache}")
    print(f"verified_rows={len(rows)} verified_pairs={pair_count}")
    print(f"csv={out}")


if __name__ == "__main__":
    main()
