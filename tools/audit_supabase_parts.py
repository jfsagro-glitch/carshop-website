#!/usr/bin/env python3
"""Audit Supabase parts table for OEM import integrity."""
import csv
import re
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import import_to_supabase as cfg  # noqa: E402


INTERNAL_RE = re.compile(r"^[A-Z]{2}-[A-Z0-9]{4}-[A-Z0-9]+-")
GENERATED_FILTER = "?or=(description.like.%D0%97%D0%B0%D0%BF%D1%87%D0%B0%D1%81%D1%82%D1%8C*,description.like.OEM-%D0%BA%D0%B0%D0%BD%D0%B4%D0%B8%D0%B4%D0%B0%D1%82*)"


def supabase_headers(extra=None):
    headers = {
        "apikey": cfg.SUPABASE_KEY,
        "Authorization": f"Bearer {cfg.SUPABASE_KEY}",
    }
    if extra:
        headers.update(extra)
    return headers


def count_parts(query=""):
    headers = supabase_headers({"Prefer": "count=exact"})
    params = {"select": "id"}
    url = f"{cfg.SUPABASE_URL}/rest/v1/parts{query}"
    resp = requests.get(url, headers=headers, params=params if not query else None, timeout=60)
    resp.raise_for_status()
    content_range = resp.headers.get("content-range", "")
    return int(content_range.rsplit("/", 1)[-1]) if "/" in content_range else None


def fetch_generated_sample(limit=5000):
    params = {
        "select": "oem_number,brand,category,description",
        "limit": str(limit),
    }
    resp = requests.get(
        f"{cfg.SUPABASE_URL}/rest/v1/parts{GENERATED_FILTER}",
        headers=supabase_headers(),
        params=params,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def audit_csv(path=ROOT / "generated_parts_catalog.csv"):
    rows = empty = internal = 0
    oems = {}
    with open(path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            rows += 1
            oem = (row.get("oem_number") or "").strip()
            if not oem:
                empty += 1
            if INTERNAL_RE.match(oem):
                internal += 1
            oems[oem] = oems.get(oem, 0) + 1
    return {
        "rows": rows,
        "empty_oem": empty,
        "internal_like": internal,
        "duplicate_oem_values": sum(1 for count in oems.values() if count > 1),
    }


def main():
    print("Supabase parts audit")
    print(f"total_parts={count_parts()}")
    print(f"generated_parts={count_parts(GENERATED_FILTER)}")
    sample = fetch_generated_sample()
    bad = [row for row in sample if INTERNAL_RE.match(row.get("oem_number") or "")]
    empty = [row for row in sample if not (row.get("oem_number") or "").strip()]
    print(f"generated_sample={len(sample)} sample_internal_like={len(bad)} sample_empty_oem={len(empty)}")
    print("CSV audit")
    for key, value in audit_csv().items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
