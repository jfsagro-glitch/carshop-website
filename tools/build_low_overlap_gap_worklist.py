#!/usr/bin/env python3
"""Build low-overlap OEM gap worklist.

Rewrites suggested sources for unresolved pairs by dropping high-overlap domains and
injecting brand-specific alternatives to improve unique coverage discovery.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IN = ROOT / "data" / "oem_gap_worklist.csv"
DEFAULT_OUT = ROOT / "data" / "oem_gap_worklist_low_overlap.csv"

HIGH_OVERLAP_DOMAINS = {
    "emex.ru",
    "rmsauto.ru",
    "elcats.ru",
    "parts.com",
    "gmpartsdepartment.com",
    "factorychryslerparts.com",
    "jeepchryslerparts.eu",
}

BRAND_LOW_OVERLAP = {
    "AC": ["acurapartswarehouse.com", "hondaworld.ru", "hondapartsdeals.com"],
    "HO": ["hondaworld.ru", "hondapartsdeals.com", "acurapartswarehouse.com"],
    "BM": ["realoem.com", "bmwcats.com"],
    "MN": ["realoem.com", "bmwcats.com"],
    "VW": ["partsale.eu", "trshop.audi.de"],
    "AU": ["partsale.eu", "trshop.audi.de"],
    "SK": ["partsale.eu", "trshop.audi.de"],
    "SE": ["partsale.eu", "trshop.audi.de"],
    "FO": ["fordparts.com", "oemfordpart.com"],
    "CH": ["gmpartsdepartment.com", "parts.com"],
    "GM": ["gmpartsdepartment.com", "parts.com"],
    "CA": ["gmpartsdepartment.com", "parts.com"],
    "BU": ["gmpartsdepartment.com", "parts.com"],
    "CR": ["factorychryslerparts.com", "jeepchryslerparts.eu"],
    "DG": ["factorychryslerparts.com", "jeepchryslerparts.eu"],
    "JP": ["jeepchryslerparts.eu", "factorychryslerparts.com"],
    "TY": ["toyotacarmine.ru", "japancats.ru"],
    "LX": ["needet.ru", "japancats.ru"],
    "NI": ["japancats.ru", "needet.ru"],
    "IN": ["japancats.ru", "needet.ru"],
    "MA": ["japancats.ru", "needet.ru"],
    "MI": ["mitsubishi-autoparts.com.ua", "japancats.ru"],
    "HY": ["hyundai.a-inside.ru", "kia.a-inside.ru"],
    "KI": ["kia.a-inside.ru", "hyundai.a-inside.ru"],
    "FI": ["eper.fiatklubpolska.pl", "fiatdalys.lt"],
    "PE": ["public.servicebox.peugeot.com", "service.citroen.com"],
    "CI": ["service.citroen.com", "public.servicebox.peugeot.com"],
    "LR": ["new.lrcat.com"],
    "BY": ["xn--80aaonli0a.xn--p1ai", "relines.ru"],
    "GL": ["relines.ru", "xn--80aaonli0a.xn--p1ai"],
    "CY": ["relines.ru", "xn--80aaonli0a.xn--p1ai"],
    "HV": ["irito-parts.ru", "relines.ru"],
    "CG": ["relines.ru", "xn--80aaonli0a.xn--p1ai"],
}


def parse_sources(value: str) -> list[str]:
    out = []
    for item in (value or "").split(";"):
        item = item.strip()
        if not item:
            continue
        if "(" in item and ")" in item:
            domain = item[: item.index("(")].strip()
            mode = item[item.index("(") + 1 : item.index(")")].strip()
        else:
            domain = item
            mode = "manual_check"
        if domain:
            out.append(f"{domain}|{mode}")
    return out


def domain_only(entry: str) -> str:
    return entry.split("|", 1)[0].strip()


def mode_only(entry: str) -> str:
    return entry.split("|", 1)[1].strip() if "|" in entry else "manual_check"


def render_sources(entries: list[str]) -> str:
    return "; ".join(f"{domain_only(e)} ({mode_only(e)})" for e in entries)


def load_domain_scores(path: str) -> dict[str, dict[str, float]]:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        return {}
    raw = json.load(open(p, encoding="utf-8"))
    out: dict[str, dict[str, float]] = {}
    by_brand = raw.get("by_brand") or {}
    for prefix, stats in by_brand.items():
        scores: dict[str, float] = {}
        for item in stats or []:
            domain = str(item.get("domain") or "").strip().lower()
            if not domain:
                continue
            scores[domain] = float(item.get("conversion") or 0.0)
        out[str(prefix).strip().upper()] = scores
    return out


def rank_entries(entries: list[str], prefix: str, score_by_brand: dict[str, dict[str, float]]) -> list[str]:
    scores = score_by_brand.get(prefix, {})

    def key_fn(item: str):
        domain = domain_only(item).lower()
        score = scores.get(domain, -1.0)
        return (score,)

    return sorted(entries, key=key_fn, reverse=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build low-overlap gap worklist")
    parser.add_argument("--input", default=str(DEFAULT_IN), help="Input gap worklist CSV")
    parser.add_argument("--output", default=str(DEFAULT_OUT), help="Output low-overlap worklist CSV")
    parser.add_argument("--min-sources", type=int, default=3, help="Minimum suggested sources per row")
    parser.add_argument("--scores-json", default="", help="Optional domain conversion JSON from oem_domain_conversion_report.py")
    parser.add_argument("--top-domains-per-brand", type=int, default=0, help="Keep only top-N scored domains per brand (0 disables)")
    args = parser.parse_args()

    src = Path(args.input)
    out = Path(args.output)

    with src.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
        fields = list(rows[0].keys()) if rows else []

    score_by_brand = load_domain_scores(args.scores_json)

    changed = 0
    added_by_brand = defaultdict(int)

    for row in rows:
        prefix = str(row.get("brand_prefix") or "").strip().upper()
        current = parse_sources(str(row.get("suggested_sources") or ""))

        filtered = [e for e in current if domain_only(e) not in HIGH_OVERLAP_DOMAINS]
        existing_domains = {domain_only(e) for e in filtered}

        for d in BRAND_LOW_OVERLAP.get(prefix, []):
            if d not in existing_domains:
                filtered.append(f"{d}|manual_check")
                existing_domains.add(d)
                added_by_brand[prefix] += 1
            if len(filtered) >= args.min_sources:
                break

        filtered = rank_entries(filtered, prefix, score_by_brand)

        if args.top_domains_per_brand > 0 and filtered:
            keep = filtered[: args.top_domains_per_brand]
            if len(keep) < args.min_sources:
                keep = filtered[: args.min_sources]
            filtered = keep

        if not filtered:
            filtered = current[: args.min_sources]

        new_value = render_sources(filtered)
        if new_value != (row.get("suggested_sources") or ""):
            row["suggested_sources"] = new_value
            changed += 1

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"rows={len(rows)} changed={changed} output={out}")
    for prefix in sorted(added_by_brand):
        print(f"brand={prefix} low_overlap_added={added_by_brand[prefix]}")


if __name__ == "__main__":
    main()
