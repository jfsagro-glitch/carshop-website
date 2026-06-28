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
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OFFERS_PATH = ROOT / "data" / "home_featured_europe.json"
HISTORY_PATH = ROOT / "data" / "telegram_europe_history.json"
EUROPE_CATALOG_PATH = ROOT / "cars_europe_new.json"
SITE_URL = "https://cmsauto.store/?source=pwa"
EUROPE_URL = "https://cmsauto.store/europe-orders.html"
CONTACT_PHONE_DISPLAY = "+79184140636"
CONTACT_WHATSAPP_URL = "https://wa.me/79184140636"
CONTACT_TELEGRAM_URL = "https://t.me/expo_mir"
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = (
    os.environ.get("TELEGRAM_EUROPE_CHANNEL_ID", "").strip()
    or os.environ.get("TELEGRAM_CHAT_ID", "").strip()
)
# Public channel is fixed intentionally so stale GitHub secrets cannot redirect posts.
PUBLIC_CHANNEL_ID = "@expo_mir"
BLOCKED_CHANNEL_IDS = {"@testforcar444", "testforcar444", "https://t.me/testforcar444"}


def all_channel_ids() -> list[str]:
    """Return de-duplicated list of channel IDs to post to."""
    ids: list[str] = []
    if CHAT_ID and CHAT_ID not in BLOCKED_CHANNEL_IDS:
        ids.append(CHAT_ID)
    if PUBLIC_CHANNEL_ID and PUBLIC_CHANNEL_ID not in ids:
        ids.append(PUBLIC_CHANNEL_ID)
    return ids

IMAGE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ExpoMirBot/1.0)",
    "Referer": "https://www.autoscout24.de/",
}
MOSCOW_TZ = timezone(timedelta(hours=3), "MSK")


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


def refresh_prices_by_cbr() -> None:
    """Refresh Europe turnkey prices from the latest CBR rates before posting."""
    subprocess.run(
        ["node", "tools/update_europe_turnkey_prices.mjs"],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        ["node", "tools/build_home_europe_offers.mjs", "--exclude-history"],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        ["node", "tools/build_stock_counts.mjs"],
        cwd=ROOT,
        check=True,
    )


def load_europe_catalog_by_url() -> dict[str, dict]:
    if not EUROPE_CATALOG_PATH.exists():
        return {}
    cars = json.loads(EUROPE_CATALOG_PATH.read_text(encoding="utf-8"))
    if not isinstance(cars, list):
        return {}
    return {str(car.get("url")): car for car in cars if isinstance(car, dict) and car.get("url")}


def format_rub(value: object) -> str:
    amount = round(float(value or 0))
    return f"{amount:,}".replace(",", "\u00a0") + " ₽" if amount > 0 else ""


def format_eur(value: object) -> str:
    amount = round(float(value or 0))
    return f"{amount:,}".replace(",", "\u00a0") + " €" if amount > 0 else ""


def engine_label(car: dict) -> str:
    cc = float(car.get("engine_cc") or 0)
    source = str(car.get("engine_source") or "")
    if not source.startswith("autoscout24_") or cc < 500 or cc > 10000:
        return "уточняется"
    liters = f"{cc / 1000:.3f}".rstrip("0").rstrip(".").replace(".", ",")
    return f"{liters} {car.get('fuel_type') or ''}".strip()


def power_label(car: dict) -> str:
    hp = round(float(car.get("power_hp") or 0))
    kw = round(float(car.get("power_kw") or 0))
    if hp and kw:
        return f"{hp} л.с. / {kw} кВт"
    if hp:
        return f"{hp} л.с."
    if kw:
        return f"{kw} кВт"
    return "уточняется"


def refresh_offer_from_catalog(offer: dict, catalog_by_url: dict[str, dict]) -> dict:
    car = catalog_by_url.get(str(offer.get("source_url") or ""))
    if not car:
        return offer

    updated = dict(offer)
    details = dict(updated.get("details") or {})
    if car.get("turnkey_price_rub"):
        updated["price"] = format_rub(car.get("turnkey_price_rub"))
    if car.get("price"):
        updated["base_price"] = format_eur(car.get("price"))
    if car.get("year") or car.get("first_registration_year"):
        updated["year"] = str(car.get("year") or car.get("first_registration_year"))
    if car.get("mileage"):
        details["mileage"] = f"{round(float(car.get('mileage') or 0)):,}".replace(",", "\u00a0") + " км"
    details["engine"] = engine_label(car)
    details["power"] = power_label(car)
    updated["details"] = details
    updated["text_excerpt"] = (
        f"{car.get('full_title') or updated.get('title')}. "
        f"Цена в Европе {updated.get('base_price')}, стоимость под ключ в РФ {updated.get('price')}."
    )
    return updated


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


def moscow_today() -> str:
    return datetime.now(MOSCOW_TZ).date().isoformat()


def already_published_today(history: dict) -> bool:
    today = moscow_today()
    for post in history["posts"]:
        if not isinstance(post, dict):
            continue
        published_at = str(post.get("published_at") or "")
        if published_at.startswith(today):
            return True
    return False


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


