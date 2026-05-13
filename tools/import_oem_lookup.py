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
import subprocess
import tempfile
from urllib.parse import urlparse
from datetime import datetime, timezone
from pathlib import Path
import sys
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.build_parts_catalog import BRAND_PREFIX  # noqa: E402
from generate_parts_catalog import get_merged_oem_lookup  # noqa: E402

TARGET = ROOT / "data" / "oem_lookup_overrides.json"
PARTS_CATALOG = ROOT / "data" / "parts_catalog.json"

BAD_OEM_FRAGMENTS = {
    "HTTP",
    "HTTPS",
    "CROPPED",
    "BRAKE",
    "ICON",
    "LOGO",
    "THUMB",
    "AVATAR",
    "PNG",
    "JPG",
    "JPEG",
    "WEBP",
    "SVG",
    "GIF",
}

OEM_FORMAT_PATTERNS = {
    "AC": [
        re.compile(r"\b\d{5}-[A-Z0-9]{3}-[A-Z0-9]{3}\b"),
        re.compile(r"\b\d{5}-[A-Z0-9]{2}[0-9]{2}\b"),
    ],
    "HO": [
        re.compile(r"\b\d{5}-[A-Z0-9]{3}-[A-Z0-9]{3}\b"),
        re.compile(r"\b\d{5}-[A-Z0-9]{2}[0-9]{2}\b"),
    ],
    "BM": [re.compile(r"\b\d{2}[\s\-]?\d{2}[\s\-]?\d{6,7}\b")],
    "MN": [re.compile(r"\b\d{2}[\s\-]?\d{2}[\s\-]?\d{6,7}\b")],
    "MB": [
        re.compile(r"\bA\d{10}\b"),
        re.compile(r"\bA\d{3}\s?\d{2}\s?\d{2}\s?\d{2}\b"),
    ],
    "VW": [re.compile(r"\b[0-9A-Z]{3}[\s\-]?[0-9A-Z]{3}[\s\-]?[0-9A-Z]{3}[\s\-]?[A-Z0-9]{0,2}\b")],
    "AU": [re.compile(r"\b[0-9A-Z]{3}[\s\-]?[0-9A-Z]{3}[\s\-]?[0-9A-Z]{3}[\s\-]?[A-Z0-9]{0,2}\b")],
    "SK": [re.compile(r"\b[0-9A-Z]{3}[\s\-]?[0-9A-Z]{3}[\s\-]?[0-9A-Z]{3}[\s\-]?[A-Z0-9]{0,2}\b")],
    "SE": [re.compile(r"\b[0-9A-Z]{3}[\s\-]?[0-9A-Z]{3}[\s\-]?[0-9A-Z]{3}[\s\-]?[A-Z0-9]{0,2}\b")],
}


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


def load_valid_catalog_pairs() -> set[tuple[str, str]]:
    if not PARTS_CATALOG.exists():
        return set()
    raw = json.load(open(PARTS_CATALOG, encoding="utf-8"))
    prefixes = []
    for brand in raw.get("brands", []):
        prefix = str(brand.get("prefix") or "").strip().upper()
        if not prefix:
            name = str(brand.get("name") or "").strip()
            prefix = norm_code(name[:2])
        if prefix:
            prefixes.append(prefix)

    codes = [
        norm_code(part.get("code") or "")
        for part in raw.get("parts_template", [])
        if norm_code(part.get("code") or "")
    ]
    return {(p, c) for p in prefixes for c in codes}


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


def detect_input_type(path: Path) -> str:
    if path.suffix.lower() == ".csv":
        return "csv"
    return "json"


def build_brand_oem_index(lookup: dict) -> dict[tuple[str, str], set[str]]:
    index: dict[tuple[str, str], set[str]] = {}
    for prefix, codes in lookup.items():
        if not isinstance(codes, dict):
            continue
        p = norm_code(prefix)
        for code, numbers in codes.items():
            c = norm_code(code)
            values = numbers if isinstance(numbers, list) else [numbers]
            for number in values:
                n = norm_oem(number)
                if not (p and c and n):
                    continue
                key = (p, n)
                index.setdefault(key, set()).add(c)
    return index


