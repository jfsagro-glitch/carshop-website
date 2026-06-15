#!/usr/bin/env python3
"""Post the current homepage Europe selection to a Telegram channel."""

from __future__ import annotations

import argparse
import html
import io
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OFFERS_PATH = ROOT / "data" / "home_featured_europe.json"
HISTORY_PATH = ROOT / "data" / "telegram_europe_history.json"
SITE_URL = "https://cmsauto.store/?source=pwa"
EUROPE_URL = "https://cmsauto.store/europe-orders.html"
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = (
    os.environ.get("TELEGRAM_EUROPE_CHANNEL_ID", "").strip()
    or os.environ.get("TELEGRAM_CHAT_ID", "").strip()
)

IMAGE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ExpoMirBot/1.0)",
    "Referer": "https://www.autoscout24.de/",
}


def load_offers() -> list[dict]:
    payload = json.loads(OFFERS_PATH.read_text(encoding="utf-8"))
    offers = payload.get("offers")
    if not isinstance(offers, list):
        raise ValueError("home_featured_europe.json has no offers array")

    valid = []
    for offer in offers:
        details = offer.get("details") or {}
        images = offer.get("images") or [offer.get("image")]
        if not all(
            (
                offer.get("title"),
                offer.get("price"),
                offer.get("source_url"),
                offer.get("year"),
                details.get("engine"),
                details.get("power"),
                details.get("mileage"),
                any(images),
            )
        ):
            continue
        valid.append(offer)
    return valid[:10]


def load_history() -> dict:
    if not HISTORY_PATH.exists():
        return {"posts": [], "cycle_offer_urls": []}
    payload = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    return {
        "posts": payload.get("posts") if isinstance(payload.get("posts"), list) else [],
        "cycle_offer_urls": (
            payload.get("cycle_offer_urls")
            if isinstance(payload.get("cycle_offer_urls"), list)
            else []
        ),
    }


def save_history(history: dict) -> None:
    HISTORY_PATH.write_text(
        json.dumps(history, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def posted_urls(history: dict) -> set[str]:
    return {
        str(post.get("source_url"))
        for post in history["posts"]
        if isinstance(post, dict) and post.get("source_url")
    }


def initialize_cycle(history: dict, offers: list[dict]) -> None:
    if not history["cycle_offer_urls"]:
        history["cycle_offer_urls"] = [str(offer["source_url"]) for offer in offers]


def rebuild_homepage_cycle(history: dict) -> list[dict]:
    subprocess.run(
        ["node", "tools/build_home_europe_offers.mjs", "--exclude-history"],
        cwd=ROOT,
        check=True,
    )
    offers = load_offers()
    history["cycle_offer_urls"] = [str(offer["source_url"]) for offer in offers]
    return offers


def image_urls(offer: dict) -> list[str]:
    raw = offer.get("images") or [offer.get("image")]
    return [str(url) for url in raw if str(url or "").startswith(("https://", "http://"))]


def download_offer_photo(offer: dict) -> bytes | None:
    for url in image_urls(offer)[:4]:
        try:
            response = requests.get(url, headers=IMAGE_HEADERS, timeout=20)
            content_type = response.headers.get("content-type", "").split(";")[0].lower()
            if response.ok and content_type.startswith("image/") and 1_000 < len(response.content) < 10_000_000:
                with Image.open(io.BytesIO(response.content)) as source:
                    photo = source.convert("RGB")
                    photo.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
                    output = io.BytesIO()
                    photo.save(output, format="JPEG", quality=88, optimize=True)
                    return output.getvalue()
        except (requests.RequestException, OSError):
            continue
    return None


def offer_caption(offer: dict) -> str:
    details = offer.get("details") or {}
    lines = [
        f"🇪🇺 <b>Автомобиль дня · {datetime.now(ZoneInfo('Europe/Moscow')).strftime('%d.%m.%Y')}</b>",
        "",
        f"🚘 <b>{html.escape(str(offer['title']))}</b>",
        f"💰 Под ключ в РФ: <b>{html.escape(str(offer['price']))}</b>",
        f"🇪🇺 Цена в Европе: {html.escape(str(offer.get('base_price') or 'уточняется'))}",
        f"🛣 Пробег: {html.escape(str(details['mileage']))}",
        f"⚙️ Двигатель: {html.escape(str(details['engine']))}",
        f"🏁 Мощность: {html.escape(str(details['power']))}",
        f'🔗 <a href="{html.escape(str(offer["source_url"]), quote=True)}">Открыть объявление</a>',
        "",
        f'🌐 <a href="{SITE_URL}">Другие предложения на сайте</a>',
    ]
    return "\n".join(lines)[:1024]


def telegram_request(method: str, **kwargs) -> requests.Response:
    response = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/{method}",
        timeout=45,
        **kwargs,
    )
    if not response.ok:
        raise RuntimeError(f"Telegram {method} failed: {response.status_code} {response.text[:500]}")
    return response


def send_offer(offer: dict, photo: bytes) -> None:
    telegram_request(
        "sendPhoto",
        data={
            "chat_id": CHAT_ID,
            "caption": offer_caption(offer),
            "parse_mode": "HTML",
        },
        files={"photo": ("offer.jpg", photo, "image/jpeg")},
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Post daily Europe offers to Telegram")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    offers = load_offers()
    history = load_history()
    initialize_cycle(history, offers)
    already_posted = posted_urls(history)
    cycle_urls = set(history["cycle_offer_urls"])

    candidates = [
        offer
        for offer in offers
        if offer["source_url"] in cycle_urls and offer["source_url"] not in already_posted
    ]
    if not candidates and not args.dry_run:
        offers = rebuild_homepage_cycle(history)
        candidates = offers

    selected = None
    photo = None
    for offer in candidates:
        downloaded = download_offer_photo(offer)
        if downloaded:
            selected = offer
            photo = downloaded
            break
        print(f"Skipped without reachable photo: {offer.get('title')}", file=sys.stderr)

    if selected is None or photo is None:
        raise RuntimeError("No unpublished Europe offer with a reachable photo")

    print(f"Prepared one Europe offer: {selected['title']} — {selected['price']}")

    if args.dry_run:
        return
    if not BOT_TOKEN or not CHAT_ID:
        raise RuntimeError("TELEGRAM_BOT_TOKEN and Telegram channel ID are required")

    send_offer(selected, photo)
    history["posts"].append(
        {
            "source_url": selected["source_url"],
            "title": selected["title"],
            "published_at": datetime.now(ZoneInfo("Europe/Moscow")).isoformat(),
        }
    )

    current_posted = posted_urls(history)
    cycle_complete = all(url in current_posted for url in history["cycle_offer_urls"])
    if cycle_complete:
        rebuild_homepage_cycle(history)
        print("Completed six-car cycle and refreshed homepage offers")

    save_history(history)
    print(f"Published one offer to Telegram channel {CHAT_ID}")


if __name__ == "__main__":
    main()
