#!/usr/bin/env python3
"""
PartsTech integration helper.

PartsTech Punchout API normally requires:
  PARTSTECH_PARTNER_ID
  PARTSTECH_PARTNER_API_KEY
  PARTSTECH_USER_ID
  PARTSTECH_USER_API_KEY

This helper intentionally reads secrets only from environment variables and
never prints them. It can test authentication and create a VIN/keyword quote
session when the credentials are complete.
"""
import argparse
import json
import os
import sys
from pathlib import Path

import requests

API_BASE = os.environ.get("PARTSTECH_API_BASE", "https://api.partstech.com").rstrip("/")


def env(name: str) -> str:
    return os.environ.get(name, "").strip()


def credentials() -> dict:
    return {
        "partnerId": env("PARTSTECH_PARTNER_ID"),
        "partnerApiKey": env("PARTSTECH_PARTNER_API_KEY"),
        "userId": env("PARTSTECH_USER_ID"),
        "userApiKey": env("PARTSTECH_USER_API_KEY"),
    }


def assert_credentials(cfg: dict) -> None:
    missing = [key for key, value in cfg.items() if not value]
    if missing:
        raise SystemExit(
            "Missing PartsTech credentials: "
            + ", ".join(missing)
            + ". Set env vars, do not commit secrets."
        )


def get_access_token() -> str:
    cfg = credentials()
    assert_credentials(cfg)
    # Punchout API auth expects Partner + User credentials in this shape.
    payload = {
        "accessType": "user",
        "credentials": {
            "partner": {"id": cfg["partnerId"], "key": cfg["partnerApiKey"]},
            "user": {"id": cfg["userId"], "key": cfg["userApiKey"]},
        },
    }
    resp = requests.post(f"{API_BASE}/oauth/access", json=payload, timeout=30)
    if resp.status_code >= 400:
        raise RuntimeError(f"PartsTech auth failed: HTTP {resp.status_code} {resp.text[:500]}")
    data = resp.json()
    token = data.get("accessToken") or data.get("access_token") or data.get("token")
    if not token:
        raise RuntimeError(f"PartsTech auth response has no token. Keys: {sorted(data.keys())}")
    return token


def create_quote_session(
    vin: str = "",
    keyword: str = "",
    part_number: str = "",
    callback_url: str = "",
    callback_order_url: str = "",
    return_url: str = "",
) -> dict:
    token = get_access_token()
    search_params = {}
    if vin:
        search_params["vin"] = vin
    if keyword:
        search_params["keyword"] = keyword
    if part_number:
        search_params["partNumber"] = part_number
    urls = {}
    if callback_url:
        urls["callbackUrl"] = callback_url
    if callback_order_url:
        urls["callbackOrderUrl"] = callback_order_url
    if return_url:
        urls["returnUrl"] = return_url
    payload = {"searchParams": search_params, "urls": urls, "settings": {"poNumber": "EXPO-MIR-OEM"}}
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{API_BASE}/punchout/quote/create", headers=headers, json=payload, timeout=30)
    if resp.status_code >= 400:
        raise RuntimeError(f"PartsTech quote session failed: HTTP {resp.status_code} {resp.text[:500]}")
    return resp.json()


def write_json(data: dict, path: str) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="PartsTech API helper")
    parser.add_argument("--auth-test", action="store_true", help="Only request an access token")
    parser.add_argument("--vin", default="", help="VIN for quote session")
    parser.add_argument("--keyword", default="", help="Keyword for quote session")
    parser.add_argument("--part-number", default="", help="Part number search")
    parser.add_argument("--callback-url", default="", help="Quote callback URL")
    parser.add_argument("--callback-order-url", default="", help="Order callback URL")
    parser.add_argument("--return-url", default="", help="Return URL after cart action")
    parser.add_argument("--output", default="data/partstech_session.json", help="Output JSON")
    args = parser.parse_args()

    try:
        if args.auth_test:
            get_access_token()
            print("PartsTech auth OK")
            return
        data = create_quote_session(
            vin=args.vin,
            keyword=args.keyword,
            part_number=args.part_number,
            callback_url=args.callback_url,
            callback_order_url=args.callback_order_url,
            return_url=args.return_url,
        )
        write_json(data, args.output)
        print(f"PartsTech session saved: {args.output}")
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
