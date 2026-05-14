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
PASSABLE_PATH = ROOT / "data" / "passable_import_filter.json"

UA = "Mozilla/5.0 (compatible; EXPO-MIR Telegram offer monitor; +https://cmsauto.store/)"

MODEL_KEYWORDS = [
    "Golf 8", "BMW G20", "BMW 3", "BMW 320", "BMW 330", "Audi A4", "Audi A5",
    "Arteon", "Prius", "Camry Hybrid", "Camry", "Tesla Model 3", "Model 3",
    "Encore GX", "Tucson Hybrid", "Tucson", "Corolla", "K5", "Sportage",
    "Sorento", "RAV4", "Lexus", "Mercedes", "Porsche", "Volkswagen", "VAG",
]
SELLING_WORDS = [
    "под ключ", "цена", "стоимость", "доставка", "растамож", "тамож", "рф", "росси", "vin", "пробег",
    "год", "купили", "выкуп", "лот", "copart", "iaai", "грузии", "германии",
    "mobile", "autoscout", "клиент", "выда", "расчет", "расчёт",
]
BAD_WORDS = ["розыгрыш", "вакансия", "обучение", "курс", "подписывай", "новости", "утильсбор"]
ALLOWED_REGION_HINTS = ("сша", "usa", "copart", "iaai", "груз", "тбилиси", "европ", "герман", "mobile", "autoscout")
OUT_OF_SCOPE_REGION_HINTS = ("коре", "китай", "🇰🇷", "🇨🇳")
RB_HINTS = (
    "цена в рб",
    "в рб",
    "для рб",
    "рб со",
    "беларус",
    "белорус",
    "льготой",
    "+375",
    "a4e.by",
)
DELIVERY_TO_RF_HINTS = (
    "под ключ",
    "доставка",
    "растамож",
    "тамож",
    "оформлен",
    "в рф",
    "для рф",
    "росси",
    "москв",
    "спб",
)


def load_passable_catalog() -> list[dict]:
    try:
        payload = json.load(open(PASSABLE_PATH, encoding="utf-8"))
    except Exception:
        return []
    return [
        item for item in payload.get("vehicle_whitelist", [])
        if set(item.get("regions", [])) & {"georgia", "usa", "europe"}
    ]


PASSABLE_CATALOG = load_passable_catalog()


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def build_model_keywords() -> list[str]:
    keywords = set(MODEL_KEYWORDS)
    for rule in PASSABLE_CATALOG:
        brand = clean_text(rule.get("brand", ""))
        model = clean_text(rule.get("model", ""))
        if model:
            keywords.add(model)
        if brand and model:
            keywords.add(f"{brand} {model}")
    return sorted(keywords, key=len, reverse=True)


MODEL_KEYWORDS = build_model_keywords()


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
        r"(?:мощность|power)[:\s]*([\d\s]{2,4}\s?[-–]\s?[\d\s]{2,4})\s?(?:л\.?\s?с\.?|hp|лс)",
        r"(?:мощность|power)[:\s]*([\d\s]{2,4})\s?(?:л\.?\s?с\.?|hp|лс)",
        r"\b([\d\s]{2,4}\s?[-–]\s?[\d\s]{2,4})\s?(?:л\.?\s?с\.?|hp|лс)\b",
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


def fill_details_from_rule(details: dict, rule: dict | None) -> dict:
    if not rule:
        return details
    if not details.get("engine"):
        details["engine"] = f"{rule.get('engine')} {rule.get('fuel')}".strip()
    if not details.get("power"):
        details["power"] = f"{rule.get('hp')} л.с. / {rule.get('kw')} кВт"
    else:
        details["power"] = f"{rule.get('hp')} л.с. / {rule.get('kw')} кВт"
    details["power_estimated"] = True
    return details


def is_allowed_offer(text: str, region: str = "") -> bool:
    text_region = text.lower()
    combined = f"{region} {text}".lower()
    if any(hint in combined for hint in RB_HINTS):
        return False
    if any(hint in text_region for hint in OUT_OF_SCOPE_REGION_HINTS):
        return False
    if not any(hint in combined for hint in ALLOWED_REGION_HINTS):
        return False
    return True


def has_delivery_to_rf(text: str) -> bool:
    lower = text.lower()
    return any(hint in lower for hint in DELIVERY_TO_RF_HINTS)


def normalize_region(region: str, text: str = "") -> str:
    combined = f"{region} {text}".lower()
    parts = []
    if any(hint in combined for hint in ("груз", "тбилиси")):
        parts.append("Грузия")
    if any(hint in combined for hint in ("сша", "usa", "copart", "iaai")):
        parts.append("США")
    if any(hint in combined for hint in ("европ", "герман", "mobile", "autoscout")):
        parts.append("Европа")
    return " / ".join(parts) or "Грузия / США / Европа"


def normalize_match_text(value: str) -> str:
    return re.sub(r"[^a-zа-я0-9]+", " ", str(value or "").lower()).strip()


