#!/usr/bin/env python3
"""Enrich AutoScout24 records with exact engine displacement from detail pages."""

import argparse
import json
import os
import random
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path
from typing import Any, Optional

import requests
from bs4 import BeautifulSoup


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
)


class RateLimiter:
    def __init__(self, requests_per_second: float):
        self.interval = 1 / max(requests_per_second, 0.1)
        self.lock = threading.Lock()
        self.next_request_at = 0.0

    def wait(self) -> None:
        with self.lock:
            now = time.monotonic()
            delay = max(0.0, self.next_request_at - now)
            self.next_request_at = max(now, self.next_request_at) + self.interval
        if delay:
            time.sleep(delay)

    def penalize(self, seconds: float) -> None:
        with self.lock:
            self.next_request_at = max(
                self.next_request_at,
                time.monotonic() + max(0.0, seconds),
            )


def nested_get(value: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def parse_cc_value(value: Any) -> int:
    if isinstance(value, dict):
        for key in ("raw", "value"):
            cc = parse_cc_value(value.get(key))
            if cc:
                return cc
        return 0
    if isinstance(value, (int, float)):
        cc = int(round(value))
    else:
        digits = re.sub(r"\D", "", str(value or ""))
        cc = int(digits) if digits else 0
    return cc if 500 <= cc <= 10000 else 0


def find_numeric_key(value: Any, keys: set[str]) -> int:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in keys:
                cc = parse_cc_value(child)
                if cc:
                    return cc
            cc = find_numeric_key(child, keys)
            if cc:
                return cc
    elif isinstance(value, list):
        for child in value:
            cc = find_numeric_key(child, keys)
            if cc:
                return cc
    return 0


def parse_json_ld_displacement(soup: BeautifulSoup) -> int:
    for script in soup.find_all("script", type="application/ld+json"):
        text = script.string or script.get_text() or ""
        try:
            payload = json.loads(text)
        except (TypeError, json.JSONDecodeError):
            continue
        nodes = payload if isinstance(payload, list) else [payload]
        for node in nodes:
            if not isinstance(node, dict):
                continue
            vehicle = node.get("offers", {}).get("itemOffered") or node
            engines = vehicle.get("vehicleEngine") or []
            if isinstance(engines, dict):
                engines = [engines]
            for engine in engines:
                displacement = nested_get(engine, "engineDisplacement", "value")
                cc = parse_cc_value(displacement)
                if cc:
                    return cc
    return 0


def parse_next_data_displacement(soup: BeautifulSoup) -> int:
    script = soup.find("script", id="__NEXT_DATA__")
    if not script or not script.string:
        return 0
    try:
        payload = json.loads(script.string)
    except json.JSONDecodeError:
        return 0
    vehicle = nested_get(payload, "props", "pageProps", "listingDetails", "vehicle") or {}
    candidates = [
        vehicle.get("rawDisplacementInCCM"),
        vehicle.get("rawCylinderCapacity"),
        nested_get(vehicle, "rawData", "engine", "cylinderCapacity", "raw"),
    ]
    for candidate in candidates:
        cc = parse_cc_value(candidate)
        if cc:
            return cc
    return find_numeric_key(
        vehicle,
        {"rawDisplacementInCCM", "rawCylinderCapacity", "cylinderCapacity"},
    )


def parse_visible_displacement(html: str) -> int:
    patterns = [
        r'"rawDisplacementInCCM"\s*:\s*(\d{3,5})',
        r'"rawCylinderCapacity"\s*:\s*(\d{3,5})',
        r'"engineDisplacement".{0,180}?"value"\s*:\s*(\d{3,5})',
        r"(?:Hubraum|рабочий объ[её]м двигателя).{0,100}?(\d[\d.\s]{2,8})\s*cm",
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.I | re.S)
        if not match:
            continue
        cc = int(re.sub(r"\D", "", match.group(1)) or 0)
        if 500 <= cc <= 10000:
            return cc
    return 0


def fetch_displacement(
    url: str,
    timeout: float,
    limiter: RateLimiter,
    retries: int,
) -> tuple[int, str]:
    response = None
    for attempt in range(max(1, retries)):
        limiter.wait()
        response = requests.get(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "de-DE,de;q=0.9,en;q=0.7",
                "Referer": "https://www.autoscout24.de/",
            },
            timeout=timeout,
        )
        if response.status_code not in {429, 500, 502, 503, 504}:
            response.raise_for_status()
            break
        if response.status_code == 429:
            limiter.penalize(min(60, 8 * (attempt + 1)))
        if attempt + 1 < retries:
            time.sleep((2 ** attempt) + random.uniform(0.2, 0.8))
    if response is None:
        return 0, ""
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    cc = parse_next_data_displacement(soup)
    if cc:
        return cc, "autoscout24_detail_next_data"
    cc = parse_json_ld_displacement(soup)
    if cc:
        return cc, "autoscout24_detail_json_ld"
    cc = parse_visible_displacement(response.text)
    return (cc, "autoscout24_detail_html") if cc else (0, "")