def is_plausible_oem(prefix: str, number: str) -> bool:
    token = norm_oem(number)
    if not token or len(token) < 6 or len(token) > 20:
        return False

    if any(fragment in token for fragment in BAD_OEM_FRAGMENTS):
        return False

    if re.search(r"\d{2,4}X\d{2,4}", token):
        return False

    if token.startswith(("HTTP", "WWW", "IMG", "SRC", "DATA")):
        return False

    if re.fullmatch(r"[A-Z]{4,}", token):
        return False

    if re.fullmatch(r"[A-Z]{1,2}-[A-Z0-9]{8,}", token):
        return False

    digits = sum(1 for c in token if c.isdigit())
    letters = sum(1 for c in token if c.isalpha())
    if digits < 3:
        return False

    patterns = OEM_FORMAT_PATTERNS.get(prefix, [])
    if patterns:
        if any(p.search(token) for p in patterns):
            if prefix in {"VW", "AU", "SK", "SE"}:
                compact = re.sub(r"[^A-Z0-9]", "", token)
                vag_digits = sum(1 for c in compact if c.isdigit())
                vag_letters = sum(1 for c in compact if c.isalpha())
                if vag_digits < 5 or vag_letters > 4:
                    return False
                if compact and not (compact[0].isdigit() or compact.startswith("N") or compact.startswith("W")):
                    return False
            return True
        if prefix in {"VW", "AU", "SK", "SE"}:
            compact = re.sub(r"[^A-Z0-9]", "", token)
            vag_digits = sum(1 for c in compact if c.isdigit())
            vag_letters = sum(1 for c in compact if c.isalpha())
            return bool(
                re.fullmatch(r"[0-9A-Z]{9,11}", compact)
                and vag_digits >= 5
                and vag_letters <= 4
                and compact
                and (compact[0].isdigit() or compact.startswith("N") or compact.startswith("W"))
            )
        return False

    if "-" not in token and len(token) > 14:
        return False
    if "-" not in token and letters > 6 and digits < 5:
        return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Import verified OEM lookup rows")
    parser.add_argument("--input", "-i", required=True, help="CSV/JSON with OEM rows, local path or https:// URL")
    parser.add_argument("--source", default="", help="Human-readable source name/URL")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-report", action="store_true", help="Do not rebuild data/oem_coverage.json")
    parser.add_argument(
        "--diagnostics-csv",
        default="",
        help="Optional CSV path to write per-row import decision diagnostics",
    )
    parser.add_argument(
        "--only-uncovered-pairs",
        action="store_true",
        help="Import row only when (brand_prefix, part_code) is absent in merged lookup at processing time",
    )
    parser.add_argument(
        "--only-catalog-pairs",
        action="store_true",
        help="Import row only when (brand_prefix, part_code) exists in data/parts_catalog.json matrix",
    )
    parser.add_argument(
        "--no-validate-oem-format",
        action="store_true",
        help="Disable OEM format plausibility validation",
    )
    parser.add_argument(
        "--max-codes-per-oem-per-brand",
        type=int,
        default=1,
        help="Reject OEM reuse across too many part codes for same brand prefix (0 disables)",
    )
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

    input_type = detect_input_type(path)
    rows = iter_csv(path) if input_type == "csv" else iter_json(path)
    data = load_target()
    brand_oem_codes = build_brand_oem_index(data.get("lookup", {}))
    uncovered_pairs = set(get_merged_oem_lookup().keys()) if args.only_uncovered_pairs else set()
    valid_pairs = load_valid_catalog_pairs() if args.only_catalog_pairs else set()

    added = skipped = skipped_pairs = skipped_invalid_pairs = skipped_invalid_oem = skipped_reuse = 0
    diagnostics_rows: list[dict[str, str]] = []
    for row in rows:
        prefix = brand_to_prefix(row)
        code = norm_code(row.get("part_code") or row.get("code") or "")
        number = norm_oem(row.get("oem_number") or row.get("oem") or row.get("number") or "")
        reason = ""
        accepted = "0"

        if args.only_catalog_pairs and (prefix, code) not in valid_pairs:
            skipped_invalid_pairs += 1
            reason = "invalid_catalog_pair"
            if args.diagnostics_csv:
                diagnostics_rows.append(
                    {
                        "brand": str(row.get("brand") or ""),
                        "brand_prefix": prefix,
                        "part_code": code,
                        "oem_number": number,
                        "accepted": accepted,
                        "reason": reason,
                    }
                )
            continue

        if not args.no_validate_oem_format and not is_plausible_oem(prefix, number):
            skipped_invalid_oem += 1
            reason = "invalid_oem_format"
            if args.diagnostics_csv:
                diagnostics_rows.append(
                    {
                        "brand": str(row.get("brand") or ""),
                        "brand_prefix": prefix,
                        "part_code": code,
                        "oem_number": number,
                        "accepted": accepted,
                        "reason": reason,
                    }
                )
            continue

        if args.max_codes_per_oem_per_brand > 0:
            key = (prefix, number)
            used_codes = brand_oem_codes.get(key, set())
            if code not in used_codes and len(used_codes) >= args.max_codes_per_oem_per_brand:
                skipped_reuse += 1
                reason = "invalid_oem_reuse"
                if args.diagnostics_csv:
                    diagnostics_rows.append(
                        {
                            "brand": str(row.get("brand") or ""),
                            "brand_prefix": prefix,
                            "part_code": code,
                            "oem_number": number,
                            "accepted": accepted,
                            "reason": reason,
                        }
                    )
                continue

        if args.only_uncovered_pairs and (prefix, code) in uncovered_pairs:
            skipped_pairs += 1
            reason = "already_covered_pair"
            if args.diagnostics_csv:
                diagnostics_rows.append(
                    {
                        "brand": str(row.get("brand") or ""),
                        "brand_prefix": prefix,
                        "part_code": code,
                        "oem_number": number,
                        "accepted": accepted,
                        "reason": reason,
                    }
                )
            continue

        if add_number(data, prefix, code, number):
            added += 1
            accepted = "1"
            reason = "added"
            brand_oem_codes.setdefault((prefix, number), set()).add(code)
            if args.only_uncovered_pairs:
                uncovered_pairs.add((prefix, code))
        else:
            skipped += 1
            reason = "duplicate_oem_in_lookup"

        if args.diagnostics_csv:
            diagnostics_rows.append(
                {
                    "brand": str(row.get("brand") or ""),
                    "brand_prefix": prefix,
                    "part_code": code,
                    "oem_number": number,
                    "accepted": accepted,
                    "reason": reason,
                }
            )

    if args.source:
        data.setdefault("sources", []).append({
            "source": args.source,
            "imported_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "file": input_arg,
            "added": added,
            "skipped": skipped,
            "skipped_pairs": skipped_pairs,
            "skipped_invalid_pairs": skipped_invalid_pairs,
            "skipped_invalid_oem": skipped_invalid_oem,
            "skipped_invalid_reuse": skipped_reuse,
            "only_uncovered_pairs": bool(args.only_uncovered_pairs),
            "only_catalog_pairs": bool(args.only_catalog_pairs),
            "validate_oem_format": not bool(args.no_validate_oem_format),
            "max_codes_per_oem_per_brand": int(args.max_codes_per_oem_per_brand),
        })

    if not args.dry_run:
        TARGET.parent.mkdir(exist_ok=True)
        with open(TARGET, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        if args.diagnostics_csv:
            diag_path = Path(args.diagnostics_csv)
            diag_path.parent.mkdir(parents=True, exist_ok=True)
            with diag_path.open("w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=["brand", "brand_prefix", "part_code", "oem_number", "accepted", "reason"],
                )
                writer.writeheader()
                writer.writerows(diagnostics_rows)
        if not args.skip_report:
            subprocess.run(
                [sys.executable, str(ROOT / "tools" / "oem_coverage_report.py"), "--json", str(ROOT / "data" / "oem_coverage.json")],
                check=True,
            )

    print(
        f"added={added} skipped={skipped} skipped_pairs={skipped_pairs} "
        f"skipped_invalid_pairs={skipped_invalid_pairs} skipped_invalid_oem={skipped_invalid_oem} "
        f"skipped_invalid_reuse={skipped_reuse} "
        f"only_uncovered_pairs={args.only_uncovered_pairs} "
        f"only_catalog_pairs={args.only_catalog_pairs} input_type={input_type} target={TARGET}"
    )
    if args.diagnostics_csv:
        print(f"diagnostics_csv={args.diagnostics_csv} diagnostics_rows={len(diagnostics_rows)}")
    if temp_path:
        temp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
