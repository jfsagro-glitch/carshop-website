#!/usr/bin/env python3
"""
notify_cars.py — Telegram-уведомление об обновлении каталогов автомобилей.

Читает авто из Supabase, синхронизированные за последние N часов (NEW/updated),
формирует компактный дайджест и отправляет в Telegram-канал.

Usage (GitHub Actions):
  python notify_cars.py
  python notify_cars.py --hours 6
  python notify_cars.py --dry-run

Env vars:
  SUPABASE_URL         (e.g. https://xxx.supabase.co)
  SUPABASE_SERVICE_KEY (service role JWT)
  TELEGRAM_BOT_TOKEN
  TELEGRAM_CHAT_ID
"""
import argparse
import os
import sys
import json
import requests
from datetime import datetime, timezone, timedelta

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
TG_TOKEN     = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TG_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "")

HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
}

REGION_LABELS = {
    "georgia": ("🇬🇪", "Грузия"),
    "europe":  ("🇪🇺", "Европа"),
    "korea":   ("🇰🇷", "Корея"),
    "usa":     ("🇺🇸", "США"),
}


def fetch_new_cars(since_iso: str, region: str) -> list:
    """Получить авто из Supabase, синхронизированные после since_iso."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return []
    url = (
        f"{SUPABASE_URL}/rest/v1/cars"
        f"?region=eq.{region}"
        f"&is_active=eq.true"
        f"&created_at=gte.{since_iso}"
        f"&order=created_at.desc"
        f"&limit=50"
        f"&select=id,brand,model,year,price,currency,mileage,fuel_type,created_at"
    )
    r = requests.get(url, headers=HEADERS, timeout=15)
    if r.status_code != 200:
        print(f"  ✗ fetch cars ({region}): {r.status_code} {r.text[:200]}", file=sys.stderr)
        return []
    return r.json()


def fetch_total_cars(region: str) -> int:
    """Общее количество активных авто по региону."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return 0
    url = (
        f"{SUPABASE_URL}/rest/v1/cars"
        f"?region=eq.{region}"
        f"&is_active=eq.true"
        f"&select=id"
    )
    r = requests.get(url, headers={**HEADERS, "Prefer": "count=exact"}, timeout=10)
    content_range = r.headers.get("content-range", "0/0")
    try:
        return int(content_range.split("/")[-1])
    except (ValueError, IndexError):
        return 0


def format_price(price, currency: str) -> str:
    if not price:
        return "—"
    try:
        p = int(float(price))
        sym = "$" if currency in ("USD", "usd") else ("€" if currency in ("EUR", "eur") else "$")
        return f"{sym}{p:,}".replace(",", " ")
    except (ValueError, TypeError):
        return str(price)


def build_message(region: str, new_cars: list, total: int, hours: int) -> str:
    flag, label = REGION_LABELS.get(region, ("🌍", region.capitalize()))
    lines = [f"{flag} <b>Обновление каталога — {label}</b>"]

    if not new_cars:
        lines.append(f"  Нет новых поступлений за последние {hours} ч.")
        lines.append(f"  Всего в базе: <b>{total}</b> авто")
        return "\n".join(lines)

    lines.append(f"  🆕 Новых поступлений: <b>{len(new_cars)}</b> авто")
    lines.append(f"  📦 Всего в базе: <b>{total}</b> авто")
    lines.append("")

    # Компактный список — первые 5 позиций
    for car in new_cars[:5]:
        brand = car.get("brand") or "—"
        model = car.get("model") or ""
        year  = car.get("year")  or ""
        price = format_price(car.get("price"), car.get("currency") or "USD")
        mileage = car.get("mileage")
        mil_str = f", {int(mileage):,} км".replace(",", " ") if mileage else ""
        lines.append(f"  • {brand} {model} {year} — {price}{mil_str}")

    if len(new_cars) > 5:
        lines.append(f"  ... и ещё {len(new_cars) - 5} авто")

    page_map = {
        "georgia": "https://cmsauto.store/georgia-stock.html",
        "europe":  "https://cmsauto.store/europe-orders.html",
        "korea":   "https://cmsauto.store/korea-orders.html",
        "usa":     "https://cmsauto.store/usa-orders.html",
    }
    if region in page_map:
        lines.append("")
        lines.append(f"  🔗 <a href=\"{page_map[region]}\">Открыть каталог</a>")

    return "\n".join(lines)


def send_telegram(text: str) -> bool:
    if not TG_TOKEN or not TG_CHAT_ID:
        print("  ⚠ TG_TOKEN или TG_CHAT_ID не заданы — пропуск.", file=sys.stderr)
        return False
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    r = requests.post(
        url,
        json={
            "chat_id":    TG_CHAT_ID,
            "text":       text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        },
        timeout=10,
    )
    return r.status_code == 200


def main():
    parser = argparse.ArgumentParser(description="Уведомление Telegram об обновлении каталогов")
    parser.add_argument("--hours", type=int, default=5,
                        help="Считать новыми авто, добавленные за последние N часов (default: 5)")
    parser.add_argument("--regions", default="georgia,europe,korea",
                        help="Регионы через запятую (default: georgia,europe,korea)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Показать сообщение, не отправляя в Telegram")
    parser.add_argument("--only-new", action="store_true",
                        help="Отправлять только если есть новые авто")
    args = parser.parse_args()

    since = (datetime.now(timezone.utc) - timedelta(hours=args.hours)).isoformat()
    regions = [r.strip() for r in args.regions.split(",") if r.strip()]

    any_sent = False
    for region in regions:
        new_cars = fetch_new_cars(since, region)
        total    = fetch_total_cars(region)

        if args.only_new and not new_cars:
            continue

        msg = build_message(region, new_cars, total, args.hours)

        if args.dry_run:
            print(f"\n--- {region} ---")
            print(msg)
        else:
            ok = send_telegram(msg)
            status = "✓" if ok else "✗"
            print(f"  {status} Telegram {region}: {len(new_cars)} new, {total} total")
            any_sent = True

    if not any_sent and not args.dry_run and not args.only_new:
        # Нет ни одного региона с данными — вышлем общий статус
        total_all = sum(fetch_total_cars(r) for r in regions)
        send_telegram(f"✅ <b>Синхронизация завершена</b>\nВсего авто в базе: <b>{total_all}</b>")


if __name__ == "__main__":
    main()
