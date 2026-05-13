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
    "Toyota": ["toyotacarmine.ru", "epcdata.ru", "japancats.ru", "emex.ru"],
    "Lexus": ["needet.ru", "epcdata.ru", "japancats.ru", "emex.ru"],
    "Honda": ["hondapartsdeals.com", "hondaworld.ru", "emex.ru"],
    "Acura": ["acurapartswarehouse.com", "needet.ru", "hondaworld.ru", "emex.ru"],
    "Hyundai": ["hyundai.a-inside.ru", "emex.ru", "rmsauto.ru"],
    "Kia": ["kia.a-inside.ru", "emex.ru", "rmsauto.ru"],
    "Nissan": ["epcdata.ru", "japancats.ru", "emex.ru", "rmsauto.ru"],
    "Infiniti": ["epcdata.ru", "japancats.ru", "needet.ru", "emex.ru"],
    "Mazda": ["epcdata.ru", "japancats.ru", "emex.ru", "rmsauto.ru"],
    "Mitsubishi": ["mitsubishi-autoparts.com.ua", "japancats.ru", "emex.ru"],
    "Subaru": ["epcdata.ru", "japancats.ru", "emex.ru", "rmsauto.ru"],
    "Suzuki": ["epcdata.ru", "japancats.ru", "emex.ru", "rmsauto.ru"],
    "Volkswagen": ["partsale.eu", "elcats.ru", "emex.ru"],
    "Audi": ["trshop.audi.de", "partsale.eu", "elcats.ru"],
    "Skoda": ["partsale.eu", "elcats.ru", "emex.ru"],
    "Seat": ["partsale.eu", "elcats.ru", "emex.ru"],
    "BMW": ["realoem.com", "bmwcats.com", "etk.bmwsar.ru", "emex.ru"],
    "Mini": ["realoem.com", "bmwcats.com", "etk.bmwsar.ru", "emex.ru"],
    "Mercedes-Benz": ["elcats.ru", "jedip.ru", "emex.ru", "rmsauto.ru"],
    "Ford": ["fordparts.com", "oemfordpart.com", "emex.ru"],
    "Chevrolet": ["gmpartsdepartment.com", "baxterautoparts.com", "parts.com", "emex.ru"],
    "GMC": ["gmpartsdepartment.com", "baxterautoparts.com", "parts.com", "emex.ru"],
    "Cadillac": ["gmpartsdepartment.com", "baxterautoparts.com", "parts.com", "emex.ru"],
    "Buick": ["gmpartsdepartment.com", "baxterautoparts.com", "parts.com", "emex.ru"],
    "Chrysler": ["factorychryslerparts.com", "moparpartsoverstock.com", "hemi.by", "jeepchryslerparts.eu", "emex.ru"],
    "Dodge": ["factorychryslerparts.com", "moparpartsoverstock.com", "hemi.by", "jeepchryslerparts.eu", "emex.ru"],
    "Jeep": ["jeepchryslerparts.eu", "moparpartsoverstock.com", "factorychryslerparts.com", "hemi.by", "emex.ru"],
    "Peugeot": ["public.servicebox.peugeot.com", "elcats.ru", "emex.ru"],
    "Citroen": ["service.citroen.com", "elcats.ru", "emex.ru"],
    "Renault": ["elcats.ru", "emex.ru", "rmsauto.ru"],
    "Opel": ["elcats.ru", "emex.ru", "rmsauto.ru"],
    "Fiat": ["eper.fiatklubpolska.pl", "fiatdalys.lt", "emex.ru"],
    "Land Rover": ["new.lrcat.com", "emex.ru", "rmsauto.ru"],
    "Porsche": ["elcats.ru", "auto2.ru", "emex.ru", "rmsauto.ru"],
    "Volvo": ["elcats.ru", "emex.ru", "rmsauto.ru"],
    "BYD": ["xn--80aaonli0a.xn--p1ai", "relines.ru", "shop.chinacar-club.ru", "autodubok.ru", "emex.ru"],
    "Geely": ["relines.ru", "xn--80aaonli0a.xn--p1ai", "shop.chinacar-club.ru", "autodubok.ru", "emex.ru"],
    "Chery": ["relines.ru", "xn--80aaonli0a.xn--p1ai", "shop.chinacar-club.ru", "autodubok.ru", "emex.ru"],
    "Haval": ["irito-parts.ru", "relines.ru", "shop.chinacar-club.ru", "autodubok.ru", "emex.ru"],
    "Changan": ["relines.ru", "xn--80aaonli0a.xn--p1ai", "shop.chinacar-club.ru", "autodubok.ru", "emex.ru"],
    "Tesla": ["parts.com", "usa-auto.ru", "findpart.org", "emex.ru"],
    "Genesis": ["hyundai.a-inside.ru", "kia.a-inside.ru", "emex.ru", "rmsauto.ru"],
}


def load_sources() -> dict[str, dict]:
    rows = json.loads(SOURCE_CANDIDATES.read_text(encoding="utf-8"))
    return {row["domain"]: row for row in rows}


def source_summary(brand: str, source_index: dict[str, dict]) -> str:
    domains = BRAND_SOURCE_MAP.get(brand, ["emex.ru", "rmsauto.ru", "elcats.ru"])
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
                "priority": "high" if part.get("category") in {"ТО", "Тормозная система", "Подвеска", "Двигатель", "Охлаждение", "Трансмиссия"} or part.get("group") in {"ТО", "Тормоза", "Подвеска", "Двигатель", "Охлаждение", "Трансмиссия"} else "normal",
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
