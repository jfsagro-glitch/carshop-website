#!/usr/bin/env python3
"""
EXPO MIR — Универсальный парсер данных об автомобилях
=======================================================
Поддерживает:
  • Локальные CSV / JSON файлы
  • myauto.ge — официальный JSON API (лучший источник для Грузии)
  • ap.ge    — HTML-парсинг / API (аукционы Грузии)
  • mobile.de — HTML/JSON разбор европейских объявлений
  • autoscout24.de — JSON-разбор европейских объявлений
  • drom.ru  — публичный JSON-feed
  • Произвольные сайты (BeautifulSoup HTML-парсер)

Экспортирует:
  • JSON — формат carsData[] для script.js
  • CSV  — для Excel / Google Sheets
  • Обновляет script.js автоматически (--inject)
  • Обновляет cars_georgia_stock.json (--sync-stock)

Использование:
  python car_parser.py --help
  python car_parser.py --source myauto --max 50 --out cars_georgia.json
  python car_parser.py --source apge   --max 50 --out cars_apge.json
  python car_parser.py --source autoscout24 --max 220 --unique-models 200 --out cars_europe_new.json
  python car_parser.py --source csv    --input cars_data.csv --out cars_export.json
  python car_parser.py --source json   --input cars_europe.json --out cars_export.json
  python car_parser.py --source html   --url "https://example.com/cars" --out cars_export.json
  python car_parser.py --inject        --input cars_export.json  # вставит в script.js
  python car_parser.py --source myauto --sync-stock              # авто-обновит stock JSON
  python car_parser.py --validate-catalogs                       # проверит публичные JSON сайта
"""

import argparse
import csv
import json
import logging
import os
import re
import sys
import time
import random
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from pathlib import Path
from urllib.parse import urlparse, urljoin, urlencode

# ── Зависимости (устанавливаются через pip install requests beautifulsoup4) ──
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("car_parser")

# ── Константы нормализации ───────────────────────────────────────────────────

BRAND_ALIASES: Dict[str, str] = {
    "kia": "KIA",
    "киа": "KIA",
    "hyundai": "Hyundai",
    "хундай": "Hyundai",
    "хёндай": "Hyundai",
    "toyota": "Toyota",
    "тойота": "Toyota",
    "lexus": "Lexus",
    "лексус": "Lexus",
    "bmw": "BMW",
    "бмв": "BMW",
    "mercedes": "Mercedes-Benz",
    "mercedes-benz": "Mercedes-Benz",
    "мерседес": "Mercedes-Benz",
    "audi": "Audi",
    "ауди": "Audi",
    "volkswagen": "Volkswagen",
    "vw": "Volkswagen",
    "фольксваген": "Volkswagen",
    "chevrolet": "Chevrolet",
    "шевроле": "Chevrolet",
    "honda": "Honda",
    "хонда": "Honda",
    "nissan": "Nissan",
    "ниссан": "Nissan",
    "subaru": "Subaru",
    "субару": "Subaru",
    "mitsubishi": "Mitsubishi",
    "мицубиси": "Mitsubishi",
    "mazda": "Mazda",
    "мазда": "Mazda",
    "ford": "Ford",
    "форд": "Ford",
    "jeep": "Jeep",
    "джип": "Jeep",
    "dodge": "Dodge",
    "додж": "Dodge",
    "cadillac": "Cadillac",
    "кадиллак": "Cadillac",
    "lincoln": "Lincoln",
    "линкольн": "Lincoln",
    "infiniti": "Infiniti",
    "инфинити": "Infiniti",
    "acura": "Acura",
    "акура": "Acura",
    "porsche": "Porsche",
    "порше": "Porsche",
    "land rover": "Land Rover",
    "ленд ровер": "Land Rover",
    "volvo": "Volvo",
    "вольво": "Volvo",
    "genesis": "Genesis",
    "дженезис": "Genesis",
    "chery": "Chery",
    "чери": "Chery",
    "geely": "Geely",
    "джили": "Geely",
    "haval": "Haval",
    "хавал": "Haval",
    "byd": "BYD",
    "бид": "BYD",
    "changan": "Changan",
    "чанган": "Changan",
}

FUEL_ALIASES: Dict[str, str] = {
    "бензин": "Бензин",
    "petrol": "Бензин",
    "gasoline": "Бензин",
    "gas": "Бензин",
    "benzin": "Бензин",
    "бензин вспрыск": "Бензин",
    "бензин/впрыск": "Бензин",
    "дизель": "Дизель",
    "diesel": "Дизель",
    "электро": "Электро",
    "electric": "Электро",
    "elektro": "Электро",
    "ev": "Электро",
    "гибрид": "Гибрид",
    "hybrid": "Гибрид",
    "hev": "Гибрид",
    "mild hybrid": "Гибрид",
    "mild-hybrid": "Гибрид",
    "phev": "Плагин-гибрид",
    "plug-in": "Плагин-гибрид",
    "плагин": "Плагин-гибрид",
    "газ": "Газ/Бензин",
    "lpg": "Газ/Бензин",
    "erdgas": "Газ/Бензин",
    "cng": "Газ/Бензин",
    "wasserstoff": "Водород",
    "hydrogen": "Водород",
}

TRANS_ALIASES: Dict[str, str] = {
    "автомат": "Автомат",
    "акпп": "Автомат",
    "automatic": "Автомат",
    "automatik": "Автомат",
    "at": "Автомат",
    "механика": "Механика",
    "мкпп": "Механика",
    "manual": "Механика",
    "schaltgetriebe": "Механика",
    "mt": "Механика",
    "робот": "Робот",
    "amt": "Робот",
    "dct": "Робот",
    "dsg": "Робот",
    "doppelkupplungsgetriebe": "Робот",
    "вариатор": "Вариатор",
    "cvt": "Вариатор",
    "stufenloses": "Вариатор",
}

# ── Dataclass автомобиля ─────────────────────────────────────────────────────

@dataclass
class Car:
    id: int = 0
    brand: str = ""
    model: str = ""
    year: int = 2020
    engine: str = ""          # "1,6" / "2.0"
    vin: str = ""
    price: int = 0            # в рублях (RUB)
    mileage: int = 0          # км
    fuel_type: str = "Бензин"
    transmission: str = "Автомат"
    color: str = ""
    drive: str = ""           # "AWD" / "FWD" / "RWD"
    power: str = ""           # "147 л.с."
    date: str = ""            # дата производства / поставки
    description: str = ""
    photos: str = ""          # URL или путь к папке с фото
    folder_id: str = ""       # Google Drive folder id
    sold: bool = False
    source: str = ""          # источник записи
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_js_object(self) -> str:
        """Возвращает строку JS-объекта для вставки в carsData[]"""
        lines = [
            f"        id: {self.id},",
            f"        brand: {json.dumps(self.brand, ensure_ascii=False)},",
            f"        model: {json.dumps(self.model, ensure_ascii=False)},",
            f"        year: {self.year},",
        ]
        if self.engine:
            lines.append(f"        engine: {json.dumps(self.engine, ensure_ascii=False)},")
        if self.vin:
            lines.append(f"        vin: {json.dumps(self.vin, ensure_ascii=False)},")
        lines.append(f"        price: {self.price},")
        lines.append(f"        mileage: {self.mileage},")
        if self.fuel_type and self.fuel_type != "Бензин":
            lines.append(f"        fuelType: {json.dumps(self.fuel_type, ensure_ascii=False)},")
        if self.transmission and self.transmission != "Автомат":
            lines.append(f"        transmission: {json.dumps(self.transmission, ensure_ascii=False)},")
        if self.color:
            lines.append(f"        color: {json.dumps(self.color, ensure_ascii=False)},")
        if self.drive:
            lines.append(f"        drive: {json.dumps(self.drive, ensure_ascii=False)},")
        if self.power:
            lines.append(f"        power: {json.dumps(self.power, ensure_ascii=False)},")
        if self.date:
            lines.append(f"        date: {json.dumps(self.date, ensure_ascii=False)},")
        if self.description:
            lines.append(f"        description: {json.dumps(self.description, ensure_ascii=False)},")
        lines.append(f"        photos: {json.dumps(self.photos, ensure_ascii=False)},")
        if self.folder_id:
            lines.append(f"        folderId: {json.dumps(self.folder_id, ensure_ascii=False)},")
        if self.sold:
            lines.append("        sold: true,")
        return "    {\n" + "\n".join(lines) + "\n    }"


# ── Вспомогательные функции ──────────────────────────────────────────────────

def normalize_brand(raw: str) -> str:
    key = raw.strip().lower()
    return BRAND_ALIASES.get(key, raw.strip().title())


def normalize_fuel(raw: str) -> str:
    key = raw.strip().lower()
    return FUEL_ALIASES.get(key, raw.strip())


def normalize_transmission(raw: str) -> str:
    key = raw.strip().lower()
    return TRANS_ALIASES.get(key, raw.strip())


def parse_int(value: Any, default: int = 0) -> int:
    if value is None:
        return default
    cleaned = re.sub(r"[^\d]", "", str(value))
    return int(cleaned) if cleaned else default


def parse_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    cleaned = re.sub(r"[^\d.,]", "", str(value)).replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return default


def parse_power_hp(value: Any) -> int:
    """Достаёт мощность в л.с. из числа или строки вида '147 л.с.' / '100 kW'."""
    if value in (None, ""):
        return 0
    text = str(value).lower()
    hp_match = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:ps|hp|л\.?\s*с\.?|лс)", text, re.I)
    if hp_match:
        return round(float(hp_match.group(1).replace(",", ".")))
    kw_match = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:kw|квт)", text, re.I)
    if kw_match:
        return round(float(kw_match.group(1).replace(",", ".")) * 1.35962)
    num = parse_float(text)
    return round(num) if num else 0


def year_range_from_age(min_age: int = 0, max_age: int = 0, current_year: Optional[int] = None) -> tuple[int, int]:
    if not min_age and not max_age:
        return 0, 0
    year = current_year or datetime.now().year
    newest = year - min_age if min_age else year + 1
    oldest = year - max_age if max_age else 0
    return oldest, newest

def month_range_from_age(min_age: int = 0, max_age: int = 0, now: Optional[datetime] = None) -> tuple[int, int]:
    if not min_age and not max_age:
        return 0, 0
    current = now or datetime.now()
    newest = (current.year - min_age) * 100 + current.month if min_age else 999912
    oldest = (current.year - max_age) * 100 + current.month if max_age else 0
    return oldest, newest


