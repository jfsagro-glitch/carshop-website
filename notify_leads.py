"""
notify_leads.py — GitHub Actions step: notify new leads to Telegram.

Reads leads with notified_at IS NULL from Supabase (service key),
sends each to Telegram Bot API, then marks notified_at = NOW().

Usage (GitHub Actions):
  python notify_leads.py

Env vars required:
  SUPABASE_URL         (e.g. https://xxx.supabase.co)
  SUPABASE_SERVICE_KEY (service role JWT)
  TELEGRAM_BOT_TOKEN
  TELEGRAM_CHAT_ID
"""
import os
import sys
import json
import requests
from datetime import datetime, timezone

SUPABASE_URL       = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY       = os.environ.get("SUPABASE_SERVICE_KEY", "")
TG_TOKEN           = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TG_CHAT_ID         = os.environ.get("TELEGRAM_CHAT_ID", "")

HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
}

MAX_NOTIFY = 20  # safety cap per run


def fetch_new_leads() -> list:
    """Fetch leads where notified_at is NULL, ordered by created_at asc."""
    url = (
        f"{SUPABASE_URL}/rest/v1/leads"
        f"?notified_at=is.null"
        f"&order=created_at.asc"
        f"&limit={MAX_NOTIFY}"
        f"&select=id,type,status,name,phone,email,message,car_info,source_page,created_at"
    )
    r = requests.get(url, headers=HEADERS, timeout=15)
    if r.status_code != 200:
        print(f"  ✗ fetch leads: {r.status_code} {r.text[:200]}")
        return []
    return r.json()


def mark_notified(lead_id: int) -> bool:
    url = f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead_id}"
    r = requests.patch(
        url,
        headers=HEADERS,
        json={"notified_at": datetime.now(timezone.utc).isoformat()},
        timeout=15,
    )
    return r.status_code in (200, 204)


def send_telegram(text: str) -> bool:
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    r = requests.post(
        url,
        json={"chat_id": TG_CHAT_ID, "text": text, "parse_mode": "HTML"},
        timeout=10,
    )
    return r.status_code == 200


def format_lead(lead: dict) -> str:
    lead_type_map = {
        "car_order":     "🚗 Заявка на авто",
        "parts_request": "🔧 Запрос запчастей",
        "vin_search":    "🔍 VIN-поиск",
        "callback":      "📞 Обратный звонок",
        "price_check":   "💰 Запрос цены",
    }
    lead_type = lead_type_map.get(lead.get("type", ""), f"📋 {lead.get('type', '?')}")
    name      = lead.get("name")  or "—"
    phone     = lead.get("phone") or "—"
    email     = lead.get("email") or "—"
    message   = lead.get("message") or ""
    page      = lead.get("source_page") or "—"
    created   = lead.get("created_at", "")[:16].replace("T", " ")

    car_info  = lead.get("car_info") or {}
    car_line  = ""
    if isinstance(car_info, dict):
        parts = []
        if car_info.get("brand"):
            parts.append(f"{car_info['brand']} {car_info.get('model','')}")
        if car_info.get("year"):
            parts.append(str(car_info["year"]))
        if car_info.get("price"):
            parts.append(f"${car_info['price']:,.0f}" if isinstance(car_info["price"], (int, float)) else str(car_info["price"]))
        if parts:
            car_line = f"\n🚘 <b>Авто:</b> {' '.join(parts)}"
    elif isinstance(car_info, str) and car_info:
        car_line = f"\n🚘 <b>Авто:</b> {car_info[:100]}"

    msg_line = f"\n💬 <b>Сообщение:</b> {message[:300]}" if message else ""

    return (
        f"<b>{lead_type}</b>  #{lead['id']}\n"
        f"🕐 {created}\n"
        f"👤 <b>Имя:</b> {name}\n"
        f"📱 <b>Тел:</b> {phone}\n"
        f"📧 <b>Email:</b> {email}"
        f"{car_line}"
        f"{msg_line}\n"
        f"📍 <b>Страница:</b> {page}"
    )


def main():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("SUPABASE_URL / SUPABASE_SERVICE_KEY not set — skip")
        sys.exit(0)
    if not TG_TOKEN or not TG_CHAT_ID:
        print("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set — skip")
        sys.exit(0)

    leads = fetch_new_leads()
    print(f"New leads to notify: {len(leads)}")

    notified = 0
    for lead in leads:
        text = format_lead(lead)
        if send_telegram(text):
            if mark_notified(lead["id"]):
                notified += 1
                print(f"  ✓ lead #{lead['id']} notified")
            else:
                print(f"  ✗ lead #{lead['id']} — could not mark notified")
        else:
            print(f"  ✗ lead #{lead['id']} — Telegram send failed")

    print(f"Done: {notified}/{len(leads)} notified")


if __name__ == "__main__":
    main()
