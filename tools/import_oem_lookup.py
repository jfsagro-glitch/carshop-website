#!/usr/bin/env python3
"""
Import verified OEM numbers into data/oem_lookup_overrides.json.

CSV columns:
  brand or prefix, part_code, oem_number
Optional columns:
  source, note

JSON format:
  [
    {"brand": "Toyota", "part_code": "OF", "oem_number": "04152-YZZA6", "source": "..."}
  ]
or:
  {"lookup": {"TY": {"OF": ["04152-YZZA6"]}}, "sources": [...]}
"""
import argparse
import csv
import json
import re
import tempfile
from urllib.parse import urlparse
from datetime import datetime, timezone
from pathlib import Path
import sys
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.build_parts_catalog import BRAND_PREFIX  # noqa: E402

TARGET = ROOT / "data" / "oem_lookup_overrides.json"


def norm_code(value: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(value or "").upper())


def norm_oem(value: str) -> str:
    value = str(value or "").strip().upper()
    return re.sub(r"\s+", "", value)


def brand_to_prefix(row: dict) -> str:
    prefix = norm_code(row.get("prefix", ""))
    if prefix:
        return prefix
    brand = str(row.get("brand", "")).strip()
    return BRAND_PREFIX.get(brand, norm_code(brand[:2]))


def load_target() -> dict:
    if TARGET.exists():
        return json.load(open(TARGET, encoding="utf-8"))
    return {
        "source_note": "Дополнительные OEM-номера, загруженные из проверенных прайсов/API/каталогов. Формат: prefix -> part code -> массив оригинальных номеров.",
        "sources": [],
        "lookup": {},
    }


def add_number(data: dict, prefix: str, code: str, number: str) -> bool:
    if not prefix or not code or not number:
        return False
    lookup = data.setdefault("lookup", {})
    bucket = lookup.setdefault(prefix, {}).setdefault(code, [])
    if number in bucket:
        return False
    bucket.append(number)
    return True


def iter_csv(path: Path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            yield row


def iter_json(path: Path):
    raw = json.load(open(path, encoding="utf-8"))
    if isinstance(raw, dict) and "lookup" in raw:
        for prefix, codes in raw["lookup"].items():
            for code, numbers in codes.items():
                if isinstance(numbers, str):
                    numbers = [numbers]
                for number in numbers:
                    yield {"prefix": prefix, "part_code": code, "oem_number": number}
        return
    if not isinstance(raw, list):
        raise ValueError("JSON должен быть массивом записей или объектом с lookup")
    yield from raw


def main() -> None:
    parser = argparse.ArgumentParser(description="Import verified OEM lookup rows")
    parser.add_argument("--input", "-i", required=True, help="CSV/JSON with OEM rows, local path or https:// URL")
    parser.add_argument("--source", default="", help="Human-readable source name/URL")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    input_arg = args.input
    temp_path = None
    if input_arg.startswith(("http://", "https://")):
        parsed = urlparse(input_arg)
        suffix = Path(parsed.path).suffix or ".csv"
        resp = requests.get(input_arg, timeout=60)
        resp.raise_for_status()
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(resp.content)
        tmp.close()
        temp_path = Path(tmp.name)
        path = temp_path
    else:
        path = Path(input_arg)
    if not path.exists():
        raise SystemExit(f"Файл не найден: {path}")

    rows = iter_csv(path) if path.suffix.lower() == ".csv" else iter_json(path)
    data = load_target()

    added = skipped = 0
    for row in rows:
        prefix = brand_to_prefix(row)
        code = norm_code(row.get("part_code") or row.get("code") or "")
        number = norm_oem(row.get("oem_number") or row.get("oem") or row.get("number") or "")
        if add_number(data, prefix, code, number):
            added += 1
        else:
            skipped += 1

    if args.source:
        data.setdefault("sources", []).append({
            "source": args.source,
            "imported_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "file": input_arg,
            "added": added,
            "skipped": skipped,
        })

    if not args.dry_run:
        TARGET.parent.mkdir(exist_ok=True)
        with open(TARGET, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"added={added} skipped={skipped} target={TARGET}")
    if temp_path:
        temp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