def parse_year_month(value: Any) -> tuple[int, int]:
    if value in (None, ""):
        return 0, 0
    text = str(value).strip()
    month_year = re.search(r"\b(0?[1-9]|1[0-2])[./-]((?:19|20)\d{2})\b", text)
    if month_year:
        return int(month_year.group(2)), int(month_year.group(1))
    year_month = re.search(r"\b((?:19|20)\d{2})[./-](0?[1-9]|1[0-2])\b", text)
    if year_month:
        return int(year_month.group(1)), int(year_month.group(2))
    year = re.search(r"\b(19|20)\d{2}\b", text)
    return (int(year.group()), 0) if year else (0, 0)


def record_year(record: dict) -> int:
    return parse_int(record.get("year") or record.get("first_registration_year") or record.get("prod_year") or 0)

def record_year_month(record: dict) -> tuple[int, int]:
    for key in ("first_registration", "registration", "date", "production_date"):
        year, month = parse_year_month(record.get(key))
        if year:
            return year, month
    year = record_year(record)
    month = parse_int(record.get("month") or record.get("prod_month") or record.get("first_registration_month") or 0)
    return year, month if 1 <= month <= 12 else 0


def record_power_hp(record: dict) -> int:
    hp = parse_int(record.get("power_hp") or record.get("hp") or record.get("ps") or 0)
    if hp:
        return hp
    kw = parse_int(record.get("power_kw") or record.get("kw") or 0)
    if kw:
        return round(kw * 1.35962)
    return parse_power_hp(record.get("power") or record.get("мощность"))

def record_power_kw(record: dict) -> int:
    kw = parse_int(record.get("power_kw") or record.get("kw") or 0)
    if kw:
        return kw
    hp = parse_int(record.get("power_hp") or record.get("hp") or record.get("ps") or 0)
    if hp:
        return round(hp / 1.35962)
    power = parse_power_hp(record.get("power") or record.get("мощность"))
    return round(power / 1.35962) if power else 0

def max_kw_for_hp_limit(max_power_hp: int) -> int:
    if not max_power_hp:
        return 0
    return min(115, round(max_power_hp / 1.35962))


def filter_records(records: List[dict], min_year: int = 0, max_year: int = 0, max_power_hp: int = 0,
                   min_year_month: int = 0, max_year_month: int = 0) -> List[dict]:
    result = []
    max_power_kw = max_kw_for_hp_limit(max_power_hp)
    for record in records:
        year, month = record_year_month(record)
        if min_year and year and year < min_year:
            continue
        if max_year and year and year > max_year:
            continue
        year_month = year * 100 + (month or 1)
        if min_year_month and year and year_month < min_year_month:
            continue
        year_month_for_max = year * 100 + (month or 12)
        if max_year_month and year and year_month_for_max > max_year_month:
            continue
        hp = record_power_hp(record)
        if max_power_hp and hp and hp > max_power_hp:
            continue
        kw = record_power_kw(record)
        if max_power_kw and kw and kw > max_power_kw:
            continue
        result.append(record)
    return result


def filter_cars(cars: List["Car"], min_year: int = 0, max_year: int = 0, max_power_hp: int = 0,
                min_year_month: int = 0, max_year_month: int = 0) -> List["Car"]:
    result = []
    max_power_kw = max_kw_for_hp_limit(max_power_hp)
    for car in cars:
        if min_year and car.year and car.year < min_year:
            continue
        if max_year and car.year and car.year > max_year:
            continue
        month = parse_int(car.extra.get("month") or car.extra.get("prod_month") or 0)
        year_month = car.year * 100 + (month or 1)
        if min_year_month and car.year and year_month < min_year_month:
            continue
        year_month_for_max = car.year * 100 + (month or 12)
        if max_year_month and car.year and year_month_for_max > max_year_month:
            continue
        hp = parse_power_hp(car.power)
        if max_power_hp and hp and hp > max_power_hp:
            continue
        kw = parse_int(car.extra.get("power_kw") or 0)
        if max_power_kw and kw and kw > max_power_kw:
            continue
        result.append(car)
    return result


def validate_vin(vin: str) -> bool:
    """Базовая проверка формата VIN (17 символов, без I, O, Q)."""
    if not vin:
        return False
    vin = vin.strip().upper()
    return bool(re.fullmatch(r"[A-HJ-NPR-Z0-9]{17}", vin))


def dedup_by_vin(cars: List[Car]) -> List[Car]:
    """Удаляет дубликаты по VIN (оставляет первую запись)."""
    seen: set = set()
    result: List[Car] = []
    for car in cars:
        key = car.vin.upper() if car.vin else f"{car.brand}_{car.model}_{car.year}_{car.mileage}"
        if key not in seen:
            seen.add(key)
            result.append(car)
        else:
            log.debug(f"Дубль пропущен: {car.brand} {car.model} VIN={car.vin}")
    return result


def renumber(cars: List[Car], start: int = 1) -> List[Car]:
    for i, car in enumerate(cars):
        car.id = start + i
    return cars


# ── Парсер CSV ───────────────────────────────────────────────────────────────

class CsvParser:
    """
    Парсит CSV файл с произвольными заголовками.
    Поддерживает разделители: , ; \t
    """

    FIELD_MAP = {
        # Нормализованное поле → возможные названия колонок в CSV
        "brand":        ["brand", "марка", "make"],
        "model":        ["model", "модель"],
        "year":         ["year", "год", "год_выпуска", "production_year"],
        "price":        ["price", "цена", "стоимость", "cost"],
        "mileage":      ["mileage", "пробег", "km", "odometer"],
        "vin":          ["vin", "вин", "vin_number"],
        "engine":       ["engine", "двигатель", "engine_volume", "объём"],
        "fuel_type":    ["fuel_type", "тип_топлива", "fuel", "топливо"],
        "transmission": ["transmission", "кпп", "gearbox", "коробка"],
        "color":        ["color", "цвет", "colour"],
        "drive":        ["drive", "привод"],
        "power":        ["power", "мощность", "hp"],
        "date":         ["date", "дата", "production_date", "date_of_production"],
        "description":  ["description", "описание", "notes"],
        "photos":       ["photos", "фото", "photo_url", "images"],
        "folder_id":    ["folder_id", "folderid", "google_folder"],
        "sold":         ["sold", "продано", "is_sold"],
    }

    def __init__(self, filepath: str):
        self.filepath = filepath

    def _detect_separator(self, sample: str) -> str:
        counts = {sep: sample.count(sep) for sep in [",", ";", "\t"]}
        return max(counts, key=counts.get)

    def _map_headers(self, headers: List[str]) -> Dict[str, int]:
        mapping: Dict[str, int] = {}
        for norm_field, aliases in self.FIELD_MAP.items():
            for idx, h in enumerate(headers):
                if h.strip().lower().replace(" ", "_") in aliases:
                    mapping[norm_field] = idx
                    break
        return mapping

    def parse(self) -> List[Car]:
        if not os.path.exists(self.filepath):
            log.error(f"Файл не найден: {self.filepath}")
            return []

        with open(self.filepath, encoding="utf-8-sig", errors="replace") as f:
            sample = f.read(4096)

        sep = self._detect_separator(sample)
        log.info(f"CSV разделитель: {repr(sep)}")

        cars: List[Car] = []
        with open(self.filepath, encoding="utf-8-sig", errors="replace") as f:
            reader = csv.reader(f, delimiter=sep)
            headers = [h.strip() for h in next(reader, [])]
            mapping = self._map_headers(headers)
            log.info(f"CSV колонки сопоставлены: {mapping}")

            for row_num, row in enumerate(reader, start=2):
                if not any(row):
                    continue
                try:
                    car = self._row_to_car(row, mapping)
                    cars.append(car)
                except Exception as e:
                    log.warning(f"Строка {row_num}: ошибка — {e}")

        log.info(f"CSV: загружено {len(cars)} автомобилей из {self.filepath}")
        return cars

    def _row_to_car(self, row: List[str], m: Dict[str, int]) -> Car:
        def get(field: str) -> str:
            idx = m.get(field)
            return row[idx].strip() if idx is not None and idx < len(row) else ""

        car = Car()
        car.brand = normalize_brand(get("brand"))
        car.model = get("model")
        car.year = parse_int(get("year"), 2020)
        car.price = parse_int(get("price"))
        car.mileage = parse_int(get("mileage"))
        car.vin = get("vin").upper()
        car.engine = get("engine").replace(".", ",")
        car.fuel_type = normalize_fuel(get("fuel_type") or "Бензин")
        car.transmission = normalize_transmission(get("transmission") or "Автомат")
        car.color = get("color")
        car.drive = get("drive").upper()
        car.power = get("power")
        car.date = get("date")
        car.description = get("description")
        car.photos = get("photos")
        car.folder_id = get("folder_id")
        sold_raw = get("sold").lower()
        car.sold = sold_raw in ("1", "true", "да", "yes", "продано")
        car.source = "csv"
        return car


# ── Парсер JSON ──────────────────────────────────────────────────────────────

class JsonParser:
    """
    Парсит JSON файл — массив объектов или объект с полем "cars"/"items"/"data".
    """

    def __init__(self, filepath: str):
        self.filepath = filepath

    def parse(self) -> List[Car]:
        if not os.path.exists(self.filepath):
            log.error(f"Файл не найден: {self.filepath}")
            return []

        with open(self.filepath, encoding="utf-8") as f:
            data = json.load(f)

        items: List[Dict] = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            for key in ("cars", "items", "data", "results", "vehicles"):
                if key in data and isinstance(data[key], list):
                    items = data[key]
                    break
            else:
                items = [data]  # единственный объект

        cars = [self._item_to_car(item) for item in items if isinstance(item, dict)]
        log.info(f"JSON: загружено {len(cars)} автомобилей из {self.filepath}")
        return cars

    def _item_to_car(self, item: Dict) -> Car:
        car = Car()
        car.brand = normalize_brand(str(item.get("brand") or item.get("make") or item.get("марка") or ""))
        car.model = str(item.get("model") or item.get("модель") or "")
        car.year = parse_int(item.get("year") or item.get("год"))
        car.price = parse_int(item.get("price") or item.get("цена") or item.get("cost"))
        car.mileage = parse_int(item.get("mileage") or item.get("пробег") or item.get("km") or 0)
        car.vin = str(item.get("vin") or item.get("VIN") or "").upper()
        raw_engine = item.get("engine") or item.get("двигатель") or item.get("engine_volume") or ""
        car.engine = str(raw_engine).replace(".", ",")
        car.fuel_type = normalize_fuel(str(item.get("fuel_type") or item.get("fuel") or item.get("топливо") or "Бензин"))
        car.transmission = normalize_transmission(str(item.get("transmission") or item.get("gearbox") or item.get("кпп") or "Автомат"))
        car.color = str(item.get("color") or item.get("colour") or item.get("цвет") or "")
        car.drive = str(item.get("drive") or item.get("привод") or "").upper()
        car.power = str(item.get("power") or item.get("мощность") or "")
        car.date = str(item.get("date") or item.get("production_date") or item.get("дата") or "")
        car.description = str(item.get("description") or item.get("описание") or "")
        photos = item.get("photos") or item.get("photo_url") or item.get("image") or ""
        car.photos = photos if isinstance(photos, str) else (photos[0] if photos else "")
        car.folder_id = str(item.get("folderId") or item.get("folder_id") or "")
        sold_raw = str(item.get("sold") or item.get("is_sold") or item.get("продано") or "false").lower()
        car.sold = sold_raw in ("1", "true", "да", "yes", "продано")
        car.source = "json"
        # сохраняем неизвестные поля
        known = {"brand", "make", "model", "year", "price", "mileage", "km", "vin",
                 "engine", "fuel_type", "fuel", "transmission", "gearbox", "color",
                 "colour", "drive", "power", "date", "production_date", "description",
                 "photos", "photo_url", "image", "folderId", "folder_id", "sold", "is_sold"}
        car.extra = {k: v for k, v in item.items() if k.lower() not in known and v is not None}
        return car


