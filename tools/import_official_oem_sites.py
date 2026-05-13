#!/usr/bin/env python3
"""Import exact OEM rows from official brand parts sites using sitemap product pages.

The importer is conservative:
- It only loads brands with known official sitemap feeds.
- It only maps product pages to internal part codes using explicit keyword rules.
- It fetches the product page and confirms the product title/specification before export.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import re
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
WORKLIST = ROOT / "data" / "oem_gap_worklist.csv"
DEFAULT_OUTPUT = ROOT / "data" / "oem_supplier_official_sites.csv"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
REQUEST_TIMEOUT_SHORT = 40
REQUEST_TIMEOUT_LONG = 60


SITE_CONFIGS = {
    "BM": {
        "brand": "BMW",
        "source_name": "BMWPartsDeal",
        "source_domain": "www.bmwpartsdeal.com",
        "sitemap": "https://www.bmwpartsdeal.com/sitemap.xml",
    },
    "AC": {
        "brand": "Acura",
        "source_name": "AcuraPartsWarehouse",
        "source_domain": "www.acurapartswarehouse.com",
        "sitemap": "https://www.acurapartswarehouse.com/sitemap.xml",
    },
    "HO": {
        "brand": "Honda",
        "source_name": "HondaPartsNow",
        "source_domain": "www.hondapartsnow.com",
        "sitemap": "https://www.hondapartsnow.com/sitemap.xml",
    },
    "TY": {
        "brand": "Toyota",
        "source_name": "ToyotaPartsDeal",
        "source_domain": "www.toyotapartsdeal.com",
        "sitemap": "https://www.toyotapartsdeal.com/sitemap.xml",
    },
    "LX": {
        "brand": "Lexus",
        "source_name": "LexusPartsNow",
        "source_domain": "www.lexuspartsnow.com",
        "sitemap": "https://www.lexuspartsnow.com/sitemap.xml",
    },
    "HY": {
        "brand": "Hyundai",
        "source_name": "HyundaiPartsDeal",
        "source_domain": "www.hyundaipartsdeal.com",
        "sitemap": "https://www.hyundaipartsdeal.com/sitemap.xml",
    },
    "KI": {
        "brand": "Kia",
        "source_name": "KiaPartsNow",
        "source_domain": "www.kiapartsnow.com",
        "sitemap": "https://www.kiapartsnow.com/sitemap.xml",
    },
    "NI": {
        "brand": "Nissan",
        "source_name": "NissanPartsDeal",
        "source_domain": "www.nissanpartsdeal.com",
        "sitemap": "https://www.nissanpartsdeal.com/sitemap.xml",
    },
    "FO": {
        "brand": "Ford",
        "source_name": "FordPartsGiant",
        "source_domain": "www.fordpartsgiant.com",
        "sitemap": "https://www.fordpartsgiant.com/sitemap.xml",
        "brand_aliases": ["ford"],
    },
    "CH": {
        "brand": "Chevrolet",
        "source_name": "GMPartsGiant",
        "source_domain": "www.gmpartsgiant.com",
        "sitemap": "https://www.gmpartsgiant.com/sitemap.xml",
        "brand_aliases": ["chevrolet", "chevy"],
    },
    "GM": {
        "brand": "GMC",
        "source_name": "GMPartsGiant",
        "source_domain": "www.gmpartsgiant.com",
        "sitemap": "https://www.gmpartsgiant.com/sitemap.xml",
        "brand_aliases": ["gmc"],
    },
    "CA": {
        "brand": "Cadillac",
        "source_name": "GMPartsGiant",
        "source_domain": "www.gmpartsgiant.com",
        "sitemap": "https://www.gmpartsgiant.com/sitemap.xml",
        "brand_aliases": ["cadillac"],
    },
    "BU": {
        "brand": "Buick",
        "source_name": "GMPartsGiant",
        "source_domain": "www.gmpartsgiant.com",
        "sitemap": "https://www.gmpartsgiant.com/sitemap.xml",
        "brand_aliases": ["buick"],
    },
    "CR": {
        "brand": "Chrysler",
        "source_name": "MoparPartsGiant",
        "source_domain": "www.moparpartsgiant.com",
        "sitemap": "https://www.moparpartsgiant.com/sitemap.xml",
        "brand_aliases": ["chrysler"],
    },
    "DG": {
        "brand": "Dodge",
        "source_name": "MoparPartsGiant",
        "source_domain": "www.moparpartsgiant.com",
        "sitemap": "https://www.moparpartsgiant.com/sitemap.xml",
        "brand_aliases": ["dodge"],
    },
    "JP": {
        "brand": "Jeep",
        "source_name": "MoparPartsGiant",
        "source_domain": "www.moparpartsgiant.com",
        "sitemap": "https://www.moparpartsgiant.com/sitemap.xml",
        "brand_aliases": ["jeep"],
    },
    "SU": {
        "brand": "Subaru",
        "source_name": "SubaruPartsDeal",
        "source_domain": "www.subarupartsdeal.com",
        "sitemap": "https://www.subarupartsdeal.com/sitemap.xml",
    },
    "VW": {
        "brand": "Volkswagen",
        "source_name": "VWPartsInfo",
        "source_domain": "parts.volkswagen.de",
        "sitemap": "https://parts.volkswagen.de/sitemap.xml",
        "brand_aliases": ["volkswagen", "vw"],
    },
    "AU": {
        "brand": "Audi",
        "source_name": "AudiPartsInfo",
        "source_domain": "parts.audi.de",
        "sitemap": "https://parts.audi.de/sitemap.xml",
        "brand_aliases": ["audi"],
    },
    "SK": {
        "brand": "Skoda",
        "source_name": "SkodaPartsInfo",
        "source_domain": "parts.skoda.de",
        "sitemap": "https://parts.skoda.de/sitemap.xml",
        "brand_aliases": ["skoda"],
    },
    "SE": {
        "brand": "Seat",
        "source_name": "SeatPartsInfo",
        "source_domain": "parts.seat.de",
        "sitemap": "https://parts.seat.de/sitemap.xml",
        "brand_aliases": ["seat"],
    },
    "MB": {
        "brand": "Mercedes-Benz",
        "source_name": "MercedesPartsInfo",
        "source_domain": "parts.mercedes-benz.de",
        "sitemap": "https://parts.mercedes-benz.de/sitemap.xml",
        "brand_aliases": ["mercedes", "mercedes-benz", "benz"],
    },
}


class ProxyRotator:
    def __init__(self, entries: list[tuple[str, str]], prefer_proxy: bool = False):
        self.entries = entries
        self.prefer_proxy = prefer_proxy
        self._idx = 0

    def sequence(self) -> list[tuple[str, str | None]]:
        if not self.entries:
            return [("direct", None)]

        n = len(self.entries)
        ordered = [self.entries[(self._idx + i) % n] for i in range(n)]
        self._idx = (self._idx + 1) % n

        proxies = [(region or "proxy", proxy) for region, proxy in ordered]
        if self.prefer_proxy:
            return proxies + [("direct", None)]
        return [("direct", None)] + proxies


def normalize_proxy_url(proxy: str) -> str:
    proxy = proxy.strip()
    if not proxy:
        return ""
    if not proxy.startswith("http://") and not proxy.startswith("https://"):
        return f"http://{proxy}"
    return proxy


def load_proxy_entries(proxy_file: str, proxies_inline: str, regions_filter: set[str]) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []

    if proxy_file:
        path = Path(proxy_file)
        if path.exists():
            for raw in path.read_text(encoding="utf-8").splitlines():
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                region = ""
                proxy = line
                if "|" in line:
                    region, proxy = [x.strip() for x in line.split("|", 1)]
                proxy_url = normalize_proxy_url(proxy)
                if proxy_url:
                    entries.append((region.upper(), proxy_url))

    if proxies_inline:
        for item in proxies_inline.split(","):
            proxy_url = normalize_proxy_url(item)
            if proxy_url:
                entries.append(("", proxy_url))

    if regions_filter:
        entries = [item for item in entries if (item[0] or "").upper() in regions_filter]

    deduped: dict[str, tuple[str, str]] = {}
    for region, proxy in entries:
        deduped[proxy] = (region, proxy)
    return list(deduped.values())


def session_get(
    session: requests.Session,
    url: str,
    timeout: int,
    verify_ssl: bool,
    rotator: ProxyRotator,
) -> requests.Response:
    last_exc: Exception | None = None
    for _label, proxy in rotator.sequence():
        try:
            proxy_dict = {"http": proxy, "https": proxy} if proxy else None
            response = session.get(url, timeout=timeout, verify=verify_ssl, proxies=proxy_dict)
            if response.status_code < 500:
                return response
        except requests.RequestException as exc:
            last_exc = exc
            continue

    if last_exc:
        raise last_exc
    raise requests.RequestException(f"Failed to fetch {url}")


RULES = {
    "CKP": {
        "seed_terms": ["crankshaft", "crank", "sensor", "angle"],
        "match_groups": [("crankshaft", "sensor"), ("crank angle", "sensor"), ("crank sensor",)],
        "exclude_terms": ["connector", "harness", "clip", "bracket", "stay", "holder", "passage", "spacer", "sub harness", "sub wire", "wire", "cover", "gasket"],
    },
    "CMP": {
        "seed_terms": ["camshaft", "cam", "sensor"],
        "match_groups": [("camshaft", "sensor"), ("cam position", "sensor"), ("cam sensor",)],
        "exclude_terms": ["connector", "harness", "clip", "bracket", "stay", "holder", "passage", "spacer", "sub harness", "sub wire", "wire", "cover", "gasket"],
    },
    "OPS": {
        "seed_terms": ["oil", "pressure", "switch", "sensor"],
        "match_groups": [("oil pressure switch",), ("oil pressure sensor",), ("pressure switch", "oil")],
        "exclude_terms": ["connector", "harness", "clip", "bracket", "stay", "holder", "passage", "spacer", "sub harness", "cover", "insulator", "hose", "bolt", "gasket"],
    },
    "MAP": {
        "seed_terms": ["map", "manifold", "absolute", "pressure", "sensor"],
        "match_groups": [("map sensor",), ("manifold absolute pressure sensor",)],
        "exclude_terms": ["connector", "harness", "clip", "bracket", "stay", "holder", "spacer", "joint", "cover", "insulator", "hose", "bolt", "gasket"],
    },
    "ODW": {
        "seed_terms": ["drain", "washer", "gasket", "plug"],
        "match_groups": [("drain plug washer",), ("drain plug gasket",), ("oil drain plug washer",), ("washer", "drain plug")],
        "exclude_terms": ["bolt", "screw"],
    },
    "ODP": {
        "seed_terms": ["drain", "plug", "oil", "pan"],
        "match_groups": [("oil drain plug",), ("drain plug", "oil"), ("plug", "drain", "oil")],
        "exclude_terms": ["washer", "gasket", "bolt washer"],
    },
    "IMG": {
        "seed_terms": ["intake", "manifold", "gasket"],
        "match_groups": [("intake manifold gasket",), ("gasket", "intake manifold")],
        "exclude_terms": [],
    },
    "EMG": {
        "seed_terms": ["exhaust", "manifold", "gasket"],
        "match_groups": [("exhaust manifold gasket",), ("gasket", "exhaust manifold")],
        "exclude_terms": [],
    },
    "HGG": {
        "seed_terms": ["head", "gasket", "cylinder"],
        "match_groups": [("head gasket",), ("cylinder head gasket",)],
        "exclude_terms": [],
    },
    "SBF": {
        "seed_terms": ["stabilizer", "sway", "bushing", "front"],
        "match_groups": [("front stabilizer bushing",), ("front sway bar bushing",), ("bushing", "front stabilizer")],
        "exclude_terms": ["link", "bar", "shaft"],
    },
    "SBR": {
        "seed_terms": ["stabilizer", "sway", "bushing", "rear"],
        "match_groups": [("rear stabilizer bushing",), ("rear sway bar bushing",), ("bushing", "rear stabilizer")],
        "exclude_terms": ["link", "bar", "shaft"],
    },
    "RAB": {
        "seed_terms": ["rear", "arm", "bushing", "control"],
        "match_groups": [("rear arm bushing",), ("rear control arm bushing",), ("bushing", "rear", "arm")],
        "exclude_terms": ["front", "link", "shaft"],
    },
    "CVB": {
        "seed_terms": ["boot", "joint", "cv", "shaft"],
        "match_groups": [("cv joint boot",), ("cv", "boot"), ("drive shaft boot",), ("driveshaft", "boot")],
        "exclude_terms": ["band", "clip", "clamp", "ball joint", "tie rod", "rack"],
    },
}


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", value.lower())).strip()


def load_worklist(path: Path) -> dict[str, set[str]]:
    unresolved: dict[str, set[str]] = defaultdict(set)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            prefix = str(row.get("brand_prefix") or "").strip().upper()
            code = str(row.get("part_code") or "").strip().upper()
            if prefix in SITE_CONFIGS and code in RULES:
                unresolved[prefix].add(code)
    return unresolved


def list_partsinfo_sitemaps(
    session: requests.Session,
    sitemap_url: str,
    verify_ssl: bool,
    rotator: ProxyRotator,
) -> list[str]:
    xml_text = session_get(session, sitemap_url, REQUEST_TIMEOUT_SHORT, verify_ssl, rotator).text
    root = ET.fromstring(xml_text)
    locs = [el.text.strip() for el in root.iter() if el.tag.endswith("loc") and el.text]
    return [loc for loc in locs if "sitemap_partsinfo" in loc.lower()]


def iter_urls_from_sitemap(
    session: requests.Session,
    sitemap_url: str,
    verify_ssl: bool,
    rotator: ProxyRotator,
) -> list[str]:
    data = gzip.decompress(session_get(session, sitemap_url, REQUEST_TIMEOUT_LONG, verify_ssl, rotator).content)
    root = ET.fromstring(data)
    return [el.text.strip() for el in root.iter() if el.tag.endswith("loc") and el.text]


def classify_code(text: str, target_codes: set[str]) -> str:
    normalized = normalize_text(text)
    for code in sorted(target_codes):
        if any(term in normalized for term in RULES[code].get("exclude_terms", [])):
            continue
        for group in RULES[code]["match_groups"]:
            if all(term in normalized for term in group):
                return code
    return ""


def looks_relevant(url: str, target_codes: set[str]) -> bool:
    return bool(classify_code(url, target_codes))


def extract_spec_table(soup: BeautifulSoup) -> dict[str, str]:
    specs: dict[str, str] = {}
    for row in soup.find_all("tr"):
        cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"])]
        if len(cells) >= 2:
            key = cells[0]
            value = cells[1]
            if key and value and key not in specs:
                specs[key] = value
    return specs


def parse_fitment(soup: BeautifulSoup, brand: str) -> dict[str, str]:
    heading = next((tag for tag in soup.find_all(["h2", "h3"]) if "vehicle fitment" in tag.get_text(" ", strip=True).lower()), None)
    if heading is None:
        return {"model": "", "year_from": "", "year_to": "", "engine": ""}

    table = heading.find_next("table")
    if table is None:
        return {"model": "", "year_from": "", "year_to": "", "engine": ""}

    models: list[str] = []
    engines: list[str] = []
    year_from = None
    year_to = None
    for row in table.find_all("tr")[:25]:
        cells = [cell.get_text(" ", strip=True) for cell in row.find_all("td")]
        if not cells:
            continue
        first = cells[0]
        match = re.match(r"(?P<start>\d{4})(?:-(?P<end>\d{4}))?\s+" + re.escape(brand) + r"\s+(?P<model>.+)", first)
        if match:
            start = int(match.group("start"))
            end = int(match.group("end") or match.group("start"))
            model = match.group("model").strip()
            if model and model not in models:
                models.append(model)
            year_from = start if year_from is None else min(year_from, start)
            year_to = end if year_to is None else max(year_to, end)
        if len(cells) >= 3:
            engine = cells[2].strip()
            if engine and engine not in engines:
                engines.append(engine)
    return {
        "model": "; ".join(models[:4]),
        "year_from": str(year_from or ""),
        "year_to": str(year_to or ""),
        "engine": "; ".join(engines[:4]),
    }


def extract_fitment_brands(soup: BeautifulSoup) -> set[str]:
    brands: set[str] = set()
    heading = next((tag for tag in soup.find_all(["h2", "h3"]) if "vehicle fitment" in tag.get_text(" ", strip=True).lower()), None)
    if heading is None:
        return brands
    table = heading.find_next("table")
    if table is None:
        return brands
    for row in table.find_all("tr")[:30]:
        cells = [cell.get_text(" ", strip=True) for cell in row.find_all("td")]
        if not cells:
            continue
        first = cells[0]
        m = re.match(r"\d{4}(?:-\d{4})?\s+([A-Za-z\-]+)", first)
        if m:
            brands.add(m.group(1).lower())
    return brands


def page_matches_brand(config: dict[str, Any], soup: BeautifulSoup, title: str, part_description: str) -> bool:
    aliases = [alias.lower() for alias in config.get("brand_aliases", [config["brand"]])]
    text = normalize_text(" ".join([title, part_description]))
    fitment_brands = extract_fitment_brands(soup)

    if fitment_brands and not any(alias in fitment_brands for alias in aliases):
        return False

    if any(alias in text for alias in aliases):
        return True

    if fitment_brands:
        return any(alias in fitment_brands for alias in aliases)

    return False


def parse_oem_from_url(url: str) -> str:
    stem = url.rsplit("/", 1)[-1].split(".html", 1)[0]
    token = stem.rsplit("~", 1)[-1]
    return token.upper()


def fetch_row(
    session: requests.Session,
    prefix: str,
    url: str,
    target_codes: set[str],
    verify_ssl: bool,
    rotator: ProxyRotator,
) -> dict[str, str] | None:
    config = SITE_CONFIGS[prefix]
    response = session_get(session, url, REQUEST_TIMEOUT_SHORT, verify_ssl, rotator)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    title_tag = soup.find("h1")
    title = title_tag.get_text(" ", strip=True) if title_tag else ""
    specs = extract_spec_table(soup)
    part_description = specs.get("Part Description", "")
    if not page_matches_brand(config, soup, title, part_description):
        return None
    code = classify_code(" ".join([title, part_description]), target_codes)
    if not code:
        return None

    oem_number = specs.get("Manufacturer Part Number", "") or parse_oem_from_url(url)
    if not oem_number:
        return None

    fitment = parse_fitment(soup, config["brand"])
    return {
        "brand_prefix": prefix,
        "part_code": code,
        "oem_number": oem_number,
        "source_name": config["source_name"],
        "source_url": url,
        "retrieved_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "brand": config["brand"],
        "model": fitment["model"],
        "year_from": fitment["year_from"],
        "year_to": fitment["year_to"],
        "engine": fitment["engine"],
        "restyle": "",
        "vin_pattern": "",
    }


def import_site(
    prefix: str,
    session: requests.Session,
    unresolved_codes: set[str],
    max_pages: int,
    verify_ssl: bool,
    rotator: ProxyRotator,
) -> list[dict[str, str]]:
    config = SITE_CONFIGS[prefix]
    results: dict[tuple[str, str, str], dict[str, str]] = {}

    candidate_urls_by_code: dict[str, list[str]] = defaultdict(list)
    try:
        sitemap_urls = list_partsinfo_sitemaps(session, config["sitemap"], verify_ssl, rotator)
    except (requests.RequestException, ET.ParseError, gzip.BadGzipFile, OSError) as exc:
        print(f"brand={prefix} sitemap_error={type(exc).__name__}")
        return []

    for sitemap_url in sitemap_urls:
        try:
            urls = iter_urls_from_sitemap(session, sitemap_url, verify_ssl, rotator)
        except (requests.RequestException, ET.ParseError, gzip.BadGzipFile, OSError):
            continue
        for url in urls:
            code = classify_code(url, unresolved_codes)
            if code:
                candidate_urls_by_code[code].append(url)
        if sum(len(urls) for urls in candidate_urls_by_code.values()) >= max_pages * 12:
            break

    code_queue = deque(sorted(candidate_urls_by_code))
    idx_by_code = {code: 0 for code in candidate_urls_by_code}
    ordered_candidates: list[str] = []
    while code_queue and len(ordered_candidates) < max_pages * 8:
        code = code_queue.popleft()
        idx = idx_by_code[code]
        urls = candidate_urls_by_code[code]
        if idx < len(urls):
            ordered_candidates.append(urls[idx])
            idx_by_code[code] = idx + 1
            if idx + 1 < len(urls):
                code_queue.append(code)

    for url in ordered_candidates:
        try:
            row = fetch_row(session, prefix, url, unresolved_codes, verify_ssl, rotator)
        except (requests.RequestException, ET.ParseError, ValueError):
            continue
        if row is None:
            continue
        key = (row["brand_prefix"], row["part_code"], row["oem_number"])
        results.setdefault(key, row)
        if len(results) >= max_pages:
            break

    return sorted(results.values(), key=lambda row: (row["part_code"], row["oem_number"]))


def main() -> None:
    parser = argparse.ArgumentParser(description="Import exact OEM rows from official brand parts sites")
    parser.add_argument("--brands", default="BM,AC,HO,TY,LX,HY,KI,NI,FO,SU,CH,GM,CA,BU,CR,DG,JP,VW,AU,SK,SE,MB", help="Comma-separated brand prefixes to import")
    parser.add_argument("--max-pages-per-brand", type=int, default=250, help="Maximum accepted OEM pages per brand")
    parser.add_argument("--skip-ssl", action="store_true", help="Disable SSL verification")
    parser.add_argument("--proxy-file", default="", help="Proxy list file (one per line, optional format REGION|host:port)")
    parser.add_argument("--proxies", default="", help="Comma-separated proxy URLs/hosts")
    parser.add_argument("--regions", default="", help="Comma-separated region tags to filter proxy file entries")
    parser.add_argument("--prefer-proxy", action="store_true", help="Try proxies before direct connection")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output CSV path")
    args = parser.parse_args()

    requested = [item.strip().upper() for item in args.brands.split(",") if item.strip()]
    unresolved = load_worklist(WORKLIST)
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    verify_ssl = not args.skip_ssl
    regions_filter = {item.strip().upper() for item in args.regions.split(",") if item.strip()}
    proxies = load_proxy_entries(args.proxy_file, args.proxies, regions_filter)
    rotator = ProxyRotator(proxies, prefer_proxy=args.prefer_proxy)

    print(f"ssl_verify={verify_ssl}")
    print(f"proxy_count={len(proxies)}")

    rows: list[dict[str, str]] = []
    for prefix in requested:
        if prefix not in SITE_CONFIGS:
            continue
        target_codes = unresolved.get(prefix, set())
        target_codes &= set(RULES)
        if not target_codes:
            continue
        imported = import_site(prefix, session, target_codes, args.max_pages_per_brand, verify_ssl, rotator)
        print(f"brand={prefix} imported={len(imported)} target_codes={','.join(sorted(target_codes))}")
        rows.extend(imported)

    deduped: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in rows:
        deduped[(row["brand_prefix"], row["part_code"], row["oem_number"])] = row

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "brand_prefix", "part_code", "oem_number", "source_name", "source_url", "retrieved_at",
                "brand", "model", "year_from", "year_to", "engine", "restyle", "vin_pattern",
            ],
        )
        writer.writeheader()
        writer.writerows(sorted(deduped.values(), key=lambda row: (row["brand_prefix"], row["part_code"], row["oem_number"])))

    print(f"rows={len(deduped)} output={output}")


if __name__ == "__main__":
    main()