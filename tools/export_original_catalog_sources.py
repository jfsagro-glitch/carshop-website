#!/usr/bin/env python3
"""Export public original-catalog entry points from Exist and AvtoTO.

These pages are source indexes, not flat OEM exports. The output is used as
provenance/navigation metadata for remaining OEM gaps.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "oem_original_catalog_sources.json"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

PREFIX_TO_BRAND_SLUGS = {
    "AC": ["acura"],
    "AU": ["audi"],
    "BM": ["bmw"],
    "BU": ["buick"],
    "BY": ["byd"],
    "CA": ["cadillac"],
    "CG": ["changan"],
    "CH": ["chevrolet"],
    "CI": ["citroen"],
    "CR": ["chrysler"],
    "CY": ["chery", "omoda"],
    "DG": ["dodge"],
    "FI": ["fiat"],
    "FO": ["ford"],
    "GE": ["genesis"],
    "GL": ["geely"],
    "GM": ["gmc"],
    "HO": ["honda"],
    "HV": ["haval", "great-wall"],
    "HY": ["hyundai"],
    "IN": ["infiniti"],
    "JP": ["jeep"],
    "KI": ["kia"],
    "LR": ["land-rover"],
    "LX": ["lexus"],
    "MA": ["mazda"],
    "MB": ["mercedes"],
    "MI": ["mitsubishi"],
    "MN": ["mini"],
    "NI": ["nissan"],
    "OP": ["opel", "vauxhall"],
    "PE": ["peugeot"],
    "PO": ["porsche"],
    "RE": ["renault"],
    "SE": ["seat"],
    "SK": ["skoda"],
    "SU": ["subaru"],
    "SZ": ["suzuki"],
    "TY": ["toyota"],
    "VO": ["volvo"],
    "VW": ["vw", "volkswagen"],
}


def fetch(url: str, timeout: int) -> str:
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    response.raise_for_status()
    return response.text


def normalize_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def extract_avtoto(timeout: int) -> list[dict[str, str]]:
    base = "https://www.avtoto.ru"
    html = fetch(f"{base}/catalogs/original/", timeout)
    soup = BeautifulSoup(html, "html.parser")
    rows: list[dict[str, str]] = []

    for link in soup.find_all("a", href=True):
        href = str(link["href"])
        if "catalog_original.acat:get_models_list" not in href:
            continue
        brand_match = re.search(r"catalog:([^.#]+)", href)
        brand_id_match = re.search(r"brand_id:(\d+)", href)
        if not brand_match:
            continue
        slug = normalize_slug(brand_match.group(1))
        rows.append(
            {
                "source": "AvtoTO original catalogs",
                "domain": "avtoto.ru",
                "brand_slug": slug,
                "brand_id": brand_id_match.group(1) if brand_id_match else "",
                "url": urljoin(base, href),
                "mode": "public_index_spa_navigation",
            }
        )
    return rows


def extract_exist(timeout: int) -> list[dict[str, str]]:
    base = "https://www.exist.ru"
    html = fetch(f"{base}/Catalog/Links/Original", timeout)
    soup = BeautifulSoup(html, "html.parser")
    rows: list[dict[str, str]] = []

    for link in soup.find_all("a", href=True):
        text = link.get_text(" ", strip=True)
        href = str(link["href"])
        joined = urljoin(base, href)
        text_lower = text.lower()
        if not any(word in text_lower for word in ("каталог оригин", "original")):
            continue
        if not any(domain in joined.lower() for domain in ("elcats", "japancats", "exist")):
            continue
        slug = normalize_slug(text)
        rows.append(
            {
                "source": "Exist original catalog links",
                "domain": "exist.ru",
                "brand_slug": slug,
                "brand_id": "",
                "url": joined,
                "mode": "public_index_external_catalog",
            }
        )
    return rows


def attach_prefixes(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for row in rows:
        haystack = normalize_slug(" ".join([row.get("brand_slug", ""), row.get("url", "")]))
        prefixes = [
            prefix
            for prefix, slugs in PREFIX_TO_BRAND_SLUGS.items()
            if any(slug in haystack for slug in slugs)
        ]
        if not prefixes:
            continue
        for prefix in prefixes:
            item = dict(row)
            item["brand_prefix"] = prefix
            out.append(item)
    return sorted(out, key=lambda x: (x["brand_prefix"], x["domain"], x["url"]))


def main() -> None:
    parser = argparse.ArgumentParser(description="Export public original catalog source links")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    rows = attach_prefixes(extract_avtoto(args.timeout) + extract_exist(args.timeout))
    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "note": "Source indexes for manual/API-backed OEM lookup; not flat OEM-number exports.",
        "rows": rows,
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"rows={len(rows)} output={output}")


if __name__ == "__main__":
    main()