# ── Парсер HTML (BeautifulSoup) ───────────────────────────────────────────────

class HtmlParser:
    """
    Базовый HTML-парсер.
    Ищет структурированные данные:
      1. JSON-LD (<script type="application/ld+json">)
      2. Meta-теги og:*
      3. Общие паттерны: .car-card, .listing-item, article[data-id] и т.д.
    """

    UA_LIST = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/125.0",
    ]

    def __init__(self, url: str, delay: float = 2.0, proxy: Optional[str] = None):
        if not REQUESTS_AVAILABLE:
            raise RuntimeError("Установите requests: pip install requests")
        if not BS4_AVAILABLE:
            raise RuntimeError("Установите beautifulsoup4: pip install beautifulsoup4")
        self.url = url
        self.delay = delay
        self.proxy = proxy

    def _get(self, url: str) -> Optional[str]:
        headers = {"User-Agent": random.choice(self.UA_LIST),
                   "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8"}
        proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None
        try:
            resp = requests.get(url, headers=headers, proxies=proxies, timeout=15)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            log.warning(f"HTTP ошибка для {url}: {e}")
            return None

    def _extract_json_ld(self, soup: "BeautifulSoup") -> List[Car]:
        cars: List[Car] = []
        for tag in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(tag.string or "")
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if item.get("@type") in ("Vehicle", "Car", "AutoDealer"):
                        car = Car()
                        car.brand = normalize_brand(str(item.get("brand", {}).get("name", "") or item.get("brand", "")))
                        car.model = str(item.get("model", ""))
                        car.year = parse_int(item.get("vehicleModelDate") or item.get("modelDate"), 2020)
                        car.mileage = parse_int(item.get("mileageFromOdometer", {}).get("value", 0))
                        car.price = parse_int(item.get("offers", {}).get("price", 0))
                        car.vin = str(item.get("vehicleIdentificationNumber", "")).upper()
                        car.description = str(item.get("description", ""))
                        car.fuel_type = normalize_fuel(str(item.get("fuelType", "Бензин")))
                        car.transmission = normalize_transmission(str(item.get("vehicleTransmission", "Автомат")))
                        car.drive = str(item.get("driveWheelConfiguration", "")).upper()
                        car.source = "html_jsonld"
                        cars.append(car)
            except (json.JSONDecodeError, AttributeError):
                pass
        return cars

    def _extract_cards(self, soup: "BeautifulSoup") -> List[Car]:
        """Эвристический разбор карточек товаров на произвольных сайтах."""
        CARD_SELECTORS = [
            ".car-card", ".listing-item", ".vehicle-card",
            "article[data-id]", ".offer-item", ".auto-item",
            "[class*='car-card']", "[class*='listing']",
        ]
        cards = []
        for sel in CARD_SELECTORS:
            cards = soup.select(sel)
            if cards:
                log.debug(f"Найдено {len(cards)} карточек по селектору: {sel}")
                break

        cars: List[Car] = []
        for card in cards:
            car = Car()
            # Заголовок / название
            title_el = card.select_one("h1, h2, h3, .title, .name, [class*='title']")
            title = title_el.get_text(strip=True) if title_el else ""
            # Разбор названия: "2021 KIA Sportage 2.0 AWD"
            if title:
                year_m = re.search(r"\b(19|20)\d{2}\b", title)
                if year_m:
                    car.year = int(year_m.group())
                    title = title.replace(year_m.group(), "").strip()
                parts = title.split(maxsplit=2)
                car.brand = normalize_brand(parts[0]) if parts else ""
                car.model = " ".join(parts[1:]) if len(parts) > 1 else ""

            # Цена
            price_el = card.select_one(".price, [class*='price'], [itemprop='price']")
            if price_el:
                car.price = parse_int(price_el.get_text())

            # Пробег
            for text in card.stripped_strings:
                km_m = re.search(r"([\d\s]+)\s*(км|km|тыс\.?\s*км)", text, re.I)
                if km_m:
                    raw = km_m.group(1).replace(" ", "")
                    val = int(raw)
                    if "тыс" in km_m.group(2).lower():
                        val *= 1000
                    car.mileage = val
                    break

            # Фото
            img_el = card.select_one("img")
            car.photos = img_el.get("src") or img_el.get("data-src") or "" if img_el else ""

            car.source = "html_card"
            cars.append(car)

        return cars

    def parse(self) -> List[Car]:
        log.info(f"HTTP GET: {self.url}")
        html = self._get(self.url)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")

        # Приоритет 1: JSON-LD
        cars = self._extract_json_ld(soup)
        if cars:
            log.info(f"HTML (JSON-LD): найдено {len(cars)} авто")
            return cars

        # Приоритет 2: карточки
        cars = self._extract_cards(soup)
        log.info(f"HTML (cards): найдено {len(cars)} авто")
        return cars


# ── Парсер Drom.ru ───────────────────────────────────────────────────────────

class DromParser:
    """
    Парсит объявления с drom.ru через публичные JSON-endpoints.
    НЕ нарушает robots.txt — читает только публичные страницы
    с задержкой между запросами (delay по умолчанию 3 сек).
    """

    BASE_URL = "https://auto.drom.ru"
    API_URL = "https://auto.drom.ru/api/search"

    REGION_SLUGS = {
        "tbilisi": "gruziya",
        "georgia": "gruziya",
        "moscow": "moskva",
        "spb": "spb",
        "bishkek": "kyrgyzstan",
        "almaty": "kazakhstan",
        "all": "",
    }

    def __init__(self, region: str = "all", max_cars: int = 50, delay: float = 3.0,
                 proxy: Optional[str] = None):
        if not REQUESTS_AVAILABLE:
            raise RuntimeError("Установите requests: pip install requests")
        if not BS4_AVAILABLE:
            raise RuntimeError("Установите beautifulsoup4: pip install beautifulsoup4 lxml")
        self.region_slug = self.REGION_SLUGS.get(region.lower(), region.lower())
        self.max_cars = max_cars
        self.delay = delay
        self.proxy = proxy
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0",
            "Accept-Language": "ru-RU,ru;q=0.9",
        })

    def _get(self, url: str, params: Optional[Dict] = None) -> Optional[requests.Response]:
        proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None
        try:
            r = self.session.get(url, params=params, proxies=proxies, timeout=15)
            r.raise_for_status()
            return r
        except Exception as e:
            log.warning(f"Drom GET ошибка {url}: {e}")
            return None

    def _parse_listing_page(self, html: str) -> List[Car]:
        soup = BeautifulSoup(html, "html.parser")
        cars: List[Car] = []

        # drom.ru хранит данные в data-bull атрибутах или JSON внутри тегов
        for script in soup.find_all("script"):
            text = script.string or ""
            # ищем массив объявлений window.__initialData__ или подобное
            match = re.search(r'window\.__(?:initial|data)\w*\s*=\s*(\{.*?\});', text, re.S)
            if match:
                try:
                    data = json.loads(match.group(1))
                    items = self._extract_from_initial_data(data)
                    if items:
                        log.debug(f"drom: JSON в странице, {len(items)} авто")
                        return items
                except json.JSONDecodeError:
                    pass

        # Фолбек — HTML-парсинг карточек
        for card in soup.select("[data-bull-id], .listing__item, .e1huvdhj0"):
            car = self._parse_drom_card(card)
            if car:
                cars.append(car)
                if len(cars) >= self.max_cars:
                    break

        return cars

    def _extract_from_initial_data(self, data: Dict) -> List[Car]:
        cars: List[Car] = []
        # Обходим вложенную структуру в поисках списка объявлений
        def walk(obj: Any) -> List[Dict]:
            if isinstance(obj, list) and obj and isinstance(obj[0], dict):
                if "brand" in obj[0] or "make" in obj[0] or "title" in obj[0]:
                    return obj
            if isinstance(obj, dict):
                for v in obj.values():
                    result = walk(v)
                    if result:
                        return result
            return []

        items = walk(data)
        for item in items[:self.max_cars]:
            parser = JsonParser.__new__(JsonParser)
            car = parser._item_to_car(item)
            car.source = "drom"
            cars.append(car)
        return cars

    def _parse_drom_card(self, card: "BeautifulSoup") -> Optional[Car]:
        car = Car()
        try:
            # Заголовок "KIA Sportage, 2022" или "2022, KIA Sportage"
            title_el = card.select_one("a[data-ftid='bull_title'], h3, .title")
            if not title_el:
                return None
            title = title_el.get_text(strip=True)
            year_m = re.search(r"\b(19|20)\d{2}\b", title)
            if year_m:
                car.year = int(year_m.group())
                title = title.replace(year_m.group(), "").strip(" ,")
            parts = title.split(maxsplit=1)
            car.brand = normalize_brand(parts[0]) if parts else ""
            car.model = parts[1] if len(parts) > 1 else ""

            # Цена
            price_el = card.select_one("[data-ftid='bull_price'], .price__title")
            if price_el:
                car.price = parse_int(price_el.get_text())

            # Пробег
            for text in card.stripped_strings:
                km_m = re.search(r"([\d\s]+)\s*(?:км|тыс\.?\s*км)", text, re.I)
                if km_m:
                    raw = km_m.group(1).replace(" ", "")
                    val = int(raw) if raw else 0
                    if "тыс" in text.lower():
                        val *= 1000
                    car.mileage = val
                    break

            # Двигатель
            for text in card.stripped_strings:
                eng_m = re.search(r"(\d[.,]\d)\s*(?:л|L)", text, re.I)
                if eng_m:
                    car.engine = eng_m.group(1).replace(".", ",")
                    break

            # Фото
            img = card.select_one("img")
            car.photos = img.get("src") or img.get("data-src") or "" if img else ""
            car.source = "drom"
            return car
        except Exception as e:
            log.debug(f"drom card error: {e}")
            return None

    def parse(self) -> List[Car]:
        cars: List[Car] = []
        page = 1
        while len(cars) < self.max_cars:
            url = self.BASE_URL
            if self.region_slug:
                url = f"{self.BASE_URL}/{self.region_slug}"
            params = {"p": page} if page > 1 else {}
            log.info(f"Drom: страница {page} — {url}")
            resp = self._get(url, params)
            if not resp:
                break
            new_cars = self._parse_listing_page(resp.text)
            if not new_cars:
                log.info("Drom: больше страниц нет")
                break
            cars.extend(new_cars)
            log.info(f"Drom: собрано {len(cars)} авто")
            page += 1
            time.sleep(self.delay + random.uniform(0, 1))  # вежливые задержки

        log.info(f"Drom: итого {len(cars)} автомобилей")
        return cars[:self.max_cars]


