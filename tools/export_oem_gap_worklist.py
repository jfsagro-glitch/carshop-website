#!/usr/bin/env python3
"""Export unresolved strict OEM gaps as a CSV worklist with suggested sources.

This does not invent OEMs. It identifies remaining brand x part-code holes after
strict merge and annotates them with likely next real sources for manual/API import.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from generate_parts_catalog import get_merged_oem_lookup  # noqa: E402

PARTS_CATALOG = ROOT / "data" / "parts_catalog.json"
SOURCE_CANDIDATES = ROOT / "data" / "oem_source_candidates.json"
DEFAULT_OUT = ROOT / "data" / "oem_gap_worklist.csv"

BRAND_SOURCE_MAP = {
    "Toyota": ["japan-parts.eu", "exist.ru", "toyotacarmine.ru", "epcdata.ru", "japancats.ru", "autoparts24.eu", "emex.ru"],
    "Lexus": ["japan-parts.eu", "exist.ru", "needet.ru", "epcdata.ru", "japancats.ru", "autoparts24.eu", "emex.ru"],
    "Honda": ["hondapartsdeals.com", "hondaworld.ru", "japan-parts.eu", "exist.ru", "autoparts24.eu", "emex.ru"],
    "Acura": ["acurapartswarehouse.com", "japan-parts.eu", "exist.ru", "needet.ru", "hondaworld.ru", "emex.ru"],
    "Hyundai": ["hyundai.a-inside.ru", "exist.ru", "autoparts24.eu", "alvadi.ee", "emex.ru"],
    "Kia": ["kia.a-inside.ru", "exist.ru", "autoparts24.eu", "alvadi.ee", "emex.ru"],
    "Nissan": ["japan-parts.eu", "exist.ru", "epcdata.ru", "japancats.ru", "autoparts24.eu", "emex.ru"],
    "Infiniti": ["japan-parts.eu", "exist.ru", "epcdata.ru", "japancats.ru", "needet.ru", "emex.ru"],
    "Mazda": ["japan-parts.eu", "exist.ru", "epcdata.ru", "japancats.ru", "autoparts24.eu", "emex.ru"],
    "Mitsubishi": ["japan-parts.eu", "exist.ru", "mitsubishi-autoparts.com.ua", "japancats.ru", "autoparts24.eu", "emex.ru"],
    "Subaru": ["japan-parts.eu", "exist.ru", "epcdata.ru", "japancats.ru", "autoparts24.eu", "emex.ru"],
    "Suzuki": ["japan-parts.eu", "exist.ru", "epcdata.ru", "japancats.ru", "autoparts24.eu", "emex.ru"],
    "Volkswagen": ["partsale.eu", "elcats.ru", "autoparts24.eu", "alvadi.ee", "exist.ru", "emex.ru"],
    "Audi": ["partsale.eu", "elcats.ru", "autoparts24.eu", "alvadi.ee", "exist.ru", "emex.ru"],
    "Skoda": ["partsale.eu", "elcats.ru", "autoparts24.eu", "alvadi.ee", "exist.ru", "emex.ru"],
    "Seat": ["partsale.eu", "elcats.ru", "autoparts24.eu", "alvadi.ee", "exist.ru", "emex.ru"],
    "BMW": ["realoem.com", "bmwcats.com", "autoparts24.eu", "alvadi.ee", "exist.ru", "emex.ru"],
    "Mini": ["realoem.com", "bmwcats.com", "japan-parts.eu", "autoparts24.eu", "alvadi.ee", "exist.ru", "emex.ru"],
    "Mercedes-Benz": ["elcats.ru", "autoparts24.eu", "alvadi.ee", "exist.ru", "jedip.ru", "emex.ru"],
    "Ford": ["autoparts24.eu", "alvadi.ee", "exist.ru", "avtoto.ru", "fordparts.com", "oemfordpart.com", "emex.ru"],
    "Chevrolet": ["gmpartsgiant.com", "autoparts24.eu", "exist.ru", "avtoto.ru", "gmpartsdepartment.com", "baxterautoparts.com", "emex.ru"],
    "GMC": ["gmpartsgiant.com", "autoparts24.eu", "exist.ru", "avtoto.ru", "gmpartsdepartment.com", "baxterautoparts.com", "emex.ru"],
    "Cadillac": ["gmpartsgiant.com", "autoparts24.eu", "exist.ru", "avtoto.ru", "gmpartsdepartment.com", "baxterautoparts.com", "emex.ru"],
    "Buick": ["gmpartsgiant.com", "autoparts24.eu", "exist.ru", "avtoto.ru", "gmpartsdepartment.com", "baxterautoparts.com", "emex.ru"],
    "Chrysler": ["autoparts24.eu", "exist.ru", "factorychryslerparts.com", "moparpartsoverstock.com", "hemi.by", "emex.ru"],
    "Dodge": ["autoparts24.eu", "exist.ru", "factorychryslerparts.com", "moparpartsoverstock.com", "hemi.by", "emex.ru"],
    "Jeep": ["autoparts24.eu", "exist.ru", "jeepchryslerparts.eu", "moparpartsoverstock.com", "hemi.by", "emex.ru"],
    "Peugeot": ["autoparts24.eu", "alvadi.ee", "exist.ru", "elcats.ru", "emex.ru"],
    "Citroen": ["autoparts24.eu", "alvadi.ee", "exist.ru", "elcats.ru", "emex.ru"],
    "Renault": ["autoparts24.eu", "alvadi.ee", "exist.ru", "elcats.ru", "emex.ru"],
    "Opel": ["autoparts24.eu", "alvadi.ee", "exist.ru", "elcats.ru", "emex.ru"],
    "Fiat": ["autoparts24.eu", "alvadi.ee", "exist.ru", "elcats.ru", "emex.ru"],
    "Land Rover": ["autoparts24.eu", "alvadi.ee", "exist.ru", "new.lrcat.com", "emex.ru"],
    "Porsche": ["autoparts24.eu", "alvadi.ee", "exist.ru", "elcats.ru", "auto2.ru", "emex.ru"],
    "Volvo": ["autoparts24.eu", "alvadi.ee", "exist.ru", "elcats.ru", "emex.ru"],
    "BYD": ["exist.ru", "relines.ru", "xn--80aaonli0a.xn--p1ai", "autoparts24.eu", "shop.chinacar-club.ru", "emex.ru"],
    "Geely": ["exist.ru", "relines.ru", "xn--80aaonli0a.xn--p1ai", "autoparts24.eu", "shop.chinacar-club.ru", "emex.ru"],
    "Chery": ["exist.ru", "relines.ru", "xn--80aaonli0a.xn--p1ai", "autoparts24.eu", "shop.chinacar-club.ru", "emex.ru"],
    "Haval": ["exist.ru", "irito-parts.ru", "relines.ru", "autoparts24.eu", "shop.chinacar-club.ru", "emex.ru"],
    "Changan": ["exist.ru", "relines.ru", "xn--80aaonli0a.xn--p1ai", "autoparts24.eu", "shop.chinacar-club.ru", "emex.ru"],
    "Tesla": ["autoparts24.eu", "exist.ru", "parts.com", "usa-auto.ru", "findpart.org", "emex.ru"],
    "Genesis": ["hyundai.a-inside.ru", "kia.a-inside.ru", "autoparts24.eu", "exist.ru", "alvadi.ee", "emex.ru"],
}


def load_sources() -> dict[str, dict]:
    rows = json.loads(SOURCE_CANDIDATES.read_text(encoding="utf-8"))
    return {row["domain"]: row for row in rows}


def source_summary(brand: str, source_index: dict[str, dict]) -> str:
    domains = BRAND_SOURCE_MAP.get(brand, ["exist.ru", "avtoto.ru", "emex.ru", "rmsauto.ru", "elcats.ru"])
    if "exist.ru" not in domains:
        domains = [*domains, "exist.ru"]
    if "avtoto.ru" not in domains:
        domains = [*domains, "avtoto.ru"]
    parts: list[str] = []
    for domain in domains:
        row = source_index.get(domain)
        if not row:
            parts.append(domain)
            continue
        parts.append(f"{domain} ({row.get('mode', 'manual_check')})")
    return "; ".join(parts)


def build_rows() -> list[dict[str, str]]:
    catalog = json.loads(PARTS_CATALOG.read_text(encoding="utf-8"))
    lookup = get_merged_oem_lookup()
    source_index = load_sources()

    parts_by_code = {part["code"]: part for part in catalog.get("parts_template", [])}
    rows: list[dict[str, str]] = []
    for brand in catalog.get("brands", []):
        brand_name = brand["name"]
        prefix = brand.get("prefix", brand_name[:2].upper())
        for code, part in parts_by_code.items():
            if (prefix, code) in lookup:
                continue
            rows.append({
                "brand": brand_name,
                "brand_prefix": prefix,
                "part_code": code,
                "part_name": part.get("name", ""),
                "category": part.get("category", ""),
                "group": part.get("group", ""),
                "priority": "high" if part.get("category") in {"ТО", "Тормозная система", "Подвеска", "Двигатель", "Охлаждение", "Трансмиссия"} or part.get("group") in {"ТО", "Тормоза", "Подвеска", "Двигатель", "Охлаждение", "Трансмиссия"} else "medium",
                "suggested_sources": source_summary(brand_name, source_index),
            })
    rows.sort(key=lambda row: (row["priority"] != "high", row["brand"], row["category"], row["part_code"]))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Export unresolved strict OEM gaps as worklist CSV")
    parser.add_argument("--output", default=str(DEFAULT_OUT), help="CSV output path")
    args = parser.parse_args()

    rows = build_rows()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "brand", "brand_prefix", "part_code", "part_name", "category", "group", "priority", "suggested_sources",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    high = sum(1 for row in rows if row["priority"] == "high")
    print(f"rows={len(rows)} high_priority={high} output={output}")


if __name__ == "__main__":
    main()
