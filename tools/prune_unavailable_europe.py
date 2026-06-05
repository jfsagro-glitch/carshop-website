#!/usr/bin/env python3
"""
Remove unavailable Europe listings from cars_europe_new.json.

The parser can keep URLs that later become inactive on AutoScout24/mobile.de.
This script checks listing pages and removes only listings that clearly resolve
to a "no longer available" page. Network errors are kept by default, so a
temporary block does not wipe the catalog.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

UNAVAILABLE_PATTERNS = [
    r"fahrzeug\s+(?:ist\s+)?(?:leider\s+)?nicht\s+mehr\s+verf(?:ü|ue)gbar",
    r"dieses\s+fahrzeug\s+ist\s+nicht\s+mehr\s+verf(?:ü|ue)gbar",
    r"dieses\s+angebot\s+ist\s+nicht\s+mehr\s+verf(?:ü|ue)gbar",
    r"angebot\s+(?:ist\s+)?(?:leider\s+)?nicht\s+mehr\s+verf(?:ü|ue)gbar",
    r"vehicle\s+(?:is\s+)?no\s+longer\s+available",
    r"listing\s+(?:is\s+)?no\s+longer\s+available",
    r"this\s+car\s+is\s+no\s+longer\s+available",
    r"this\s+vehicle\s+is\s+no\s+longer\s+available",
    r"к\s+сожалению[^.]{0,120}(?:автомобиль|объявление)[^.]{0,120}(?:больше\s+не|недоступ)",
    r"этот\s+автомобиль\s+больше\s+не",
]

AVAILABLE_HINTS = [
    r"seller",
    r"anbieter",
    r"kontakt",
    r"fahrzeugdetails",
    r"mileage",
    r"kilometerstand",
    r"first\s+registration",
    r"erstzulassung",
]


@dataclass
class CheckResult:
    index: int
    status: str
    url: str
    reason: str = ""


def normalize_html(text: str) -> str:
    text = re.sub(r"<script\b[^>]*>.*?</script>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.lower()


def looks_unavailable(html: str) -> str:
    normalized = normalize_html(html)
    for pattern in UNAVAILABLE_PATTERNS:
        if re.search(pattern, normalized, flags=re.I):
            return pattern
    return ""


def has_available_hint(html: str) -> bool:
    normalized = normalize_html(html)
    return any(re.search(pattern, normalized, flags=re.I) for pattern in AVAILABLE_HINTS)


def check_listing(index: int, car: dict[str, Any], timeout: float) -> CheckResult:
    url = str(car.get("url") or "").strip()
    if not url.startswith(("http://", "https://")):
        return CheckResult(index, "keep", url, "missing-url")

    headers = {
        "User-Agent": USER_AGENT,
        "Accept-Language": "de-DE,de;q=0.9,en;q=0.8,ru;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True, stream=True)
    except requests.RequestException as exc:
        return CheckResult(index, "keep", url, f"network-error:{exc.__class__.__name__}")

    final_url = response.url.lower()
    if response.status_code in (404, 410):
        response.close()
        return CheckResult(index, "remove", url, f"http-{response.status_code}")
    if response.status_code >= 500:
        response.close()
        return CheckResult(index, "keep", url, f"http-{response.status_code}")
    if response.status_code == 200 and "autoscout24" in final_url and "/angebote/" in final_url:
        response.close()
        return CheckResult(index, "keep", url, "http-200")

    html = response.text or ""
    response.close()
    unavailable_reason = looks_unavailable(html)
    if unavailable_reason:
        return CheckResult(index, "remove", url, f"unavailable:{unavailable_reason}")

    if "autoscout24" in final_url and any(part in final_url for part in ("/lst", "/angebote?", "/auto/")):
        if not has_available_hint(html):
            return CheckResult(index, "keep", url, "uncertain-autoscout-page")

    return CheckResult(index, "keep", url, f"http-{response.status_code}")


def prune_catalog(path: Path, workers: int, timeout: float, limit: int, dry_run: bool) -> int:
    cars = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(cars, list):
        raise SystemExit(f"{path} must contain a JSON array")

    indexed = list(enumerate(cars))
    if limit > 0:
        indexed = indexed[:limit]

    started = time.time()
    print(f"Checking {len(indexed)} Europe listings from {path} with {workers} workers...")

    results: list[CheckResult] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(check_listing, index, car, timeout) for index, car in indexed]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            if result.status == "remove":
                print(f"REMOVE #{result.index}: {result.url} ({result.reason})")

    remove_indexes = {result.index for result in results if result.status == "remove"}
    kept = [car for index, car in enumerate(cars) if index not in remove_indexes]

    print(
        f"Checked {len(indexed)} listings in {time.time() - started:.1f}s. "
        f"Removed {len(remove_indexes)} unavailable listings. Kept {len(kept)}."
    )

    if remove_indexes and not dry_run:
        path.write_text(json.dumps(kept, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return len(remove_indexes)


def main() -> int:
    parser = argparse.ArgumentParser(description="Remove unavailable Europe listings")
    parser.add_argument("--input", default="cars_europe_new.json", help="Path to Europe JSON catalog")
    parser.add_argument("--workers", type=int, default=10, help="Parallel HTTP checks")
    parser.add_argument("--timeout", type=float, default=12.0, help="HTTP timeout per listing")
    parser.add_argument("--limit", type=int, default=0, help="Check only first N rows, 0 means all")
    parser.add_argument("--dry-run", action="store_true", help="Report removals without writing JSON")
    args = parser.parse_args()

    removed = prune_catalog(
        path=Path(args.input),
        workers=max(1, args.workers),
        timeout=max(2.0, args.timeout),
        limit=max(0, args.limit),
        dry_run=args.dry_run,
    )
    return 0 if removed >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())