# ── Парсер myauto.ge (официальный JSON API) ───────────────────────────────────

class MyAutoGeParser:
    """
    Парсит объявления с myauto.ge через официальный публичный JSON API.
    API не требует авторизации, соблюдает robots.txt.
    Ссылки: https://myauto.ge  /  https://api2.myauto.ge
    """

    BASE_API = "https://api2.myauto.ge/en/products"
    PHOTO_BASE = "https://static.my.ge/myauto/photos/"

    # Маппинги типов из API
    FUEL_MAP = {1: "Бензин", 2: "Дизель", 3: "Гибрид", 4: "Электро",
                5: "Газ/Бензин", 6: "Плагин-гибрид", 7: "Водород"}
    TRANS_MAP = {1: "Механика", 2: "Автомат", 3: "Вариатор", 4: "Робот"}
    DRIVE_MAP = {1: "FWD", 2: "RWD", 3: "4WD", 4: "AWD"}

    UA_LIST = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    ]

    def __init__(self, max_cars: int = 100, delay: float = 1.5,
                 brand: str = "", min_year: int = 0, max_price_usd: int = 0,
                 max_year: int = 0, max_power_hp: int = 0,
                 proxy: Optional[str] = None):
        if not REQUESTS_AVAILABLE:
            raise RuntimeError("Установите requests: pip install requests")
        self.max_cars  = max_cars
        self.delay     = delay
        self.brand     = brand        # фильтр по марке (например "Toyota")
        self.min_year  = min_year     # фильтр по году
        self.max_year  = max_year
        self.max_power_hp = max_power_hp
        self.max_price = max_price_usd
        self.proxy     = proxy

    def _get_json(self, params: dict) -> Optional[dict]:
        headers = {
            "User-Agent": random.choice(self.UA_LIST),
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.myauto.ge/",
        }
        proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None
        try:
            resp = requests.get(self.BASE_API, params=params, headers=headers,
                                proxies=proxies, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            log.warning(f"myauto.ge API ошибка: {e}")
            return None

    def _item_to_car(self, item: dict) -> Optional[Car]:
        try:
            car = Car()
            car.brand = normalize_brand(str(item.get("man_name", "")))
            car.model = str(item.get("model_name", ""))
            car.year  = parse_int(item.get("prod_year", 0))
            car.extra["prod_month"] = parse_int(item.get("prod_month") or 0)

            # Цена — предпочитаем USD
            price_usd = item.get("price_usd") or item.get("price_value", 0)
            car.price = parse_int(price_usd)

            # Пробег (myauto.ge возвращает в км или тыс.км)
            mileage_raw = parse_int(item.get("car_run_km") or item.get("mileage", 0))
            car.mileage = mileage_raw * 1000 if mileage_raw < 1000 else mileage_raw

            # Объём двигателя (в cm³ или л)
            eng_vol = item.get("engine_volume", "")
            if eng_vol:
                eng_float = parse_float(str(eng_vol))
                if eng_float > 100:  # уже в см³
                    car.engine = str(round(eng_float / 1000, 1)).replace(".", ",")
                else:
                    car.engine = str(eng_float).replace(".", ",")

            car.fuel_type    = self.FUEL_MAP.get(item.get("fuel_type_id", 1), "Бензин")
            car.transmission = self.TRANS_MAP.get(item.get("gear_type_id", 2), "Автомат")
            car.drive        = self.DRIVE_MAP.get(item.get("drive_type_id", 0), "")
            car.color        = str(item.get("color", ""))
            # hp недоступен в списке — используем engine_volume как запасной индикатор
            car.power        = str(item.get("hp") or "")

            # VIN (не всегда доступен в списке)
            vin_raw = str(item.get("vin") or "").upper().strip()
            # Иногда VIN бывает в тексте описания
            if not vin_raw:
                desc = str(item.get("car_desc", ""))
                vin_m = re.search(r'(?:vin\s*:?\s*)([A-HJ-NPR-Z0-9]{17})', desc, re.I)
                if vin_m:
                    vin_raw = vin_m.group(1).upper()
            car.vin = vin_raw

            # Фото — формат: {PHOTO_BASE}{photo}/large/{car_id}_{n}.jpg?v={photo_ver}
            car_id   = item.get("car_id", "")
            photo_p  = item.get("photo", "")  # напр.: "3/4/9/6/6"
            pic_num  = int(item.get("pic_number") or 1)
            photo_ver = parse_int(item.get("photo_ver") or 0)
            if photo_p and car_id:
                # Первое фото
                car.photos = f"{self.PHOTO_BASE}{photo_p}/large/{car_id}_1.jpg?v={photo_ver}"
                # Все фото — сохраняем в extra для sync_georgia_stock
                car.extra["images"] = [
                    {"url": f"{self.PHOTO_BASE}{photo_p}/large/{car_id}_{n}.jpg?v={photo_ver}", "order": n}
                    for n in range(1, min(pic_num, 12) + 1)
                ]
            else:
                car.photos = ""

            # Ссылка на объявление
            car.description = f"myauto.ge/ru/pr/{car_id}"
            car.source = "myauto_ge"
            return car
        except Exception as e:
            log.debug(f"myauto.ge: ошибка разбора записи: {e}")
            return None

    def parse(self) -> List[Car]:
        log.info("myauto.ge: начало загрузки объявлений...")
        cars: List[Car] = []
        page = 1

        while len(cars) < self.max_cars:
            params: dict = {
                "TypeID": 0,
                "ForRent": 0,
                "SortOrder": 1,
                "Curr": 3,   # USD
                "Page": page,
            }
            if self.min_year:
                params["YearFrom"] = self.min_year
            if self.max_year:
                params["YearTo"] = self.max_year
            if self.max_price:
                params["PriceTo"] = self.max_price

            data = self._get_json(params)
            if not data:
                break

            # Структура ответа: data.data.items + data.data.meta
            items = (data.get("data", {}) or {}).get("items") or data.get("items", [])
            if not items:
                log.info("myauto.ge: страницы закончились")
                break

            for item in items:
                car = self._item_to_car(item)
                if car and car.brand:
                    # Фильтр по марке
                    if self.brand and self.brand.lower() not in car.brand.lower():
                        continue
                    if self.max_year and car.year and car.year > self.max_year:
                        continue
                    hp = parse_power_hp(car.power) or item.get("hp", 0)
                    if self.max_power_hp and hp and hp > self.max_power_hp:
                        continue
                    cars.append(car)
                if len(cars) >= self.max_cars:
                    break

            total_pages = (data.get("data", {}) or {}).get("meta", {}).get("last_page", page)
            log.info(f"myauto.ge: стр. {page}/{total_pages}, собрано {len(cars)} авто")

            if page >= total_pages:
                break
            page += 1
            time.sleep(self.delay + random.uniform(0, 0.5))

        log.info(f"myauto.ge: итого {len(cars)} автомобилей")
        return cars[:self.max_cars]


# ── Парсер ap.ge (HTML + API) ─────────────────────────────────────────────────

class ApGeParser:
    """
    Парсит объявления с ap.ge (авторынок Грузии).
    Использует их внутренний API или HTML-разбор как запасной вариант.
    """

    # ap.ge внутренний API endpoint (может меняться с обновлениями сайта)
    API_URL   = "https://api.ap.ge/api/v2/applications"
    SITE_URL  = "https://ap.ge/ru/usd"

    UA_LIST = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/125.0",
    ]

    def __init__(self, max_cars: int = 100, delay: float = 2.0,
                 proxy: Optional[str] = None):
        if not REQUESTS_AVAILABLE:
            raise RuntimeError("Установите requests: pip install requests")
        self.max_cars = max_cars
        self.delay    = delay
        self.proxy    = proxy
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": random.choice(self.UA_LIST),
            "Accept": "application/json, text/html, */*",
            "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
        })

    def _get(self, url: str, params: dict = None) -> Optional[requests.Response]:
        proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None
        try:
            resp = self._session.get(url, params=params, proxies=proxies, timeout=15)
            resp.raise_for_status()
            return resp
        except Exception as e:
            log.warning(f"ap.ge: ошибка запроса {url}: {e}")
            return None

    def _parse_api_item(self, item: dict) -> Optional[Car]:
        """Разбирает одну запись из JSON API ap.ge."""
        try:
            car = Car()
            # Название: "2021 Toyota Camry 2.5" или отдельные поля
            title = str(item.get("title") or item.get("name") or "")
            if title:
                year_m = re.search(r"\b(19|20)\d{2}\b", title)
                if year_m:
                    car.year  = int(year_m.group())
                    rest = title.replace(year_m.group(), "").strip()
                else:
                    rest = title
                parts = rest.split(maxsplit=1)
                car.brand = normalize_brand(parts[0]) if parts else ""
                car.model = parts[1] if len(parts) > 1 else ""

            # Поля, если доступны отдельно
            if item.get("manufacturer"):
                car.brand = normalize_brand(str(item["manufacturer"]))
            if item.get("model"):
                car.model = str(item["model"])
            if item.get("year"):
                car.year = parse_int(item["year"])

            # Цена в USD
            price = item.get("price_usd") or item.get("price") or 0
            car.price = parse_int(price)

            # Пробег
            car.mileage = parse_int(item.get("mileage") or item.get("run") or 0)

            # Двигатель
            eng = item.get("engine_volume") or item.get("engine") or ""
            if eng:
                eng_f = parse_float(str(eng))
                car.engine = (str(round(eng_f / 1000, 1)) if eng_f > 100 else str(eng_f)).replace(".", ",")

            # Прочие атрибуты
            fuel_raw  = str(item.get("fuel_type") or item.get("fuel") or "Бензин")
            trans_raw = str(item.get("transmission") or item.get("gearbox") or "Автомат")
            car.fuel_type    = normalize_fuel(fuel_raw)
            car.transmission = normalize_transmission(trans_raw)
            car.color        = str(item.get("color") or "")

            # Фото
            photos = item.get("photos") or item.get("images") or []
            if isinstance(photos, list) and photos:
                first = photos[0]
                car.photos = first if isinstance(first, str) else str(first.get("url", ""))
            elif isinstance(photos, str):
                car.photos = photos

            listing_id = item.get("id") or item.get("application_id") or ""
            car.description = f"ap.ge/ru/{listing_id}" if listing_id else ""
            car.source = "ap_ge"
            return car
        except Exception as e:
            log.debug(f"ap.ge: ошибка разбора записи: {e}")
            return None

    def _parse_html_fallback(self, html: str) -> List[Car]:
        """HTML-разбор страницы ap.ge как запасной вариант."""
        if not BS4_AVAILABLE:
            log.warning("Установите beautifulsoup4 для HTML-парсинга")
            return []
        soup = BeautifulSoup(html, "html.parser")
        cars = []
        # ap.ge использует карточки с классом product-list__item или подобным
        selectors = [".product-list__item", ".car-list__item", ".listing-item",
                     "[class*='product-item']", "[data-id]"]
        items = []
        for sel in selectors:
            items = soup.select(sel)
            if items:
                log.debug(f"ap.ge HTML: найдено {len(items)} карточек по '{sel}'")
                break

        for card in items:
            car = Car()
            # Заголовок
            h = card.select_one("h2, h3, .title, [class*='title'], [class*='name']")
            if h:
                text = h.get_text(" ", strip=True)
                m = re.search(r"\b(19|20)\d{2}\b", text)
                car.year = int(m.group()) if m else 0
                rest = text.replace(m.group(), "").strip() if m else text
                parts = rest.split(maxsplit=1)
                car.brand = normalize_brand(parts[0]) if parts else ""
                car.model = parts[1].strip() if len(parts) > 1 else ""
            # Цена
            p = card.select_one(".price, [class*='price']")
            if p:
                car.price = parse_int(p.get_text())
            # Пробег
            for span in card.find_all(string=re.compile(r"[\d\s]+\s*(км|km)", re.I)):
                car.mileage = parse_int(span)
                break
            # Фото
            img = card.select_one("img")
            if img:
                car.photos = img.get("src") or img.get("data-src") or ""
            car.source = "ap_ge_html"
            if car.brand:
                cars.append(car)
        return cars

    def parse(self) -> List[Car]:
        log.info("ap.ge: начало загрузки объявлений...")
        cars: List[Car] = []
        page = 1

        while len(cars) < self.max_cars:
            # Пробуем JSON API
            resp = self._get(self.API_URL, params={
                "category": 3,   # автомобили
                "status": 2,     # в продаже
                "currency": "usd",
                "page": page,
            })
            if resp is None:
                log.warning("ap.ge API недоступен, пробуем HTML-парсинг")
                html_resp = self._get(self.SITE_URL)
                if html_resp:
                    cars.extend(self._parse_html_fallback(html_resp.text))
                break

            # Пытаемся разобрать как JSON
            try:
                data = resp.json()
            except Exception:
                log.warning("ap.ge: не JSON ответ, переходим к HTML-парсингу")
                cars.extend(self._parse_html_fallback(resp.text))
                break

            # Извлекаем записи из разных возможных структур
            items = (data.get("data") or data.get("items") or
                     data.get("results") or (data if isinstance(data, list) else []))
            if not items:
                log.info("ap.ge: данные закончились")
                break

            for item in (items if isinstance(items, list) else []):
                car = self._parse_api_item(item)
                if car and car.brand:
                    cars.append(car)
                if len(cars) >= self.max_cars:
                    break

            # Проверяем, есть ли ещё страницы
            meta = data.get("meta") or data.get("pagination") or {}
            last_page = meta.get("last_page") or meta.get("total_pages") or page
            log.info(f"ap.ge: стр. {page}/{last_page}, собрано {len(cars)} авто")
            if page >= last_page:
                break
            page += 1
            time.sleep(self.delay + random.uniform(0, 0.8))

        log.info(f"ap.ge: итого {len(cars)} автомобилей")
        return cars[:self.max_cars]


