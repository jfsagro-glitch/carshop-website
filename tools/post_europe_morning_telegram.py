#!/usr/bin/env python3
"""Post the current homepage Europe selection to a Telegram channel."""

from __future__ import annotations

import argparse
import html
import io
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OFFERS_PATH = ROOT / "data" / "home_featured_europe.json"
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


def offer_caption(offer: dict, first: bool = False) -> str:
    details = offer.get("details") or {}
    lines = []
    if first:
        lines.extend(
            [
                f"🇪🇺 <b>Утренняя подборка EXPO MIR · {datetime.now(ZoneInfo('Europe/Moscow')).strftime('%d.%m.%Y')}</b>",
                "Актуальные предложения из Европы по критериям главной страницы.",
                "",
            ]
        )
    lines.extend(
        [
            f"🚘 <b>{html.escape(str(offer['title']))}</b>",
            f"💰 Под ключ в РФ: <b>{html.escape(str(offer['price']))}</b>",
            f"🇪🇺 Цена в Европе: {html.escape(str(offer.get('base_price') or 'уточняется'))}",
            f"🛣 Пробег: {html.escape(str(details['mileage']))}",
            f"⚙️ Двигатель: {html.escape(str(details['engine']))}",
            f"🏁 Мощность: {html.escape(str(details['power']))}",
            f'🔗 <a href="{html.escape(str(offer["source_url"]), quote=True)}">Открыть объявление</a>',
        ]
    )
    if first:
        lines.extend(["", f'🌐 <a href="{SITE_URL}">Смотреть подборку на сайте</a>'])
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


def send_album(offers_with_photos: list[tuple[dict, bytes]]) -> None:
    if len(offers_with_photos) == 1:
        offer, photo = offers_with_photos[0]
        telegram_request(
            "sendPhoto",
            data={
                "chat_id": CHAT_ID,
                "caption": offer_caption(offer, first=True),
                "parse_mode": "HTML",
            },
            files={"photo": ("offer.jpg", photo, "image/jpeg")},
        )
        return

    media = []
    files = {}
    for index, (offer, photo) in enumerate(offers_with_photos):
        attachment = f"photo{index}"
        media.append(
            {
                "type": "photo",
                "media": f"attach://{attachment}",
                "caption": offer_caption(offer, first=index == 0),
                "parse_mode": "HTML",
            }
        )
        files[attachment] = (f"offer-{index}.jpg", photo, "image/jpeg")

    telegram_request(
        "sendMediaGroup",
        data={"chat_id": CHAT_ID, "media": json.dumps(media, ensure_ascii=False)},
        files=files,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Post daily Europe offers to Telegram")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    offers = load_offers()
    prepared = []
    for offer in offers:
        downloaded = download_offer_photo(offer)
        if downloaded:
            prepared.append((offer, downloaded))
        else:
            print(f"Skipped without reachable photo: {offer.get('title')}", file=sys.stderr)

    if not prepared:
        raise RuntimeError("No Europe offers with reachable photos")

    print(f"Prepared {len(prepared)} Europe offers:")
    for offer, _ in prepared:
        print(f" - {offer['title']} — {offer['price']}")

    if args.dry_run:
        return
    if not BOT_TOKEN or not CHAT_ID:
        raise RuntimeError("TELEGRAM_BOT_TOKEN and Telegram channel ID are required")

    send_album(prepared)
    print(f"Published {len(prepared)} offers to Telegram channel {CHAT_ID}")


if __name__ == "__main__":
    main()
