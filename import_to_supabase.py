#!/usr/bin/env python3
"""
Import generated car data from JSON files into Supabase.
Replaces existing data for each source with the new generated cars.
Usage: python import_to_supabase.py [--dry-run]
"""
import json
import sys
import os
import requests
from datetime import datetime, timezone

SUPABASE_URL = "https://jolyujjfxzhkswflqodz.supabase.co"
SUPABASE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpvbHl1ampmeHpoa3N3Zmxxb2R6Iiwi"
    "cm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3Nzg0NDU2MSwiZXhwIjoyMDkzND"
    "IwNTYxfQ.Ex7h9hdsXba1fWcoqx3CSlImdrXTw7IVn5bsFsAM1j8"
)
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates,return=minimal",
}
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
DRY_RUN = "--dry-run" in sys.argv

def _float(v):
    try:
        return float(str(v).replace(",", ".")) if v else None
    except (ValueError, TypeError):
        return None


def korea_to_row(r: dict) -> dict:
    url = r.get("url") or ""
    eid = r.get("external_id") or url or f"encar:{r.get('id', '')}"
    specs = {}
    if r.get("drive"):
        specs["drive"] = r["drive"]
    if r.get("productionDate"):
        specs["productionDate"] = r["productionDate"]
    return {
        "external_id": eid,
        "source": r.get("source") or "encar",
        "region": "korea",
        "brand": r.get("brand"),
        "model": r.get("model"),
        "year": r.get("year"),
        "price": r.get("price"),
        "currency": r.get("currency") or "USD",
        "mileage": r.get("mileage"),
        "engine": _float(r.get("engine")),
        "fuel_type": r.get("fuel_type"),
        "transmission": r.get("transmission"),
        "color": r.get("color"),
        "drive": r.get("drive"),
        "power_hp": r.get("power_hp"),
        "power_kw": r.get("power_kw"),
        "vin": None,
        "url": url,
        "images": r.get("images") or [],
        "specs": specs,
        "is_active": True,
        "last_seen": NOW,
    }


def europe_to_row(r: dict) -> dict:
    url = r.get("url") or ""
    eid = r.get("external_id") or url or f"autoscout24:{r.get('id', '')}"
    # For images: generated cars have [url_string], real cars have [{url,order}]
    imgs = r.get("images") or []
    if imgs and isinstance(imgs[0], dict):
        imgs = [i["url"] for i in imgs if i.get("url")]
    specs = {}
    for k in ("drive", "country", "color", "first_registration"):
        if r.get(k):
            specs[k] = r[k]
    return {
        "external_id": eid,
        "source": r.get("source") or "autoscout24",
        "region": "europe",
        "brand": r.get("brand"),
        "model": r.get("model"),
        "year": r.get("year") or r.get("first_registration_year"),
        "price": r.get("price"),
        "currency": r.get("currency") or "EUR",
        "mileage": r.get("mileage"),
        "engine": _float(r.get("engine")),
        "fuel_type": r.get("fuel_type"),
        "transmission": r.get("transmission"),
        "color": r.get("color"),
        "drive": r.get("drive"),
        "power_hp": r.get("power_hp"),
        "power_kw": r.get("power_kw"),
        "vin": r.get("vin") or None,
        "url": url,
        "images": imgs,
        "specs": specs,
        "is_active": True,
        "last_seen": NOW,
    }


def georgia_to_row(r: dict) -> dict:
    url = r.get("url") or r.get("description") or ""
    eid = r.get("external_id") or f"myauto_ge:{r.get('id', '')}"
    photos = r.get("photos")
    images = r.get("images") or (
        [photos] if photos and isinstance(photos, str) else
        photos if isinstance(photos, list) else []
    )
    return {
        "external_id": eid,
        "source": r.get("source") or "myauto_ge",
        "region": "georgia",
        "brand": r.get("brand"),
        "model": r.get("model"),
        "year": r.get("year"),
        "price": r.get("price"),
        "currency": "USD",
        "mileage": r.get("mileage"),
        "engine": _float(r.get("engine")),
        "fuel_type": r.get("fuel_type"),
        "transmission": r.get("transmission"),
        "color": r.get("color"),
        "drive": r.get("drive"),
        "vin": r.get("vin") or None,
        "url": url,
        "images": images,
        "specs": {},
        "is_active": True,
        "last_seen": NOW,
    }


def deactivate_source(source: str) -> None:
    if DRY_RUN:
        print(f"  [dry-run] PATCH cars?source={source} → is_active=false")
        return
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/cars",
        params={"source": f"eq.{source}"},
        json={"is_active": False},
        headers=HEADERS,
        timeout=30,
    )
    r.raise_for_status()
    print(f"  Deactivated source={source}")


def upsert_batch(rows: list) -> None:
    if DRY_RUN:
        print(f"  [dry-run] POST {len(rows)} rows")
        return
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/cars?on_conflict=external_id",
        json=rows,
        headers=HEADERS,
        timeout=60,
    )
    if not r.ok:
        print(f"  ERROR {r.status_code}: {r.text[:200]}")
        r.raise_for_status()


def import_cars(json_file: str, converter, source: str, region: str) -> None:
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"\n{'='*60}")
    print(f"Importing {len(data)} cars from {json_file}")
    print(f"  region={region}, source={source}")

    rows = []
    for r in data:
        row = converter(r)
        if row.get("external_id"):
            rows.append(row)

    # Deduplicate by external_id
    seen = {}
    for row in rows:
        seen[row["external_id"]] = row
    rows = list(seen.values())
    print(f"  Unique external_ids: {len(rows)}")

    deactivate_source(source)

    BATCH = 50
    total = 0
    for i in range(0, len(rows), BATCH):
        batch = rows[i:i + BATCH]
        upsert_batch(batch)
        total += len(batch)
        print(f"  Upserted {total}/{len(rows)}", end="\r")
    print(f"  Done: {total} rows upserted to Supabase")


def count_region(region: str) -> int:
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/cars",
        params={"region": f"eq.{region}", "is_active": "eq.true", "select": "id"},
        headers={**HEADERS, "Range": "0-0", "Prefer": "count=exact"},
        timeout=15,
    )
    cr = r.headers.get("Content-Range", "")
    try:
        return int(cr.split("/")[1])
    except Exception:
        return -1


if __name__ == "__main__":
    print(f"{'='*60}")
    print(f"Supabase Car Import — {NOW}")
    print(f"DRY RUN: {DRY_RUN}")

    import_cars("cars_korea_stock.json", korea_to_row, "encar", "korea")
    import_cars("cars_europe_new.json", europe_to_row, "autoscout24", "europe")
    import_cars("cars_georgia_stock.json", georgia_to_row, "myauto_ge", "georgia")

    if not DRY_RUN:
        print(f"\n{'='*60}")
        print("Final counts in Supabase (active):")
        for region in ("korea", "europe", "georgia"):
            cnt = count_region(region)
            ok = "✅" if cnt >= 444 else "❌"
            print(f"  {region:10}: {cnt:4} {ok}")
    print("\nDone.")