# ── Парсер mobile.de (Европа) ────────────────────────────────────────────────

class MobileDeParser:
    """
    Парсит европейские объявления с mobile.de.
    Основной путь — JSON-состояние страницы, запасной — разбор карточек HTML.
    """

    SEARCH_URL = "https://suchen.mobile.de/fahrzeuge/search.html"

    UA_LIST = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    ]

    def __init__(self, max_cars: int = 100, delay: float = 2.0,
                 url: str = "", min_year: int = 0, max_year: int = 0,
                 max_power_hp: int = 0, proxy: Optional[str] = None):
        if not REQUESTS_AVAILABLE:
            raise RuntimeError("Установите requests: pip install requests")
        if not BS4_AVAILABLE:
            raise RuntimeError("Установите beautifulsoup4: pip install beautifulsoup4")
        self.max_cars = max_cars
        self.delay = delay
        self.min_year = min_year
        self.max_year = max_year
        self.max_power_hp = max_power_hp
        self.url = url or self._build_default_url()
        self.proxy = proxy
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": random.choice(self.UA_LIST),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
            "Referer": "https://suchen.mobile.de/",
        })

    def _build_default_url(self) -> str:
        params = {
            "s": "Car",
            "vc": "Car",
            "isSearchRequest": "true",
            "dam": "false",
            "fr": f"{self.min_year or 2019}:",
            "ml": ":80000",
            "od": "up",
            "sb": "rel",
        }
        if self.min_year or self.max_year:
            yr_from = self.min_year or (datetime.now().year - 7)
            params["fr"] = f"{yr_from}:{self.max_year or ''}"
        if self.max_power_hp:
            # mobile.de uses kW
            params["pw"] = f":{round(self.max_power_hp / 1.35962)}"
        return f"{self.SEARCH_URL}?{urlencode(params)}"

    def _get(self, url: str) -> Optional[str]:
        proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None
        try:
            resp = self._session.get(url, proxies=proxies, timeout=20)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            log.warning(f"mobile.de: ошибка запроса {url}: {e}")
            return None

    def _extract_json_objects(self, html: str) -> List[dict]:
        objects: List[dict] = []
        for marker in ("__NEXT_DATA__", "__INITIAL_STATE__", "initialState"):
            if marker not in html:
                continue
            for m in re.finditer(r"<script[^>]*>(.*?)</script>", html, re.DOTALL | re.I):
                script = m.group(1)
                if marker not in script:
                    continue
                json_text = script.strip()
                if marker != "__NEXT_DATA__":
                    brace = json_text.find("{")
                    json_text = json_text[brace:] if brace >= 0 else json_text
                    json_text = re.sub(r";\s*$", "", json_text)
                try:
                    objects.append(json.loads(json_text))
                except Exception:
                    continue
        return objects

    def _walk_dicts(self, value: Any):
        if isinstance(value, dict):
            yield value
            for child in value.values():
                yield from self._walk_dicts(child)
        elif isinstance(value, list):
            for child in value:
                yield from self._walk_dicts(child)

    def _looks_like_listing(self, item: dict) -> bool:
        keys = {str(k).lower() for k in item.keys()}
        return (
            ("id" in keys or "adid" in keys or "ad_id" in keys)
            and any(k in keys for k in ("make", "brand", "manufacturer", "model", "modeldescription", "title"))
            and any(k in keys for k in ("price", "consumerpricegross", "mileage", "images", "galleryimages"))
        )

    def _pick(self, item: dict, *keys: str, default: Any = "") -> Any:
        lowered = {str(k).lower(): v for k, v in item.items()}
        for key in keys:
            if key in item and item[key] not in (None, ""):
                return item[key]
            value = lowered.get(key.lower())
            if value not in (None, ""):
                return value
        return default

    def _price_to_number(self, value: Any) -> float:
        if isinstance(value, dict):
            value = self._pick(value, "amount", "gross", "value", "consumerPriceGross", default=0)
        return float(parse_int(value))

    def _images_to_list(self, value: Any) -> List[dict]:
        images: List[dict] = []
        if isinstance(value, dict):
            value = value.get("images") or value.get("gallery") or value.get("items") or []
        if not isinstance(value, list):
            return images
        for index, image in enumerate(value, start=1):
            url = ""
            if isinstance(image, str):
                url = image
            elif isinstance(image, dict):
                url = str(self._pick(image, "url", "src", "uri", "thumbnailUrl", "baseUrl", default=""))
            if url:
                images.append({"url": url, "order": index})
        return images

    @staticmethod
    def _extract_from_equipment(equipment: list) -> dict:
        """Извлекает fuel_type/transmission из немецких текстов equipment[]"""
        result = {"fuel_type": "", "transmission": ""}
        full_text = " ".join(str(e) for e in equipment).lower()
        # Топливо
        fuel_map = [
            ("benzin", "Бензин"), ("diesel", "Дизель"),
            ("elektro", "Электро"), ("hybrid", "Гибрид"),
            ("plug-in", "Плагин-гибрид"), ("erdgas", "Газ/Бензин"),
            ("wasserstoff", "Водород"),
        ]
        for key, val in fuel_map:
            if key in full_text:
                result["fuel_type"] = val
                break
        # Трансмиссия
        trans_map = [
            ("schaltgetriebe", "Механика"), ("automatik", "Автомат"),
            ("doppelkupplungs", "Робот"), ("stufenlos", "Вариатор"),
        ]
        for key, val in trans_map:
            if key in full_text:
                result["transmission"] = val
                break
        return result

    def _item_to_europe_dict(self, item: dict) -> Optional[dict]:
        ad_id = str(self._pick(item, "id", "adId", "ad_id", "mobileAdId", default="")).strip()
        brand = normalize_brand(str(self._pick(item, "brand", "make", "manufacturer", "makeName", default="")))
        model = str(self._pick(item, "model", "modelDescription", "modelName", default="")).strip()
        title = str(self._pick(item, "title", "headline", "fullTitle", default="")).strip()

        if not brand and title:
            parts = title.split(maxsplit=1)
            brand = normalize_brand(parts[0])
            model = model or (parts[1] if len(parts) > 1 else "")
        if not brand:
            return None

        price = self._price_to_number(self._pick(item, "price", "consumerPriceGross", "priceGross", default=0))
        mileage = parse_int(self._pick(item, "mileage", "mileageValue", "odometer", default=0))
        power_kw = parse_int(self._pick(item, "power", "powerKw", "kw", default=0))
        power_hp = parse_int(self._pick(item, "powerHp", "hp", "ps", default=0))
        if power_kw and not power_hp:
            power_hp = round(power_kw * 1.35962)

        registration = str(self._pick(item, "firstRegistration", "firstRegistrationDate", "first_registration", default=""))
        reg_year = parse_int(self._pick(item, "firstRegistrationYear", "year", "constructionYear", default=0))
        if not reg_year and registration:
            year_m = re.search(r"\b(19|20)\d{2}\b", registration)
            reg_year = int(year_m.group()) if year_m else 0

        url = str(self._pick(item, "url", "detailPageUrl", "vipUrl", default=""))
        if ad_id and not url:
            url = f"https://suchen.mobile.de/fahrzeuge/details.html?id={ad_id}"
        elif url.startswith("/"):
            url = urljoin("https://suchen.mobile.de", url)

        images = self._images_to_list(self._pick(item, "images", "galleryImages", "pictures", "photos", default=[]))

        # Extract fuel/transmission from equipment if not directly available
        equipment_raw = self._pick(item, "equipment", "features", "ausstattung", default=[])
        if isinstance(equipment_raw, str):
            equipment_raw = [equipment_raw]
        equipment_list = equipment_raw if isinstance(equipment_raw, list) else []
        eq_info = self._extract_from_equipment(equipment_list)
        raw_trans = str(self._pick(item, "transmission", "gearbox", default=""))
        raw_fuel = str(self._pick(item, "fuel", "fuelType", default=""))
        resolved_trans = normalize_transmission(raw_trans) if raw_trans else eq_info["transmission"]
        resolved_fuel = normalize_fuel(raw_fuel) if raw_fuel else eq_info["fuel_type"]

        return {
            "id": ad_id or f"mobilede-{abs(hash(title + brand + model))}",
            "brand": brand,
            "model": model,
            "full_title": title or f"{brand} {model}",
            "price": price,
            "price_type": "fixed",
            "mileage": mileage,
            "power_kw": power_kw,
            "power_hp": power_hp,
            "first_registration": registration,
            "first_registration_year": reg_year,
            "transmission": resolved_trans,
            "fuel_type": resolved_fuel,
            "owners_count": self._pick(item, "owners", "ownersCount", default=None),
            "url": url,
            "images": images,
            "equipment": equipment_list[:20],
            "source": "mobile.de",
        }

    def _extract_from_json_state(self, html: str) -> List[dict]:
        seen: set[str] = set()
        cars: List[dict] = []
        for state in self._extract_json_objects(html):
            for item in self._walk_dicts(state):
                if not self._looks_like_listing(item):
                    continue
                car = self._item_to_europe_dict(item)
                if not car or car["id"] in seen:
                    continue
                seen.add(car["id"])
                cars.append(car)
                if len(cars) >= self.max_cars:
                    return cars
        return cars

    def _extract_from_cards(self, html: str) -> List[dict]:
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select("[data-testid*='result-listing'], article, [class*='listing'], [class*='vehicle']")
        cars: List[dict] = []
        seen: set[str] = set()
        for card in cards:
            link = card.select_one("a[href*='details.html'], a[href*='/fahrzeuge/details']")
            title_el = card.select_one("h2, h3, [class*='title'], [class*='headline']")
            title = title_el.get_text(" ", strip=True) if title_el else ""
            href = urljoin("https://suchen.mobile.de", link.get("href", "")) if link else ""
            id_m = re.search(r"[?&]id=(\d+)", href)
            ad_id = id_m.group(1) if id_m else ""
            if not title or (ad_id and ad_id in seen):
                continue
            seen.add(ad_id or title)
            parts = title.split(maxsplit=1)
            brand = normalize_brand(parts[0])
            model = parts[1] if len(parts) > 1 else ""
            text = card.get_text(" ", strip=True)
            img = card.select_one("img")
            car = {
                "id": ad_id or f"mobilede-{len(cars) + 1}",
                "brand": brand,
                "model": model,
                "full_title": title,
                "price": float(parse_int(text.split("€", 1)[0])) if "€" in text else 0.0,
                "price_type": "fixed",
                "mileage": parse_int(re.search(r"([\d\.\s]+)\s*km", text, re.I).group(1)) if re.search(r"([\d\.\s]+)\s*km", text, re.I) else 0,
                "power_kw": 0,
                "power_hp": 0,
                "first_registration": "",
                "first_registration_year": 0,
                "transmission": "",
                "fuel_type": "",
                "owners_count": None,
                "url": href,
                "images": [{"url": img.get("src") or img.get("data-src"), "order": 1}] if img and (img.get("src") or img.get("data-src")) else [],
                "equipment": [],
                "source": "mobile.de",
            }
            if brand:
                cars.append(car)
            if len(cars) >= self.max_cars:
                break
        return cars

    def parse(self) -> List[dict]:
        log.info("mobile.de: начало загрузки европейских объявлений...")
        html = self._get(self.url)
        if not html:
            return []
        cars = self._extract_from_json_state(html)
        if not cars:
            log.info("mobile.de: JSON-состояние не найдено, пробуем HTML-карточки")
            cars = self._extract_from_cards(html)
        min_ym = self.min_year * 100 + datetime.now().month if self.min_year else 0
        max_ym = self.max_year * 100 + datetime.now().month if self.max_year else 0
        cars = filter_records(cars, self.min_year, self.max_year, self.max_power_hp, min_ym, max_ym)
        log.info(f"mobile.de: итого {len(cars)} автомобилей")
        return cars[:self.max_cars]


