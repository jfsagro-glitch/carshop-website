#!/usr/bin/env python3
"""Import OEM numbers from Emex/Exist product card pages only.

This module intentionally avoids extracting OEM directly from search-result pages.
It starts from seed OEMs and discovers additional OEM tokens by parsing product card links
inside Emex/Exist card pages.
"""
from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import requests

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "oem_supplier_merged_all.csv"
DEFAULT_OUTPUT = ROOT / "data" / "oem_supplier_product_cards_emex_exist.csv"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

EMEX_CARD = "https://emex.ru/products/{oem}"
EXIST_CARD = "https://www.exist.ru/Price/?pcode={oem}"

EMEX_LINK_RE = re.compile(r"(?:https?://(?:www\.)?emex\.ru)?/products/([A-Za-z0-9\-]{6,30})", re.IGNORECASE)
EXIST_LINK_RE = re.compile(r"(?:\?|&)pcode=([A-Za-z0-9\-]{6,30})", re.IGNORECASE)


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def valid_oem(token: str) -> bool:
    t = token.strip().upper()
    if len(t) < 6 or len(t) > 30:
        return False
    if not re.fullmatch(r"[A-Z0-9\-]+", t):
        return False
    digits = sum(ch.isdigit() for ch in t)
    letters = sum(ch.isalpha() for ch in t)
    if digits < 3:
        return False
    if letters == 0:
        return False
    return True


def load_seed_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def build_seed_queue(rows: list[dict[str, str]], seed_limit: int, seeds_per_pair: int) -> list[tuple[str, str, str, str]]:
    by_pair: dict[tuple[str, str], deque[str]] = defaultdict(deque)
    for row in rows:
        prefix = str(row.get("brand_prefix") or "").strip().upper()
        code = str(row.get("part_code") or "").strip().upper()
        oem = str(row.get("oem_number") or "").strip().upper()
        if not (prefix and code and valid_oem(oem)):
            continue
        key = (prefix, code)
        if oem not in by_pair[key]:
            by_pair[key].append(oem)

    queue: list[tuple[str, str, str, str]] = []
    idx_by_pair = {k: 0 for k in by_pair}
    pairs = deque(sorted(by_pair))
    while pairs and len(queue) < seed_limit:
        pair = pairs.popleft()
        i = idx_by_pair[pair]
        seeds = by_pair[pair]
        if i < len(seeds) and i < seeds_per_pair:
            queue.append((pair[0], pair[1], seeds[i], ""))
            idx_by_pair[pair] = i + 1
            if idx_by_pair[pair] < len(seeds) and idx_by_pair[pair] < seeds_per_pair:
                pairs.append(pair)
    return queue


def extract_emex_candidates(html: str) -> list[str]:
    out: list[str] = []
    seen = set()
    for token in EMEX_LINK_RE.findall(html):
        oem = token.strip().upper()
        if valid_oem(oem) and oem not in seen:
            seen.add(oem)
            out.append(oem)
    return out


def extract_exist_candidates(html: str) -> list[str]:
    out: list[str] = []
    seen = set()
    for token in EXIST_LINK_RE.findall(html):
        oem = token.strip().upper()
        if valid_oem(oem) and oem not in seen:
            seen.add(oem)
            out.append(oem)
    return out


def fetch_candidates(session: requests.Session, url: str, timeout: int, source: str) -> Iterable[str]:
    r = session.get(url, timeout=timeout)
    if r.status_code != 200:
        return []
    html = r.text
    if source == "emex":
        return extract_emex_candidates(html)
    return extract_exist_candidates(html)


def run_import(input_csv: Path, output_csv: Path, seed_limit: int, seeds_per_pair: int, timeout: int, max_new_per_seed: int) -> None:
    rows = load_seed_rows(input_csv)
    seeds = build_seed_queue(rows, seed_limit=seed_limit, seeds_per_pair=seeds_per_pair)
    print(f"seed_rows={len(rows)} seed_queue={len(seeds)}")

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    discovered: dict[tuple[str, str, str], dict[str, str]] = {}
    processed = 0

    for prefix, code, seed_oem, _ in seeds:
        seed_upper = seed_oem.upper()
        sources = [
            ("emex-product-card", "emex", EMEX_CARD.format(oem=seed_upper)),
            ("exist-product-card", "exist", EXIST_CARD.format(oem=seed_upper)),
        ]

        for source_name, source_kind, card_url in sources:
            try:
                cands = list(fetch_candidates(session, card_url, timeout=timeout, source=source_kind))
            except requests.RequestException:
                continue

            added = 0
            for cand in cands:
                if cand == seed_upper:
                    continue
                key = (prefix, code, cand)
                if key in discovered:
                    continue
                discovered[key] = {
                    "brand_prefix": prefix,
                    "part_code": code,
                    "oem_number": cand,
                    "source_name": source_name,
                    "source_url": card_url,
                    "retrieved_at": now_utc(),
                    "brand": "",
                    "model": "",
                    "year_from": "",
                    "year_to": "",
                    "engine": "",
                    "restyle": "",
                    "vin_pattern": "",
                }
                added += 1
                if added >= max_new_per_seed:
                    break

        processed += 1
        if processed % 200 == 0:
            print(f"processed={processed}/{len(seeds)} discovered={len(discovered)}")

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "brand_prefix", "part_code", "oem_number", "source_name", "source_url", "retrieved_at",
                "brand", "model", "year_from", "year_to", "engine", "restyle", "vin_pattern",
            ],
        )
        writer.writeheader()
        writer.writerows(sorted(discovered.values(), key=lambda r: (r["brand_prefix"], r["part_code"], r["oem_number"])))

    pair_count = len({(r["brand_prefix"], r["part_code"]) for r in discovered.values()})
    print(f"discovered_rows={len(discovered)} pairs={pair_count}")
    print(f"output={output_csv}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract OEM from Emex/Exist product card pages only")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Input CSV with seed OEM rows")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output CSV path")
    parser.add_argument("--seed-limit", type=int, default=4000, help="Max seed OEM rows to process")
    parser.add_argument("--seeds-per-pair", type=int, default=2, help="Max seed OEMs per brand/code pair")
    parser.add_argument("--timeout", type=int, default=12, help="HTTP timeout seconds")
    parser.add_argument("--max-new-per-seed", type=int, default=8, help="Max discovered OEMs kept per seed")
    args = parser.parse_args()

    run_import(
        input_csv=Path(args.input),
        output_csv=Path(args.output),
        seed_limit=args.seed_limit,
        seeds_per_pair=args.seeds_per_pair,
        timeout=args.timeout,
        max_new_per_seed=args.max_new_per_seed,
    )


if __name__ == "__main__":
    main()