def parse_engine_liters(value: str) -> float:
    match = re.search(r"\d+(?:[.,]\d+)?", str(value or "").replace(",", "."))
    return float(match.group(0)) if match else 0.0


def matches_passable_catalog(title: str, engine: str, text: str, region: str = "") -> tuple[bool, dict | None]:
    if not PASSABLE_CATALOG:
        return True, None
    combined_region = f"{region} {text}".lower()
    region_keys = set()
    if any(hint in combined_region for hint in ("груз", "тбилиси")):
        region_keys.add("georgia")
    if any(hint in combined_region for hint in ("сша", "usa", "copart", "iaai")):
        region_keys.add("usa")
    if any(hint in combined_region for hint in ("европ", "герман", "mobile", "autoscout")):
        region_keys.add("europe")
    haystack = normalize_match_text(f"{title} {text}")
    engine_value = parse_engine_liters(engine)
    best = None
    best_score = -1
    for rule in PASSABLE_CATALOG:
        rule_regions = set(rule.get("regions", []))
        if region_keys and not (region_keys & rule_regions):
            continue
        brand = normalize_match_text(rule.get("brand", ""))
        model = normalize_match_text(rule.get("model", ""))
        if brand and brand not in haystack:
            continue
        if model and model not in haystack:
            continue
        rule_engine = parse_engine_liters(rule.get("engine", ""))
        if engine_value and rule_engine and abs(engine_value - rule_engine) > 0.11:
            continue
        hp = int(rule.get("hp") or 0)
        kw = int(rule.get("kw") or 0)
        if hp > 160 or (kw > 116 and not hp):
            continue
        score = len(model) + (8 if engine_value and rule_engine else 0)
        if score > best_score:
            best = rule
            best_score = score
    return bool(best), best


def has_required_offer_fields(item: dict) -> bool:
    details = item.get("details") or {}
    text = item.get("text_excerpt", "")
    images = item.get("images") or ([item.get("image")] if item.get("image") else [])
    passable, rule = matches_passable_catalog(item.get("title", ""), details.get("engine", ""), text, item.get("region", ""))
    if passable and rule:
        details = fill_details_from_rule(details, rule)
        item["details"] = details
    return all(
        [
            item.get("year"),
            item.get("price"),
            details.get("engine"),
            details.get("power"),
            details.get("mileage"),
            images,
            is_allowed_offer(text, item.get("region", "")),
            has_delivery_to_rf(text) or has_delivery_to_rf(item.get("telegram_post", "")),
            passable,
        ]
    )


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
        f"📍 Направление: {normalize_region(region, item.get('text_excerpt', ''))}\n"
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
    if has_required_offer_fields(item):
        item["quality"] = "strict"
    else:
        item["quality"] = "out_of_scope"
    item["region"] = normalize_region(item.get("region", ""), text)
    item["score"] = int(item.get("score") or post_score(text, 1, item.get("images", []), item.get("year", ""), item.get("price", ""), details))
    item["telegram_post"] = build_caption(item)
    return item


def local_image_urls(value) -> list[str]:
    if not isinstance(value, list):
        return []
    urls = []
    for item in value:
        url = item if isinstance(item, str) else item.get("url", "")
        if url and url not in urls:
            urls.append(url)
    return urls


def format_local_price(item: dict, default_currency: str = "") -> str:
    price = item.get("price")
    if not price:
        return ""
    try:
        value = int(round(float(price)))
    except Exception:
        return str(price)
    currency = str(item.get("price_currency") or item.get("currency") or default_currency or "").upper()
    if currency == "EUR":
        return f"{value:,} €".replace(",", " ")
    if currency == "USD":
        return f"${value:,}".replace(",", " ")
    return f"{value:,} ₽".replace(",", " ")


def local_year_month(item: dict) -> int:
    year = int(item.get("year") or item.get("first_registration_year") or 0)
    month = int(item.get("month") or item.get("first_registration_month") or 0)
    if not month:
        registration = str(item.get("first_registration") or item.get("productionDate") or "")
        match = re.search(r"\b(0?[1-9]|1[0-2])[./-](20\d{2})\b", registration)
        if match:
            year = int(match.group(2))
            month = int(match.group(1))
    return year * 100 + month if year and month else year * 100