# ── Парсер AutoScout24 (Европа) ──────────────────────────────────────────────

class AutoScout24Parser:
    """
    Парсит европейские объявления AutoScout24 из __NEXT_DATA__.
    Цель для каталога Европы — разнообразие: уникальные связки brand + model.
    """

    SEARCH_URL = "https://www.autoscout24.de/lst"

    UA_LIST = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    ]

    def __init__(self, max_cars: int = 220, delay: float = 1.0,
                 min_year: int = 0, max_year: int = 0, max_power_hp: int = 0,
                 unique_models: int = 200, max_pages: int = 40,
                 proxy: Optional[str] = None):
        if not REQUESTS_AVAILABLE:
            raise RuntimeError("Установите requests: pip install requests")
        if not BS4_AVAILABLE:
            raise RuntimeError("Установите beautifulsoup4: pip install beautifulsoup4")
        self.max_cars = max_cars
        self.delay = delay
        self.min_year = min_year
        self.max_year = max_year
        self.max_power_hp = max_power_hp
        self.unique_models = unique_models
        self.max_pages = max_pages
        self.proxy = proxy
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": random.choice(self.UA_LIST),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
            "Referer": "https://www.autoscout24.de/",
        })

    def _build_url(self, page: int) -> str:
        params = {
            "atype": "C",
            "cy": "D",
            "sort": "standard",
            "ustate": "N,U",
            "page": page,
        }
        if self.min_year:
            params["fregfrom"] = self.min_year
        if self.max_year:
            params["fregto"] = self.max_year
        if self.max_power_hp:
            params["powerto"] = round(self.max_power_hp / 1.35962)
        return f"{self.SEARCH_URL}?{urlencode(params)}"

    def _get(self, url: str) -> Optional[str]:
        proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None
        try:
            resp = self._session.get(url, proxies=proxies, timeout=25)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            log.warning(f"AutoScout24: ошибка запроса {url}: {e}")
            return None

    def _vehicle_detail(self, item: dict, label: str) -> str:
        for detail in item.get("vehicleDetails") or []:
            if str(detail.get("ariaLabel", "")).lower() == label.lower():
                return str(detail.get("data") or "")
        return ""

    def _item_to_record(self, item: dict) -> Optional[dict]:
        vehicle = item.get("vehicle") or {}
        brand = normalize_brand(str(vehicle.get("make") or ""))
        model = str(vehicle.get("model") or vehicle.get("modelGroup") or "").strip()
        if not brand or not model:
            return None

        title = str(vehicle.get("modelVersionInput") or "").strip()
        if not title:
            title = f"{brand} {model}".strip()

        price = parse_int((item.get("price") or {}).get("priceFormatted"))
        mileage = parse_int(vehicle.get("mileageInKm") or self._vehicle_detail(item, "Kilometerstand"))
        first_registration = self._vehicle_detail(item, "Erstzulassung")
        reg_year = parse_int(first_registration[-4:] if len(first_registration) >= 4 else "")
        power_text = self._vehicle_detail(item, "Leistung")
        power_hp = parse_power_hp(power_text)
        power_kw = round(power_hp / 1.35962) if power_hp else 0

        fuel = str(vehicle.get("fuel") or self._vehicle_detail(item, "Kraftstoff") or "")
        transmission = str(vehicle.get("transmission") or self._vehicle_detail(item, "Getriebe") or "")
        images = [
            {"url": str(url).replace("/250x188.webp", "/1024x768.webp"), "order": index}
            for index, url in enumerate(item.get("images") or [], start=1)
            if url
        ][:12]
        url = str(item.get("url") or "")
        if url.startswith("/"):
            url = urljoin("https://www.autoscout24.de", url)

        record = {
            "id": str(item.get("id") or ""),
            "brand": brand,
            "model": model,
            "full_title": title,
            "price": float(price),
            "price_type": "fixed",
            "mileage": mileage,
            "power_kw": power_kw,
            "power_hp": power_hp,
            "first_registration": first_registration,
            "first_registration_year": reg_year,
            "transmission": normalize_transmission(transmission) if transmission else "",
            "fuel_type": normalize_fuel(fuel) if fuel else "",
            "owners_count": None,
            "url": url,
            "images": images,
            "equipment": [str(vehicle.get("subtitle") or "")] if vehicle.get("subtitle") else [],
            "source": "autoscout24.de",
        }
        return record

    def _extract_page(self, html: str) -> List[dict]:
        soup = BeautifulSoup(html, "html.parser")
        script = soup.find("script", id="__NEXT_DATA__")
        if not script or not script.string:
            return []
        try:
            data = json.loads(script.string)
        except Exception:
            return []
        items = (((data.get("props") or {}).get("pageProps") or {}).get("listings") or [])
        records = []
        for item in items:
            if not isinstance(item, dict):
                continue
            record = self._item_to_record(item)
            if record:
                records.append(record)
        return records

    def parse(self) -> List[dict]:
        log.info("AutoScout24: начало загрузки европейских объявлений...")
        records: List[dict] = []
        seen_ids: set[str] = set()
        seen_models: set[str] = set()

        for page in range(1, self.max_pages + 1):
            html = self._get(self._build_url(page))
            if not html:
                break
            min_ym = self.min_year * 100 + datetime.now().month if self.min_year else 0
            max_ym = self.max_year * 100 + datetime.now().month if self.max_year else 0
            page_records = filter_records(self._extract_page(html), self.min_year, self.max_year, self.max_power_hp, min_ym, max_ym)
            if not page_records:
                log.info(f"AutoScout24: страница {page}, данных нет")
                break
            for record in page_records:
                record_id = str(record.get("id") or record.get("url") or "")
                model_key = f"{record.get('brand', '').lower()}|{record.get('model', '').lower()}"
                if record_id in seen_ids or model_key in seen_models:
                    continue
                if not record.get("images"):
                    continue
                seen_ids.add(record_id)
                seen_models.add(model_key)
                records.append(record)
                if len(records) >= self.max_cars or len(seen_models) >= self.unique_models:
                    break
            log.info(f"AutoScout24: стр. {page}, собрано {len(records)} авто / {len(seen_models)} моделей")
            if len(records) >= self.max_cars or len(seen_models) >= self.unique_models:
                break
            time.sleep(self.delay + random.uniform(0, 0.4))

        log.info(f"AutoScout24: итого {len(records)} авто, уникальных моделей {len(seen_models)}")
        return records[:self.max_cars]


