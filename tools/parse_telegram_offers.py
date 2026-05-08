#!/usr/bin/env python3
"""Parse public Telegram channel previews and prepare top car offers."""
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
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
ALLOWED_REGION_HINTS = ("сша", "copart", "iaai", "груз", "тбилиси", "европ", "герман", "mobile", "autoscout")
OUT_OF_SCOPE_REGION_HINTS = ("коре", "китай", "🇰🇷", "🇨🇳")


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def clean_number(value: str) -> str:
    value = clean_text(value)
    value = re.sub(r"\s+([,.])", r"\1", value)
    value = re.sub(r"([,.])\s+", r"\1", value)
    return value


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


def parse_mileage(text: str) -> str:
    patterns = [
        r"(?:пробег|mileage)[:\s]*([\d\s.,]{2,8})\s?(км|km|mi|миль)?",
        r"\b([\d\s.,]{2,8})\s?(км|km|mi|миль)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            value = clean_number(match.group(1))
            unit = match.group(2) or "км"
            return f"{value} {unit}"
    return ""


def parse_engine(text: str) -> str:
    patterns = [
        r"(?:двигатель|об[ъе]м)[:\s]*([0-9][.,][0-9]\s?(?:л|l)?(?:\s?[A-Za-zА-Яа-я0-9-]+)?)",
        r"[🛠⚙️]\s*([0-9][.,][0-9]\s?(?:л|l|TDI|TSI|TFSI|HEMI|Hybrid|турбо|бензин|дизель)?)",
        r"\b([0-9][.,][0-9])\s?(?:л|l)\b",
        r"\b([0-9][.,][0-9]\s?(?:TDI|TSI|TFSI|HEMI|Hybrid|турбо|бензин|дизель))\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return clean_text(match.group(1)).replace(",", ".")
    return ""


def estimate_power(title: str, engine: str) -> tuple[str, bool]:
    haystack = f"{title} {engine}".lower()
    rules = [
        ("5.7", "395 л.с."),
        ("hemi", "395 л.с."),
        ("elantra n line", "201 л.с."),
        ("audi a4 2.0", "252 л.с."),
        ("audi a6 2.0", "245 л.с."),
        ("3.0", "340-367 л.с."),
        ("2.0tdi", "150-200 л.с."),
        ("2.0 дизель", "150-200 л.с."),
        ("1.6", "123-201 л.с."),
        ("1.4", "125-150 л.с."),
    ]
    for needle, power in rules:
        if needle in haystack:
            return power, True
    return "", False


def parse_power(text: str) -> str:
    patterns = [
        r"(?:мощность|power)[:\s]*([\d\s]{2,4})\s?(?:л\.?\s?с\.?|hp|лс)",
        r"\b([\d\s]{2,4})\s?(?:л\.?\s?с\.?|hp|лс)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return f"{clean_text(match.group(1))} л.с."
    return ""


def parse_year(text: str) -> str:
    leading = re.search(r"^\s*(20(?:1[0-9]|2[0-6]))\s+[A-ZА-Я]", text, re.I)
    if leading:
        return leading.group(1)
    labeled = re.search(r"(?:год|year)[:\s]*\b(20(?:1[0-9]|2[0-6]))\b", text, re.I)
    if labeled:
        return labeled.group(1)
    years = [int(y) for y in re.findall(r"\b(20(?:1[0-9]|2[0-6]))\b", text)]
    if not years:
        return ""
    return str(min(years))


def parse_model(text: str) -> str:
    lower = text.lower()
    for keyword in MODEL_KEYWORDS:
        if keyword.lower() in lower:
            return keyword
    match = re.search(r"\b([A-ZА-Я][A-Za-zА-Яа-я-]+)\s+([A-ZА-Я0-9][A-Za-zА-Яа-я0-9-]{1,14})(?:\s+(?:Hybrid|AWD|xDrive|Quattro|GT|Line|G20|8))?", text)
    return clean_text(match.group(0)) if match else "Интересное авто"


def is_allowed_offer(text: str, region: str = "") -> bool:
    text_region = text.lower()
    combined = f"{region} {text}".lower()
    if not any(hint in combined for hint in ALLOWED_REGION_HINTS):
        return False
    if any(hint in text_region for hint in OUT_OF_SCOPE_REGION_HINTS) and not any(hint in text_region for hint in ALLOWED_REGION_HINTS):
        return False
    return True


def parse_images(post) -> list[str]:
    images = []
    for img in post.select("a.tgme_widget_message_photo_wrap"):
        style = img.get("style", "")
        match = re.search(r"url\(['\"]?([^'\")]+)", style)
        if match and match.group(1) not in images:
            images.append(match.group(1))
    for media in post.select(".tgme_widget_message_video_thumb"):
        style = media.get("style", "")
        match = re.search(r"url\(['\"]?([^'\")]+)", style)
        if match and match.group(1) not in images:
            images.append(match.group(1))
    return images


def post_score(text: str, priority: int, images: list[str], year: str, price: str, details: dict) -> int:
    lower = text.lower()
    score = priority * 10
    score += 22 if images else 0
    score += min(len(images), 5) * 2
    score += 20 if price else 0
    score += 8 if year and int(year) >= 2021 else 0
    score += 10 if details.get("engine") else 0
    score += 8 if details.get("mileage") else 0
    score += 6 if details.get("power") else 0
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
    details = item.get("details", {})
    specs = [
        f"⚙️ Двигатель: {details.get('engine') or 'уточняется'}",
        f"🐎 Мощность: {details.get('power') or 'уточняется'}",
        f"🛣️ Пробег: {details.get('mileage') or 'уточняется'}",
    ]
    specs_text = "\n".join(line for line in specs if line)
    return (
        f"🔥 {title}\n\n"
        f"📍 Направление: {region}\n"
        f"📅 Год: {year}\n"
        f"💰 Ориентир: {price}\n"
        f"{specs_text}\n"
        f"{facts_text}\n\n"
        f"✅ Проверим VIN, историю, повреждения и полный бюджет под ключ.\n"
        f"🚚 Доставка, растаможка и оформление через EXPO MIR.\n"
        f"📲 Напишите менеджеру: https://wa.me/996755666805\n"
        f"Источник мониторинга: {source}"
    )


def prepare_saved_offer(item: dict) -> dict:
    text = item.get("text_excerpt", "")
    if not is_allowed_offer(text, item.get("region", "")):
        item["quality"] = "out_of_scope"
    parsed_year = parse_year(text)
    if parsed_year:
        item["year"] = parsed_year
    details = item.get("details") or {}
    if not details.get("engine"):
        details["engine"] = parse_engine(text)
    if not details.get("mileage"):
        details["mileage"] = parse_mileage(text)
    if not details.get("power"):
        power = parse_power(text)
        power_estimated = False
        if not power:
            power, power_estimated = estimate_power(item.get("title", ""), details.get("engine", ""))
        details["power"] = power
        details["power_estimated"] = power_estimated
    item["details"] = details
    if "images" not in item:
        item["images"] = [item["image"]] if item.get("image") else []
    if not item.get("quality"):
        item["quality"] = "strict" if (details.get("engine") or details.get("mileage") or details.get("power")) else "price_photo"
    item["score"] = int(item.get("score") or post_score(text, 1, item.get("images", []), item.get("year", ""), item.get("price", ""), details))
    item["telegram_post"] = build_caption(item)
    return item


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
        images = parse_images(post)
        post_url = post.get("data-post", "")
        post_link = f"https://t.me/{post_url}" if post_url else url
        year = parse_year(text)
        price = parse_price(text)
        title = parse_model(text)
        engine = parse_engine(text)
        power = parse_power(text)
        power_estimated = False
        if not is_allowed_offer(text, channel.get("region", "")):
            continue
        if not price or not images:
            continue
        if not power:
            power, power_estimated = estimate_power(title, engine)
        details = {
            "engine": engine,
            "power": power,
            "power_estimated": power_estimated,
            "mileage": parse_mileage(text),
        }
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
            "image": images[0],
            "images": images,
            "details": details,
            "text_excerpt": text[:520],
            "facts": facts,
        }
        item["score"] = post_score(text, int(channel.get("priority", 1)), images, year, price, details)
        item["quality"] = "strict" if (details["engine"] or details["mileage"] or details["power"]) else "price_photo"
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
    previous_offers = []
    previous_path = Path(args.out)
    if previous_path.exists():
        try:
            previous_payload = json.load(open(previous_path, encoding="utf-8"))
            previous_offers = [prepare_saved_offer(item) for item in previous_payload.get("offers", [])]
        except Exception:
            previous_offers = []
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
    for item in [*previous_offers, *all_items]:
        key = (item["title"].lower(), item.get("price", ""), item["channel"])
        if key not in dedup or item["score"] >= dedup[key]["score"]:
            dedup[key] = item
    in_scope = [item for item in dedup.values() if item.get("quality") != "out_of_scope"]
    strict = [item for item in in_scope if item.get("quality") == "strict"]
    relaxed = [item for item in in_scope if item.get("quality") != "strict"]
    top = sorted(strict, key=lambda item: item["score"], reverse=True)[:args.limit]
    if len(top) < args.limit:
        top += sorted(relaxed, key=lambda item: item["score"], reverse=True)[: args.limit - len(top)]

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
        photos = "\n".join(f"- {src}" for src in item.get("images", [])[:8]) or "-"
        md += [f"## {i}. {item['title']} — {item['source']}", "", item["telegram_post"], "", "Фото:", photos, ""]
    Path(args.markdown).write_text("\n".join(md), encoding="utf-8")
    print(f"saved={args.out} offers={len(top)} parsed={len(all_items)} errors={len(errors)}")


if __name__ == "__main__":
    main()
