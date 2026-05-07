#!/usr/bin/env python3
"""Probe candidate OEM catalog sources for availability and robots hints."""
import argparse
import json
import urllib.robotparser
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "oem_source_candidates.json"
DEFAULT_OUTPUT = ROOT / "data" / "oem_source_probe.json"
UA = "EXPO-MIR-OEM-Audit/1.0 (+https://cmsauto.store/)"
CATALOG_PATHS = ("/catalog", "/cat", "/parts", "/search", "/vin")
PARKED_HINTS = ("hugedomains.com", "domain_profile", "domain for sale", "buy this domain")


def origin(domain: str) -> str:
    return domain if domain.startswith(("http://", "https://")) else f"https://{domain}"


def get_robots(base_url: str) -> dict:
    robots_url = base_url.rstrip("/") + "/robots.txt"
    result = {"robots_url": robots_url, "robots_status": None, "robots_allows_root": None, "robots_path_rules": {}}
    try:
        resp = requests.get(robots_url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        result["robots_status"] = resp.status_code
        if resp.status_code < 400:
            parser = urllib.robotparser.RobotFileParser()
            parser.parse(resp.text.splitlines())
            result["robots_allows_root"] = parser.can_fetch(UA, base_url + "/")
            result["robots_path_rules"] = {
                path: parser.can_fetch(UA, base_url.rstrip("/") + path) for path in CATALOG_PATHS
            }
    except Exception as exc:
        result["robots_error"] = str(exc)[:180]
    return result


def probe_one(item: dict) -> dict:
    base = origin(item["domain"])
    parsed = urlparse(base)
    if not parsed.netloc:
        base = "https://" + base
    row = dict(item)
    row.update({"url": base, "checked_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
    try:
        resp = requests.get(base, headers={"User-Agent": UA}, timeout=15, allow_redirects=True)
        text_sample = resp.text[:5000] if "html" in resp.headers.get("content-type", "") else ""
        row.update({
            "status": resp.status_code,
            "final_url": resp.url,
            "content_type": resp.headers.get("content-type", ""),
            "title_hint": extract_title(resp.text) if text_sample else "",
            "parked_or_wrong_domain": looks_parked(resp.url, text_sample),
        })
    except Exception as exc:
        row.update({"status": None, "error": str(exc)[:180]})
    row.update(get_robots(base))
    row["manual_lookup_assessment"] = assess_manual_lookup(row)
    row["bulk_import_assessment"] = assess(row)
    return row


def extract_title(text: str) -> str:
    lower = text.lower()
    start = lower.find("<title")
    if start < 0:
        return ""
    start = lower.find(">", start)
    end = lower.find("</title>", start)
    if start < 0 or end < 0:
        return ""
    return " ".join(text[start + 1:end].split())[:160]


def looks_parked(final_url: str, text: str) -> bool:
    haystack = f"{final_url}\n{text}".lower()
    return any(hint in haystack for hint in PARKED_HINTS)


def assess_manual_lookup(row: dict) -> str:
    if row.get("parked_or_wrong_domain"):
        return "not_catalog_or_domain_changed"
    if row.get("status") in {401, 403}:
        return "auth_or_blocked"
    if row.get("robots_allows_root") is False:
        return "robots_disallow"
    if row.get("status") and row["status"] < 400:
        path_rules = row.get("robots_path_rules") or {}
        if any(value is False for value in path_rules.values()):
            return "manual_lookup_ok_catalog_paths_limited"
        return "manual_lookup_ok_bulk_requires_terms"
    return "needs_browser_manual_check"


def assess(row: dict) -> str:
    mode = row.get("mode", "")
    status = row.get("status")
    robots = row.get("robots_allows_root")
    if mode in {"partner_api_or_export", "catalog_export_possible"}:
        return "prefer_export_or_api"
    if mode == "account_required":
        return "needs_account_terms_check"
    if status in {401, 403}:
        return "blocked_or_auth_required"
    if row.get("parked_or_wrong_domain"):
        return "unavailable_or_needs_manual_check"
    if robots is False:
        return "robots_disallow_bulk"
    if status and status < 400:
        return "manual_single_lookup_ok_bulk_unconfirmed"
    return "unavailable_or_needs_manual_check"


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe OEM catalog candidate sources")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    items = json.load(open(args.input, encoding="utf-8"))
    if args.limit:
        items = items[:args.limit]
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(probe_one, item) for item in items]
        for future in as_completed(futures):
            row = future.result()
            results.append(row)
            print(f"{row.get('domain'):32} status={row.get('status')} assessment={row.get('bulk_import_assessment')}")

    results.sort(key=lambda row: (row.get("priority", "z"), row.get("domain", "")))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(results),
        "results": results,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote={out}")


if __name__ == "__main__":
    main()
