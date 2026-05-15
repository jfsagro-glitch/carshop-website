#!/usr/bin/env python3
"""Build verified OEM lookup from source records with mandatory provenance fields.

Input format (CSV):
  brand_prefix,part_code,oem_number,source_name,source_url,retrieved_at
Optional columns:
  brand,model,year_from,year_to,engine,restyle,vin_pattern
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.oem_validation import is_plausible_oem as is_plausible_oem_for_brand
from tools.oem_validation import split_oem_candidates


def is_plausible_oem_number(value: str, prefix: str = "") -> bool:
    """Reject common HTML/JS tokens accidentally captured as part numbers."""
    if prefix:
        return is_plausible_oem_for_brand(prefix, value, strict_brand=True)
    token = str(value or "").strip().upper()
    compact = re.sub(r"[^A-Z0-9]", "", token)
    if not token:
        return False
    if len(compact) < 6 or len(compact) > 24:
        return False
    if token.startswith("0X"):
        return False
    if re.fullmatch(r"20\d{2}[-./]\d{1,2}[-./]\d{1,2}", token):
        return False
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}", token):
        return False
    if re.fullmatch(r"\d{1,2}[A-ZÄÖÜ]{3,}\d{4}", token):
        return False
    if any(month in token for month in ("JULI", "JANUAR", "FEBRUAR", "MAERZ", "MÄRZ", "APRIL", "JUNI", "AUGUST", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DEZEMBER")):
        return False
    if token.startswith(("HTTP", "WWW", "IMG", "SRC")):
        return False
    if token in {"CONTENT", "SCRIPT", "WINDOW", "SEARCH", "VALUE", "FALSE", "TRUE", "NULL", "UNDEFINED", "COOKIE", "DOCTYPE"}:
        return False
    if token.startswith(("WP-", "JS-")):
        return False
    if token.startswith("G-") and len(token) > 8:
        return False
    if not re.search(r"\d", compact):
        return False
    if re.fullmatch(r"[A-Z]+", compact):
        return False
    if len(set(compact)) <= 2:
        return False
    return True


def build_verified_lookup(csv_path: Path) -> tuple[dict[str, dict[str, list[str]]], dict]:
    if not csv_path.exists():
        raise FileNotFoundError(f"Input file not found: {csv_path}")

    lookup: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    total_rows = 0
    accepted_rows = 0
    rejected_rows = 0

    required = {"brand_prefix", "part_code", "oem_number", "source_name", "source_url", "retrieved_at"}

    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing_cols = required - set(reader.fieldnames or [])
        if missing_cols:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing_cols))}")

        for row in reader:
            total_rows += 1
            prefix = str(row.get("brand_prefix") or "").strip().upper()
            code = str(row.get("part_code") or "").strip().upper()
            oem = str(row.get("oem_number") or "").strip()
            source_name = str(row.get("source_name") or "").strip()
            source_url = str(row.get("source_url") or "").strip()
            retrieved_at = str(row.get("retrieved_at") or "").strip()

            if not (prefix and code and oem and source_name and source_url and retrieved_at):
                rejected_rows += 1
                continue

            accepted_any = False
            for candidate in split_oem_candidates(oem):
                if not is_plausible_oem_number(candidate, prefix):
                    continue
                bucket = lookup[prefix][code]
                if candidate not in bucket:
                    bucket.append(candidate)
                accepted_any = True
                accepted_rows += 1
            if not accepted_any:
                rejected_rows += 1

    lookup_out = {
        prefix: {code: nums for code, nums in sorted(codes.items())}
        for prefix, codes in sorted(lookup.items())
    }
    summary = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_file": str(csv_path).replace("\\", "/"),
        "total_rows": total_rows,
        "accepted_rows": accepted_rows,
        "rejected_rows": rejected_rows,
        "brands": len(lookup_out),
        "brand_code_pairs": sum(len(codes) for codes in lookup_out.values()),
        "oem_numbers": sum(len(nums) for codes in lookup_out.values() for nums in codes.values()),
        "required_fields": sorted(required),
    }
    return lookup_out, summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Build verified OEM lookup from provenance-backed records")
    parser.add_argument("--input", required=True, help="Path to verified OEM source CSV")
    parser.add_argument("--output", default="data/oem_lookup_verified.json", help="Output JSON path")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    lookup, summary = build_verified_lookup(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "summary": summary,
        "lookup": lookup,
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"wrote={output_path}")
    print(f"brands={summary['brands']} pairs={summary['brand_code_pairs']} oem={summary['oem_numbers']}")
    print(f"accepted={summary['accepted_rows']} rejected={summary['rejected_rows']}")


if __name__ == "__main__":
    main()