def format_liters(cc: int) -> str:
    return f"{cc / 1000:.3f}".rstrip("0").rstrip(".").replace(".", ",")


def save_records(path: Path, records: list[dict]) -> None:
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for attempt in range(6):
        try:
            os.replace(temp_path, path)
            return
        except PermissionError:
            if attempt == 5:
                raise
            time.sleep(0.5 * (attempt + 1))


def should_enrich(record: dict, refresh: bool) -> bool:
    url = str(record.get("url") or "")
    if "autoscout24." not in url:
        return False
    if refresh:
        return True
    return not (
        record.get("engine_cc")
        and str(record.get("engine_source") or "").startswith("autoscout24_")
    )


def home_feature_target(record: dict) -> int:
    mileage = float(record.get("mileage") or 0)
    images = record.get("images") if isinstance(record.get("images"), list) else []
    if not (0 < mileage <= 100000) or not images or not float(record.get("price") or 0):
        return -1
    brand = re.sub(r"[^a-z0-9]", "", str(record.get("brand") or "").lower())
    model = f"{record.get('model') or ''} {record.get('full_title') or ''}"
    targets = (
        ("audi", r"(?:^|\s)a4(?:\s|$)"),
        ("bmw", r"(?:^|\s)(?:3|3er|3[\s-]?series|31[68][di]?|32\d[di]?|33\d[di]?|34\d[di]?)(?:\s|$)"),
        ("mercedesbenz", r"(?:^|\s)gla(?:\s|$)"),
        ("volkswagen", r"(?:^|\s)arteon(?:\s|$)"),
    )
    for index, (target_brand, pattern) in enumerate(targets):
        if brand == target_brand and re.search(pattern, model, re.I):
            return index
    return -1


def prioritize_candidates(candidates: list[tuple[int, dict]]) -> list[tuple[int, dict]]:
    buckets = [[] for _ in range(4)]
    remaining = []
    for candidate in candidates:
        target = home_feature_target(candidate[1])
        (buckets[target] if target >= 0 else remaining).append(candidate)
    for bucket in buckets:
        bucket.sort(key=lambda item: float(item[1].get("price") or float("inf")))

    prioritized = []
    for offset in range(12):
        for bucket in buckets:
            if offset < len(bucket):
                prioritized.append(bucket[offset])
    selected = {index for index, _ in prioritized}
    prioritized.extend(
        candidate for bucket in buckets for candidate in bucket if candidate[0] not in selected
    )
    prioritized.extend(remaining)
    return prioritized


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="cars_europe_new.json")
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--timeout", type=float, default=12)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--checkpoint-every", type=int, default=25)
    parser.add_argument("--requests-per-second", type=float, default=3)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()

    path = Path(args.input)
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    records = payload if isinstance(payload, list) else [payload]
    candidates = prioritize_candidates([
        (index, item)
        for index, item in enumerate(records)
        if should_enrich(item, args.refresh)
    ])
    if args.limit:
        candidates = candidates[: args.limit]

    updated = 0
    failed = 0
    started = time.time()
    limiter = RateLimiter(args.requests_per_second)
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {
            executor.submit(
                fetch_displacement,
                str(item.get("url")),
                args.timeout,
                limiter,
                args.retries,
            ): index
            for index, item in candidates
        }
        for future in as_completed(futures):
            index = futures[future]
            try:
                cc, source = future.result()
            except Exception:
                failed += 1
                continue
            if not cc:
                failed += 1
                continue
            records[index]["engine_cc"] = cc
            records[index]["engine"] = format_liters(cc)
            records[index]["engine_source"] = source
            records[index]["engine_verified_at"] = date.today().isoformat()
            updated += 1
            if args.checkpoint_every and updated % args.checkpoint_every == 0:
                save_records(path, records)

    save_records(path, records)
    print(
        f"AutoScout24 engine enrichment: {updated}/{len(candidates)} updated, "
        f"{failed} unavailable, {time.time() - started:.1f}s"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