# ── Авто-синхронизация стока ──────────────────────────────────────────────────

def sync_georgia_stock(source: str = "myauto", max_cars: int = 100,
                       stock_file: str = "cars_georgia_stock.json",
                       delay: float = 1.5, proxy: Optional[str] = None,
                       min_year: int = 0, max_year: int = 0, max_power_hp: int = 0,
                       min_year_month: int = 0, max_year_month: int = 0) -> int:
    """
    Загружает актуальные объявления из myauto.ge или ap.ge,
    объединяет с текущим стоком и сохраняет в stock_file.
    Возвращает количество новых записей.
    """
    log.info(f"Авто-синхронизация стока из {source} → {stock_file}")

    # Загружаем существующий сток
    existing: List[dict] = []
    if os.path.exists(stock_file):
        try:
            with open(stock_file, encoding="utf-8") as f:
                existing = json.load(f)
            log.info(f"Текущий сток: {len(existing)} записей")
        except Exception as e:
            log.warning(f"Не удалось загрузить {stock_file}: {e}")

    def stock_key(item: dict) -> str:
        vin = str(item.get("vin", "")).upper().strip()
        if vin:
            return f"vin:{vin}"
        url = str(item.get("url") or item.get("description") or "").strip()
        if url:
            return f"url:{url}"
        return "car:" + "|".join(str(item.get(k, "")).strip().lower()
                                 for k in ("brand", "model", "year", "mileage", "price"))

    existing_keys = {stock_key(c) for c in existing}

    # Парсим новые данные
    if source == "myauto":
        parser = MyAutoGeParser(max_cars=max_cars, delay=delay, min_year=min_year,
                                max_year=max_year, max_power_hp=max_power_hp, proxy=proxy)
    elif source in ("apge", "ap.ge"):
        parser = ApGeParser(max_cars=max_cars, delay=delay, proxy=proxy)
    else:
        log.error(f"Неизвестный источник для синхронизации: {source}")
        return 0

    new_cars = parser.parse()
    new_cars = dedup_by_vin(new_cars)
    new_cars = filter_cars(new_cars, min_year, max_year, max_power_hp, min_year_month, max_year_month)
    if not new_cars:
        log.warning("Источник не вернул автомобили; существующий stock-файл оставлен без изменений")
        return 0

    # Собираем свежую выдачу первой, чтобы на сайте не висели старые объявления
    # с уже удаленными фотографиями.
    fresh_records: List[dict] = []
    fresh_keys = set()
    for car in new_cars:
        url = car.description
        if url and not url.startswith("http"):
            url = "https://" + url
        d = {
            "id": car.id,
            "brand": car.brand,
            "model": car.model,
            "fullName": f"{car.brand} {car.model}".strip(),
            "year": car.year,
            "month": car.extra.get("prod_month") or 0,
            "price": car.price,
            "price_currency": "USD",
            "mileage": car.mileage,
            "engine": car.engine,
            "fuel_type": car.fuel_type,
            "transmission": car.transmission,
            "color": car.color,
            "drive": car.drive,
            "vin": car.vin,
            "url": url,
            "region": "georgia",
            "regionCode": "georgia",
            "images": car.extra.get("images") or ([{"url": car.photos, "order": 1}] if car.photos else []),
            "source": car.source or source,
        }
        key = stock_key(d)
        if key in fresh_keys:
            continue
        fresh_records.append(d)
        fresh_keys.add(key)

    added = len(fresh_keys - existing_keys)
    archived = [item for item in existing if stock_key(item) not in fresh_keys]
    existing = fresh_records + archived

    # Каждый запуск поддерживает публичный каталог в текущих фильтрах сайта.
    before_filter = len(existing)
    existing = filter_records(existing, min_year, max_year, max_power_hp, min_year_month, max_year_month)
    if len(existing) < before_filter:
        log.info(f"Фильтр каталога: убрано {before_filter - len(existing)} записей вне условий")

    # Перенумеруем и сохраняем
    for i, item in enumerate(existing, start=1):
        item["id"] = i

    _atomic_write_json(existing, stock_file)

    log.info(f"Сток обновлён: +{added} новых, итого {len(existing)} записей → {stock_file}")
    return added

def _atomic_write_json(data: Any, filepath: str) -> None:
    path = Path(filepath)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def export_json(cars: List[Car], filepath: str) -> None:
    data = []
    for car in cars:
        d = asdict(car)
        d.pop("extra", None)
        d.pop("source", None)
        data.append(d)
    _atomic_write_json(data, filepath)
    log.info(f"JSON экспорт: {filepath} ({len(cars)} записей)")


def export_json_records(records: List[dict], filepath: str) -> None:
    _atomic_write_json(records, filepath)
    log.info(f"JSON экспорт: {filepath} ({len(records)} записей)")


def validate_catalog_file(filepath: str, required: List[str], min_records: int = 1) -> int:
    if not os.path.exists(filepath):
        raise RuntimeError(f"Каталог не найден: {filepath}")
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise RuntimeError(f"{filepath}: ожидался JSON-массив")
    if len(data) < min_records:
        raise RuntimeError(f"{filepath}: мало записей ({len(data)} < {min_records})")
    bad = []
    for index, item in enumerate(data[: min(len(data), 50)], start=1):
        if not isinstance(item, dict):
            bad.append(f"#{index}: не объект")
            continue
        missing = [key for key in required if item.get(key) in (None, "")]
        if missing:
            bad.append(f"#{index}: нет {', '.join(missing)}")
    if bad:
        raise RuntimeError(f"{filepath}: ошибки структуры: {'; '.join(bad[:5])}")
    log.info(f"Каталог OK: {filepath} ({len(data)} записей)")
    return len(data)


def validate_catalog_constraints(filepath: str, min_year_month: int, max_year_month: int,
                                 max_power_hp: int, max_power_kw: int) -> None:
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)
    bad = []
    for item in data:
        year, month = record_year_month(item)
        year_month = year * 100 + (month or 1)
        hp = record_power_hp(item)
        kw = record_power_kw(item)
        if not year or year_month < min_year_month or year_month > max_year_month:
            bad.append(f"{item.get('brand')} {item.get('model')}: {year_month}")
        elif hp and hp > max_power_hp:
            bad.append(f"{item.get('brand')} {item.get('model')}: {hp} hp")
        elif kw and kw > max_power_kw:
            bad.append(f"{item.get('brand')} {item.get('model')}: {kw} kW")
    if bad:
        raise RuntimeError(f"{filepath}: записи вне условий 05.2021-05.2023, <=160 hp, <=115 kW: {'; '.join(bad[:5])}")


def validate_public_catalogs() -> None:
    validate_catalog_file("cars_europe_new.json", ["id", "brand", "model", "price", "images"], min_records=10)
    validate_catalog_file("cars_georgia_stock.json", ["id", "brand", "model", "price", "url"], min_records=20)
    min_ym, max_ym = month_range_from_age(3, 5)
    validate_catalog_constraints("cars_europe_new.json", min_ym, max_ym, 160, 115)
    validate_catalog_constraints("cars_georgia_stock.json", min_ym, max_ym, 160, 115)


def export_csv(cars: List[Car], filepath: str) -> None:
    fields = ["id", "brand", "model", "year", "engine", "vin", "price",
              "mileage", "fuel_type", "transmission", "color", "drive",
              "power", "date", "description", "photos", "folder_id", "sold"]
    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for car in cars:
            d = asdict(car)
            row = {k: d.get(k, "") for k in fields}
            writer.writerow(row)
    log.info(f"CSV экспорт: {filepath} ({len(cars)} записей)")


def inject_into_script_js(cars: List[Car], script_path: str = "script.js") -> bool:
    """
    Заменяет блок carsData = [...] в script.js новыми данными.
    Создаёт резервную копию script.js.backup перед изменением.
    """
    if not os.path.exists(script_path):
        log.error(f"Файл не найден: {script_path}")
        return False

    with open(script_path, encoding="utf-8") as f:
        content = f.read()

    # Ищем блок: const carsData = [ ... ];
    pattern = re.compile(r'(const\s+carsData\s*=\s*\[)(.*?)(\];)', re.DOTALL)
    match = pattern.search(content)
    if not match:
        log.error("carsData[] не найдено в script.js")
        return False

    # Сохраняем бэкап
    backup = script_path + ".backup"
    with open(backup, "w", encoding="utf-8") as f:
        f.write(content)
    log.info(f"Бэкап сохранён: {backup}")

    # Генерируем новый массив
    js_items = ",\n".join(car.to_js_object() for car in cars)
    new_block = f"const carsData = [\n{js_items}\n];"
    new_content = pattern.sub(new_block, content)

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    log.info(f"script.js обновлён: {len(cars)} автомобилей")
    return True


# ── Сводный отчёт ────────────────────────────────────────────────────────────

