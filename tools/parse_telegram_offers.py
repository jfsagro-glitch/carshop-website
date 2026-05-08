#!/usr/bin/env python3
"""Parse public Telegram channel previews and prepare top car offers."""
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
CHANNELS_PATH = ROOT / "data" / "telegram_car_channels.json"
OUT_JSON = ROOT / "data" / "telegram_top_offers.json"
OUT_MD = ROOT / "data" / "telegram_top_posts.md"

UA = "Mozilla/5.0 (compatible; EXPO-MIR Telegram offer monitor; +https://cmsauto.store/)"

MODEL_KEYWORDS = [
    "Golf 8", "BMW G20", "BMW 3", "BMW 320", "BMW 330", "Audi A4", "Audi A5",
    "Arteon", "Prius", "Camry Hybrid", "Camry", "Tesla Model 3", "Model 3",
    "Encore GX", "Tucson Hybrid", "Tucson", "Corolla", "K5", "Sportage",
    "Sorento", "RAV4", "Lexus", "Mercedes", "Porsche", "Volkswagen", "VAG",
]
SELLING_WORDS = [
    "под ключ", "цена", "стоимость", "доставка", "растамож", "vin", "пробег",
    "год", "купили", "выкуп", "лот", "copart", "iaai", "грузии", "германии",
    "mobile", "autoscout", "клиент", "выда", "расчет", "расчёт",
]
BAD_WORDS = ["розыгрыш", "вакансия", "обучение", "курс", "подписывай", "новости", "утильсбор"]


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def parse_price(text: str) -> str:
    patterns = [
        r"(?:(?:\$|USD)\s?[\d\s.,]{4,}|[\d\s.,]{4,}\s?(?:\$|USD))",
        r"(?:€\s?[\d\s.,]{4,}|[\d\s.,]{4,}\s?€)",
        r"(?:[\d\s.,]{6,}\s?(?:₽|руб|rub))",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return clean_text(match.group(0))
    return ""


def parse_year(text: str) -> str:
    years = [int(y) for y in re.findall(r"\b(20(?:1[8-9]|2[0-6]))\b", text)]
    if not years:
        return ""
    return str(max(years))


def parse_model(text: str) -> str:
    lower = text.lower()
    for keyword in MODEL_KEYWORDS:
        if keyword.lower() in lower:
            return keyword
    match = re.search(r"\b([A-ZА-Я][A-Za-zА-Яа-я-]+)\s+([A-ZА-Я0-9][A-Za-zА-Яа-я0-9-]{1,14})(?:\s+(?:Hybrid|AWD|xDrive|Quattro|GT|Line|G20|8))?", text)
    return clean_text(match.group(0)) if match else "Интересное авто"


def parse_image(post) -> str:
    img = post.select_one("a.tgme_widget_message_photo_wrap")
    if img:
        style = img.get("style", "")
        match = re.search(r"url\(['\"]?([^'\")]+)", style)
        if match:
            return match.group(1)
    media = post.select_one(".tgme_widget_message_video_thumb")
    if media:
        style = media.get("style", "")
        match = re.search(r"url\(['\"]?([^'\")]+)", style)
        if match:
            return match.group(1)
    return ""


def post_score(text: str, priority: int, image: str, year: str, price: str) -> int:
    lower = text.lower()
    score = priority * 10
    score += 18 if image else 0
    score += 14 if price else 0
    score += 8 if year and int(year) >= 2021 else 0
    score += sum(5 for word in SELLING_WORDS if word in lower)
    score += sum(8 for model in MODEL_KEYWORDS if model.lower() in lower)
    score -= sum(14 for word in BAD_WORDS if word in lower)
    score -= 18 if len(text) < 80 else 0
    return score


def build_caption(item: dict) -> str:
    title = item["title"]
    price = item.get("price") or "цену уточним по запросу"
    year = item.get("year") or "год уточним"
    region = item.get("region", "под заказ")
    source = item.get("source", "")
    facts = item.get("facts", [])
    facts_text = "\n".join(f"• {fact}" for fact in facts[:5])
    return (
        f"🔥 {title}\n\n"
        f"📍 Направление: {region}\n"
        f"📅 Год: {year}\n"
        f"💰 Ориентир: {price}\n"
        f"{facts_text}\n\n"
        f"✅ Проверим VIN, историю, повреждения и полный бюджет под ключ.\n"
        f"🚚 Доставка, растаможка и оформление через EXPO MIR.\n"
        f"📲 Напишите менеджеру: https://wa.me/996755666805\n"
        f"Источник мониторинга: {source}"
    )


def parse_channel(channel: dict, limit_posts: int) -> list[dict]:
    username = channel["username"].lstrip("@")
    url = f"https://t.me/s/{username}"
    resp = requests.get(url, headers={"User-Agent": UA}, timeout=25)
    if resp.url.rstrip("/").endswith(f"t.me/{username}") and "/s/" not in resp.url:
        return []
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    items = []
    for post in soup.select(".tgme_widget_message")[-limit_posts:]:
        text_el = post.select_one(".tgme_widget_message_text")
        text = clean_text(text_el.get_text(" ", strip=True) if text_el else "")
        if not text:
            continue
        image = parse_image(post)
        post_url = post.get("data-post", "")
        post_link = f"https://t.me/{post_url}" if post_url else url
        year = parse_year(text)
        price = parse_price(text)
        title = parse_model(text)
        facts = []
        if "vin" in text.lower():
            facts.append("есть VIN/данные для проверки")
        if re.search(r"пробег|mileage|км|km", text, re.I):
            facts.append("указан пробег")
        if re.search(r"доставка|растамож|под ключ", text, re.I):
            facts.append("есть расчёт под ключ/логистика")
        if re.search(r"copart|iaai|лот", text, re.I):
            facts.append("аукционный лот США")
        if re.search(r"груз", text, re.I):
            facts.append("актуально для рынка Грузии")
        item = {
            "channel": username,
            "region": channel.get("region", ""),
            "source": f"@{username}",
            "source_url": post_link,
            "title": title,
            "year": year,
            "price": price,
            "image": image,
            "text_excerpt": text[:520],
            "facts": facts,
        }
        item["score"] = post_score(text, int(channel.get("priority", 1)), image, year, price)
        item["telegram_post"] = build_caption(item)
        items.append(item)
    return items


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse public Telegram car offers")
    parser.add_argument("--channels", default=str(CHANNELS_PATH))
    parser.add_argument("--out", default=str(OUT_JSON))
    parser.add_argument("--markdown", default=str(OUT_MD))
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--posts-per-channel", type=int, default=12)
    args = parser.parse_args()

    channels = json.load(open(args.channels, encoding="utf-8"))
    all_items = []
    errors = []
    for channel in channels:
        try:
            items = parse_channel(channel, args.posts_per_channel)
            all_items.extend(items)
            print(f"@{channel['username'].lstrip('@')}: {len(items)} posts")
        except Exception as exc:
            errors.append({"channel": channel["username"], "error": str(exc)[:220]})
            print(f"@{channel['username'].lstrip('@')}: ERROR {exc}")

    dedup = {}
    for item in all_items:
        key = (item["title"].lower(), item.get("price", ""), item.get("year", ""), item["channel"])
        if key not in dedup or item["score"] > dedup[key]["score"]:
            dedup[key] = item
    top = sorted(dedup.values(), key=lambda item: item["score"], reverse=True)[:args.limit]

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_count": len(channels),
        "parsed_posts": len(all_items),
        "errors": errors,
        "offers": top,
    }
    Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md = ["# Telegram top offers", "", f"Generated: {payload['generated_at']}", ""]
    for i, item in enumerate(top, 1):
        md += [f"## {i}. {item['title']} — {item['source']}", "", item["telegram_post"], "", f"Фото: {item.get('image') or '-'}", ""]
    Path(args.markdown).write_text("\n".join(md), encoding="utf-8")
    print(f"saved={args.out} offers={len(top)} parsed={len(all_items)} errors={len(errors)}")


if __name__ == "__main__":
    main()
