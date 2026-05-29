#!/usr/bin/env python3
"""Fetch Avtostok63 premium stock from Carexpo catalog page."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = "https://carexpo.group/catalog?status=in_stock&page=5"
OUTPUT = ROOT / "data" / "avtostok63_premium.json"


def text(value: Any) -> str:
    return str(value or "").strip()


def dict_title(value: Any) -> str:
    if isinstance(value, dict):
        return text(value.get("title"))
    return text(value)


def image_url(image: Any) -> str:
    if isinstance(image, str):
        return image
    if not isinstance(image, dict):
        return ""

    for device in ("desktop", "tablet", "mobile"):
        item = image.get(device)
        if isinstance(item, dict):
            for key in ("x2", "x1", "webp_x2", "webp_x1"):
                if item.get(key):
                    return text(item[key])
    return ""


def extract_next_data(html: str) -> dict[str, Any]:
    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        html,
        flags=re.S,
    )
    if not match:
        raise RuntimeError("Carexpo __NEXT_DATA__ block not found")
    return json.loads(match.group(1))


def cars_from_next_data(data: dict[str, Any]) -> list[dict[str, Any]]:
    cached = (
        data.get("props", {})
        .get("pageProps", {})
        .get("initialState", {})
        .get("catalog", {})
        .get("carsList", {})
        .get("cached", {})
    )
    page = cached.get("status=in_stock&page=5")
    if not page or not isinstance(page.get("data"), list):
        raise RuntimeError("Carexpo page 5 stock data not found")
    return page["data"]


def normalize(car: dict[str, Any]) -> dict[str, Any]:
    brand = dict_title(car.get("brand")) or text(car.get("make"))
    model = dict_title(car.get("model"))
    generation = dict_title(car.get("model_generation"))
    configuration = dict_title(car.get("configuration"))
    images = [image_url(item) for item in car.get("images") or []]
    images = [url for url in images if url]

    details = [
        value
        for value in (model, generation, configuration, text(car.get("short_features")))
        if value
    ]
    title = " ".join(details) or "Новый автомобиль"

    location = dict_title(car.get("location")) or dict_title(car.get("country")) or "В наличии"
    price = car.get("eur_price") or car.get("published_price") or 0

    return {
        "id": f"carexpo-{car.get('id')}",
        "source_id": car.get("id"),
        "brand": brand,
        "model": model,
        "title": title,
        "year": car.get("production_year"),
        "condition": text(car.get("condition")) or "New",
        "status": text(car.get("status")) or "In Stock",
        "price_eur": price,
        "otd_price_eur": car.get("otd_price") or 0,
        "currency": car.get("currency") or "€",
        "mileage": car.get("mileage") or 0,
        "fuel_type": text(car.get("fuel_type")),
        "transmission": text(car.get("transmission")),
        "power_hp": car.get("power_hp"),
        "location": location,
        "images": images,
        "url": f"https://carexpo.group/catalog?carId={car.get('id')}",
    }


def fetch() -> dict[str, Any]:
    response = requests.get(
        SOURCE_URL,
        headers={
            "User-Agent": "Mozilla/5.0 Avtostok63 premium catalog updater",
            "Accept": "text/html,application/xhtml+xml",
        },
        timeout=35,
    )
    response.raise_for_status()
    data = extract_next_data(response.text)
    cars = [normalize(car) for car in cars_from_next_data(data)]
    cars = [car for car in cars if car["brand"] and car["images"]]
    return {
        "source": SOURCE_URL,
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "cars": cars,
    }


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    payload = fetch()
    OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(payload['cars'])} premium cars to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