def build_local_fallback_offer(item: dict, region_label: str, source_label: str, source_type: str, default_currency: str) -> dict | None:
    images = local_image_urls(item.get("images", []))
    if not images:
        return None
    hp = int(float(item.get("power_hp") or 0))
    kw = int(float(item.get("power_kw") or 0))
    if hp > 160 or (kw > 116 and not hp):
        return None
    year = str(item.get("year") or item.get("first_registration_year") or "")
    title = clean_text(f"{item.get('brand', '')} {item.get('model', '')} {year}").strip()
    details = {
        "engine": clean_text(f"{item.get('engine', '')} {item.get('fuel_type') or item.get('fuel') or ''}").strip() or "уточняется",
        "power": clean_text(f"{hp or ''} л.с. / {kw or ''} кВт").strip(" /") if (hp or kw) else "уточняется",
        "mileage": f"{int(item.get('mileage')):,} км".replace(",", " ") if item.get("mileage") else "уточняется",
    }
    offer = {
        "channel": source_type,
        "region": region_label,
        "source": source_label,
        "source_type": "catalog_fallback",
        "source_url": item.get("url") or item.get("link") or "#",
        "title": title,
        "year": year,
        "price": format_local_price(item, default_currency) or "Цена по запросу",
        "image": images[0],
        "images": images[:12],
        "details": details,
        "text_excerpt": (
            f"{title}: проходной автомобиль {region_label}, {details['engine']}, {details['power']}, "
            "с фото, доставкой, растаможкой и оформлением в РФ."
        ),
        "facts": [
            "проходной возраст 3-5 лет",
            "до 160 л.с. / 116 кВт",
            "доставка и растаможка в РФ",
        ],
        "score": 80 + (local_year_month(item) % 10000),
        "quality": "candidate",
    }
    offer["telegram_post"] = build_caption(offer)
    return offer


def load_catalog_fallbacks(limit: int, used_keys: set[tuple[str, str]]) -> list[dict]:
    sources = [
        (ROOT / "cars_georgia_stock.json", "Грузия", "MyAuto Georgia", "myauto_georgia", "USD"),
        (ROOT / "cars_europe_new.json", "Европа", "AutoScout24 / mobile.de", "europe_catalog", "EUR"),
    ]
    buckets = []
    for path, region, source, source_type, default_currency in sources:
        try:
            rows = json.load(open(path, encoding="utf-8"))
        except Exception:
            rows = []
        offers = []
        for item in rows:
            offer = build_local_fallback_offer(item, region, source, source_type, default_currency)
            if not offer:
                continue
            key = (offer["title"].lower(), offer.get("price", ""))
            if key in used_keys:
                continue
            used_keys.add(key)
            offers.append(offer)
        buckets.append(sorted(offers, key=lambda offer: offer.get("score", 0), reverse=True))
    result = []
    while len(result) < limit and any(buckets):
        for bucket in buckets:
            if bucket and len(result) < limit:
                result.append(bucket.pop(0))
    return result


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
        if not price or not year or not images:
            continue
        if not power:
            power, power_estimated = estimate_power(title, engine)
        details = {
            "engine": engine,
            "power": power,
            "power_estimated": power_estimated,
            "mileage": parse_mileage(text),
        }
        passable, rule = matches_passable_catalog(title, details["engine"], text, channel.get("region", ""))
        if not passable:
            continue
        if rule:
            title = f"{rule.get('brand')} {rule.get('model')}"
            details = fill_details_from_rule(details, rule)
        if not details["mileage"]:
            details["mileage"] = "уточняется"
        has_delivery = has_delivery_to_rf(text)
        facts = []
        if "vin" in text.lower():
            facts.append("есть VIN/данные для проверки")
        if re.search(r"пробег|mileage|км|km", text, re.I):
            facts.append("указан пробег")
        if re.search(r"доставка|растамож|под ключ", text, re.I):
            facts.append("есть расчёт под ключ/логистика")
        if re.search(r"рф|росси|москв|спб|растамож|тамож", text, re.I):
            facts.append("доставка и растаможка в РФ")
        if not has_delivery:
            facts.append("доставку и растаможку в РФ рассчитаем")
        if re.search(r"copart|iaai|лот", text, re.I):
            facts.append("аукционный лот США")
        if re.search(r"груз", text, re.I):
            facts.append("актуально для рынка Грузии")
        item = {
            "channel": username,
            "region": normalize_region(channel.get("region", ""), text),
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
        item["quality"] = "strict" if has_delivery else "candidate"
        item["telegram_post"] = build_caption(item)
        items.append(item)
    return items


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse public Telegram car offers")
    parser.add_argument("--channels", default=str(CHANNELS_PATH))
    parser.add_argument("--out", default=str(OUT_JSON))
    parser.add_argument("--markdown", default=str(OUT_MD))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--posts-per-channel", type=int, default=40)
    args = parser.parse_args()

    channels = json.load(open(args.channels, encoding="utf-8"))
    previous_offers = []
    previous_path = Path(args.out)
    if previous_path.exists():
        try:
            previous_payload = json.load(open(previous_path, encoding="utf-8"))
            previous_offers = [
                prepare_saved_offer(item) for item in previous_payload.get("offers", [])
                if item.get("source_type") != "catalog_fallback"
            ]
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
    strict = [
        item for item in dedup.values()
        if item.get("quality") in {"strict", "candidate"} and has_required_offer_fields(item)
    ]
    top = sorted(strict, key=lambda item: item["score"], reverse=True)[:args.limit]
    if len(top) < args.limit:
        used = {(item["title"].lower(), item.get("price", "")) for item in top}
        top.extend(load_catalog_fallbacks(args.limit - len(top), used))

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_count": len(channels),
        "parsed_posts": len(all_items),
        "displayed_count": len(top),
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