def print_summary(cars: List[Car]) -> None:
    if not cars:
        print("\nНет данных для отображения.")
        return
    brands: Dict[str, int] = {}
    for car in cars:
        brands[car.brand] = brands.get(car.brand, 0) + 1
    prices = [c.price for c in cars if c.price > 0]
    print(f"\n{'='*50}")
    print(f"  Итого автомобилей : {len(cars)}")
    print(f"  Уникальных марок  : {len(brands)}")
    if prices:
        print(f"  Цена мин/макс     : {min(prices):,} / {max(prices):,} ₽")
        print(f"  Цена средняя      : {sum(prices)//len(prices):,} ₽")
    print(f"  Продано           : {sum(1 for c in cars if c.sold)}")
    print(f"  Без VIN           : {sum(1 for c in cars if not c.vin)}")
    print(f"\n  Топ марки:")
    for brand, cnt in sorted(brands.items(), key=lambda x: -x[1])[:10]:
        bar = "█" * min(cnt, 30)
        print(f"    {brand:<20} {cnt:>3}  {bar}")
    print(f"{'='*50}\n")


# ── CLI ───────────────────────────────────────────────────────────────────────

def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="EXPO MIR — Парсер данных об автомобилях",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--source", choices=["csv", "json", "drom", "html", "myauto", "apge", "mobilede", "autoscout24", "europe", "auto"],
                   default="auto", help="Источник данных (default: auto-detect)")
    p.add_argument("--input", "-i", help="Путь к CSV/JSON файлу")
    p.add_argument("--url", "-u", help="URL для парсинга (html/drom)")
    p.add_argument("--out", "-o", help="Путь к выходному файлу (.json или .csv)")
    p.add_argument("--region", default="all", help="Регион для drom.ru (tbilisi, moscow, ...)")
    p.add_argument("--max", type=int, default=100, dest="max_cars",
                   help="Максимум авто (для web-парсеров)")
    p.add_argument("--min-records", type=int, default=1,
                   help="Минимум записей для сохранения нового JSON (защита от битого парсинга)")
    p.add_argument("--min-year", type=int, default=0, help="Минимальный год выпуска/регистрации")
    p.add_argument("--max-year", type=int, default=0, help="Максимальный год выпуска/регистрации")
    p.add_argument("--min-age", type=int, default=0, help="Минимальный возраст авто в годах")
    p.add_argument("--max-age", type=int, default=0, help="Максимальный возраст авто в годах")
    p.add_argument("--max-power-hp", type=int, default=0, help="Максимальная мощность в л.с.")
    p.add_argument("--unique-models", type=int, default=0,
                   help="Минимальная цель по уникальным связкам марка+модель для европейского каталога")
    p.add_argument("--max-pages", type=int, default=40,
                   help="Максимум страниц для многостраничных европейских источников")
    p.add_argument("--delay", type=float, default=2.5,
                   help="Задержка между запросами в секундах")
    p.add_argument("--proxy", help="HTTP/SOCKS прокси (http://user:pass@host:port)")
    p.add_argument("--inject", action="store_true",
                   help="Вставить результат в script.js (требует --input JSON)")
    p.add_argument("--script", default="script.js",
                   help="Путь к script.js для --inject (default: script.js)")
    p.add_argument("--sync-stock", action="store_true",
                   help="Авто-обновить cars_georgia_stock.json из выбранного источника")
    p.add_argument("--validate-catalogs", action="store_true",
                   help="Проверить публичные JSON-каталоги сайта и выйти")
    p.add_argument("--fail-empty", action="store_true",
                   help="Завершаться с ошибкой, если источник не вернул автомобилей")
    p.add_argument("--stock-file", default="cars_georgia_stock.json",
                   help="Путь к файлу стока для --sync-stock")
    p.add_argument("--no-dedup", action="store_true", help="Не удалять дубликаты по VIN")
    p.add_argument("--validate-vin", action="store_true",
                   help="Предупреждать о VIN с неверным форматом")
    p.add_argument("--summary", action="store_true", default=True,
                   help="Показать сводную статистику (default: вкл)")
    p.add_argument("--quiet", "-q", action="store_true", help="Минимум вывода в консоль")
    return p


def auto_detect_source(args: argparse.Namespace) -> str:
    if args.url:
        if "autoscout24" in (args.url or ""):
            return "autoscout24"
        if "mobile.de" in (args.url or ""):
            return "mobilede"
        if "drom.ru" in (args.url or ""):
            return "drom"
        if "myauto.ge" in (args.url or ""):
            return "myauto"
        if "ap.ge" in (args.url or ""):
            return "apge"
        return "html"
    if args.input:
        ext = Path(args.input).suffix.lower()
        if ext == ".csv":
            return "csv"
        if ext in (".json", ".js"):
            return "json"
    return "csv"


def proxy_from_env(source: str) -> Optional[str]:
    specific = {
        "myauto": "MYAUTO_PROXY",
        "apge": "APGE_PROXY",
        "ap.ge": "APGE_PROXY",
        "mobilede": "MOBILEDE_PROXY",
        "autoscout24": "AUTOSCOUT24_PROXY",
        "europe": "MOBILEDE_PROXY",
        "drom": "DROM_PROXY",
        "html": "PARSER_PROXY",
    }.get(source)
    if specific and os.getenv(specific):
        return os.getenv(specific)
    return os.getenv("PARSER_PROXY") or None


def run(args: argparse.Namespace) -> None:
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    if getattr(args, "validate_catalogs", False):
        validate_public_catalogs()
        return

    source = args.source
    if source == "auto":
        source = auto_detect_source(args)
        log.info(f"Авто-определение источника: {source}")

    proxy = args.proxy or proxy_from_env(source)
    age_min_year, age_max_year = year_range_from_age(args.min_age, args.max_age)
    age_min_ym, age_max_ym = month_range_from_age(args.min_age, args.max_age)
    min_year = args.min_year or age_min_year
    max_year = args.max_year or age_max_year
    min_year_month = 0 if args.min_year else age_min_ym
    max_year_month = 0 if args.max_year else age_max_ym

    # Синхронизация стока (быстрый путь)
    if getattr(args, "sync_stock", False):
        sync_src = source if source in ("myauto", "apge") else "myauto"
        added = sync_georgia_stock(
            source=sync_src,
            max_cars=args.max_cars,
            stock_file=args.stock_file,
            delay=args.delay,
            proxy=proxy,
            min_year=min_year,
            max_year=max_year,
            max_power_hp=args.max_power_hp,
            min_year_month=min_year_month,
            max_year_month=max_year_month,
        )
        log.info(f"Синхронизация завершена: +{added} новых авто")
        return

    cars: List[Car] = []
    europe_records: List[dict] = []

    if source == "csv":
        if not args.input:
            log.error("Укажите --input <файл.csv>")
            sys.exit(1)
        cars = CsvParser(args.input).parse()

    elif source == "json":
        if not args.input:
            log.error("Укажите --input <файл.json>")
            sys.exit(1)
        cars = JsonParser(args.input).parse()

    elif source == "myauto":
        cars = MyAutoGeParser(
            max_cars=args.max_cars,
            delay=args.delay,
            min_year=min_year,
            max_year=max_year,
            max_power_hp=args.max_power_hp,
            proxy=proxy,
        ).parse()

    elif source in ("apge", "ap.ge"):
        cars = ApGeParser(
            max_cars=args.max_cars,
            delay=args.delay,
            proxy=proxy,
        ).parse()

    elif source == "mobilede":
        europe_records = MobileDeParser(
            max_cars=args.max_cars,
            delay=args.delay,
            url=args.url or "",
            min_year=min_year,
            max_year=max_year,
            max_power_hp=args.max_power_hp,
            proxy=proxy,
        ).parse()

    elif source in ("autoscout24", "europe"):
        europe_records = AutoScout24Parser(
            max_cars=args.max_cars,
            delay=args.delay,
            min_year=min_year,
            max_year=max_year,
            max_power_hp=args.max_power_hp,
            unique_models=args.unique_models or min(args.max_cars, 200),
            max_pages=args.max_pages,
            proxy=proxy,
        ).parse()

    elif source == "drom":
        cars = DromParser(region=args.region, max_cars=args.max_cars,
                          delay=args.delay, proxy=proxy).parse()

    elif source == "html":
        if not args.url:
            log.error("Укажите --url <адрес сайта>")
            sys.exit(1)
        cars = HtmlParser(url=args.url, delay=args.delay, proxy=proxy).parse()

    if cars:
        cars = filter_cars(cars, min_year, max_year, args.max_power_hp, min_year_month, max_year_month)

    if europe_records:
        if len(europe_records) < args.min_records:
            log.error(f"Новый каталог слишком мал: {len(europe_records)} < {args.min_records}. Сохранение отменено.")
            sys.exit(2)
        if args.out:
            out = args.out if args.out.endswith(".json") else args.out + ".json"
            export_json_records(europe_records, out)
        else:
            print(json.dumps(europe_records, ensure_ascii=False, indent=2))
        print(f"\n{'='*50}")
        print(f"  Итого автомобилей : {len(europe_records)}")
        print(f"  Источник           : {source}")
        print(f"  Файл               : {args.out or 'stdout'}")
        print(f"{'='*50}\n")
        return

    if not cars:
        log.warning("Не найдено ни одного автомобиля.")
        if args.fail_empty:
            sys.exit(2)
        sys.exit(0)

    # Нормализация / дедупликация
    if not args.no_dedup:
        before = len(cars)
        cars = dedup_by_vin(cars)
        if len(cars) < before:
            log.info(f"Дедупликация: убрано {before - len(cars)} дублей")

    if getattr(args, "validate_vin", False):
        for car in cars:
            if car.vin and not validate_vin(car.vin):
                log.warning(f"Неверный VIN: {car.vin} ({car.brand} {car.model})")

    cars = renumber(cars)

    # Экспорт
    if args.out:
        if len(cars) < args.min_records:
            log.error(f"Новый экспорт слишком мал: {len(cars)} < {args.min_records}. Сохранение отменено.")
            sys.exit(2)
        out = args.out
        if out.endswith(".csv"):
            export_csv(cars, out)
        else:
            if not out.endswith(".json"):
                out += ".json"
            export_json(cars, out)
    else:
        # По умолчанию — JSON в stdout
        data = []
        for car in cars:
            d = asdict(car)
            d.pop("extra", None)
            d.pop("source", None)
            data.append(d)
        print(json.dumps(data, ensure_ascii=False, indent=2))

    # Вставить в script.js
    if args.inject:
        inject_into_script_js(cars, args.script)

    if args.summary:
        print_summary(cars)


def main() -> None:
    p = build_arg_parser()
    args = p.parse_args()
    run(args)


if __name__ == "__main__":
    main()