def download_photo(url: str) -> bytes | None:
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
        return None
    return None


def download_offer_photos(offer: dict, limit: int = 10) -> list[bytes]:
    photos = []
    for url in image_urls(offer)[:limit]:
        photo = download_photo(url)
        if photo:
            photos.append(photo)
    return photos


def offer_caption(offer: dict, test: bool = False) -> str:
    details = offer.get("details") or {}
    lines = [
        f"🚘 <b>{html.escape(str(offer['title']))}</b>",
        f"💰 Под ключ в РФ: <b>{html.escape(str(offer['price']))}</b>",
        f"🇪🇺 Цена в Европе: {html.escape(str(offer.get('base_price') or 'уточняется'))}",
        f"🛣 Пробег: {html.escape(str(details['mileage']))}",
        f"⚙️ Двигатель: {html.escape(str(details['engine']))}",
        f"🏁 Мощность: {html.escape(str(details['power']))}",
        f'🔗 <a href="{html.escape(str(offer["source_url"]), quote=True)}">Открыть объявление</a>',
        "",
        f'🌐 <a href="{SITE_URL}">Другие предложения на сайте</a>',
        "",
        "Привезем абсолютно любой автомобиль 🚘 под ваш бюджет 🚕",
        "",
        "📞 Телефон для связи:",
        CONTACT_PHONE_DISPLAY,
        f'💬 <a href="{CONTACT_WHATSAPP_URL}">WhatsApp</a> · <a href="{CONTACT_TELEGRAM_URL}">Telegram</a>',
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


def send_offer_to(chat_id: str, offer: dict, photos: list[bytes], test: bool = False) -> None:
    """Send one offer (photos + caption) to a single chat/channel."""
    if len(photos) == 1:
        telegram_request(
            "sendPhoto",
            data={
                "chat_id": chat_id,
                "caption": offer_caption(offer, test=test),
                "parse_mode": "HTML",
            },
            files={"photo": ("offer.jpg", photos[0], "image/jpeg")},
        )
        return

    media = []
    files = {}
    for index, photo in enumerate(photos[:10]):
        attachment = f"photo{index}"
        item: dict = {
            "type": "photo",
            "media": f"attach://{attachment}",
        }
        if index == 0:
            item["caption"] = offer_caption(offer, test=test)
            item["parse_mode"] = "HTML"
        media.append(item)
        files[attachment] = (f"offer-{index}.jpg", photo, "image/jpeg")

    telegram_request(
        "sendMediaGroup",
        data={"chat_id": chat_id, "media": json.dumps(media, ensure_ascii=False)},
        files=files,
    )


def send_offer(offer: dict, photos: list[bytes], test: bool = False) -> None:
    """Send the offer to every configured channel."""
    channels = all_channel_ids()
    for chat_id in channels:
        try:
            send_offer_to(chat_id, offer, photos, test=test)
            print(f"Sent to channel {chat_id}")
        except RuntimeError as exc:
            print(f"ERROR sending to channel {chat_id}: {exc}", file=sys.stderr)
            raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Post daily Europe offers to Telegram")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--test", action="store_true", help="Send a test post without recording publication history")
    args = parser.parse_args()

    history = load_history()
    if already_published_today(history) and not args.test:
        print(f"Europe offer already published today ({moscow_today()}); skipping")
        return

    refresh_prices_by_cbr()
    offers = load_offers()
    catalog_by_url = load_europe_catalog_by_url()

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
    photos = []
    for offer in candidates:
        downloaded = download_offer_photos(offer, limit=10)
        if downloaded:
            selected = refresh_offer_from_catalog(offer, catalog_by_url)
            photos = downloaded
            break
        print(f"Skipped without reachable photo: {offer.get('title')}", file=sys.stderr)

    if selected is None or not photos:
        raise RuntimeError("No unpublished Europe offer with a reachable photo")

    print(f"Prepared one Europe offer: {selected['title']} — {selected['price']} ({len(photos)} photos)")

    if args.dry_run:
        return

    channels = all_channel_ids()
    if not BOT_TOKEN or not channels:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN and at least one channel ID "
            "(TELEGRAM_EUROPE_CHANNEL_ID or TELEGRAM_CHAT_ID) are required"
        )

    send_offer(selected, photos, test=args.test)
    if args.test:
        print(f"Sent test offer to {len(channels)} channel(s): {', '.join(channels)}")
        return

    history["posts"].append(
        {
            "source_url": selected["source_url"],
            "title": selected["title"],
            "published_at": datetime.now(MOSCOW_TZ).isoformat(),
        }
    )

    current_posted = posted_urls(history)
    cycle_complete = all(url in current_posted for url in history["cycle_offer_urls"])
    if cycle_complete:
        rebuild_homepage_cycle(history)
        print("Completed six-car cycle and refreshed homepage offers")

    save_history(history)
    print(f"Published one offer to {len(channels)} channel(s): {', '.join(channels)}")


if __name__ == "__main__":
    main()
