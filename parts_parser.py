#!/usr/bin/env python3
"""
parts_parser.py — импорт запчастей из CSV/JSON и синхронизация с Supabase.

Использование:
    python parts_parser.py --input parts_catalog.csv
    python parts_parser.py --input parts_catalog.json
    python parts_parser.py --input parts_catalog.csv --dry-run
    python parts_parser.py --input parts_catalog.csv --quiet

Поддерживаемые форматы CSV (заголовок обязателен):
    oem_number, name, brand, category, price_usd, price_kgs,
    stock_qty, condition, compatible_cars, description, image_url

Поддерживаемый формат JSON: массив объектов с теми же полями.

Конфигурация (из переменных окружения или config.py):
    SUPABASE_URL — URL проекта Supabase
    SUPABASE_SERVICE_KEY — Service-role ключ
"""

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Optional

import requests

# ---------------------------------------------------------------------------
# Конфигурация
# ---------------------------------------------------------------------------

BATCH_SIZE = 50


def _load_config() -> dict:
    """Загружает SUPABASE_URL + SUPABASE_SERVICE_KEY из env или config.py."""
    cfg: dict = {}

    # 1. Переменные окружения
    cfg["url"] = os.environ.get("SUPABASE_URL", "").rstrip("/")
    cfg["key"] = os.environ.get("SUPABASE_SERVICE_KEY", "")

    # 2. config.py как запасной вариант
    if not cfg["url"] or not cfg["key"]:
        try:
            sys.path.insert(0, os.path.dirname(__file__))
            import config as _cfg
            if not cfg["url"]:
                cfg["url"] = getattr(_cfg, "SUPABASE_URL", "").rstrip("/")
            if not cfg["key"]:
                cfg["key"] = getattr(_cfg, "SUPABASE_SERVICE_KEY", "")
        except ImportError:
            pass

    return cfg


# ---------------------------------------------------------------------------
# Нормализация одной записи
# ---------------------------------------------------------------------------

def _normalize_part(row: dict) -> Optional[dict]:
    """
    Нормализует сырую строку из CSV/JSON в формат таблицы parts.
    Возвращает None, если запись невалидна (нет oem_number и name).
    """
    oem = str(row.get("oem_number") or row.get("oem") or "").strip()
    name = str(row.get("name") or "").strip()
    if not oem and not name:
        return None

    # compatible_cars: строка → массив (разделитель | или ,)
    compat_raw = str(row.get("compatible_cars") or "")
    if compat_raw:
        sep = "|" if "|" in compat_raw else ","
        compat_list = [c.strip() for c in compat_raw.split(sep) if c.strip()]
    else:
        compat_list = []

    def _to_float(val: Any) -> Optional[float]:
        try:
            v = str(val).strip().replace(",", ".")
            return float(v) if v else None
        except (ValueError, TypeError):
            return None

    def _to_int(val: Any) -> Optional[int]:
        try:
            v = str(val).strip()
            return int(float(v)) if v else None
        except (ValueError, TypeError):
            return None

    return {
        "oem_number":      oem or None,
        "name":            name,
        "brand":           str(row.get("brand") or "").strip() or None,
        "category":        str(row.get("category") or "").strip() or None,
        "price_usd":       _to_float(row.get("price_usd")),
        "price_kgs":       _to_float(row.get("price_kgs")),
        "stock_qty":       _to_int(row.get("stock_qty") or row.get("qty")),
        "condition":       str(row.get("condition") or "used").strip() or "used",
        "compatible_cars": compat_list,
        "description":     str(row.get("description") or "").strip() or None,
        "image_url":       str(row.get("image_url") or "").strip() or None,
        "is_active":       True,
        "updated_at":      datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Импортёры
# ---------------------------------------------------------------------------

class CsvPartsImporter:
    """Читает CSV файл с запчастями."""

    def load(self, path: str) -> list:
        records = []
        with open(path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                part = _normalize_part(row)
                if part:
                    records.append(part)
        return records


class JsonPartsImporter:
    """Читает JSON файл (массив объектов) с запчастями."""

    def load(self, path: str) -> list:
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
        if not isinstance(raw, list):
            raise ValueError("JSON файл должен содержать массив (list) объектов")
        records = []
        for row in raw:
            part = _normalize_part(row)
            if part:
                records.append(part)
        return records


# ---------------------------------------------------------------------------
# Supabase upsert
# ---------------------------------------------------------------------------

def _sb_upsert_parts(cfg: dict, batch: list) -> int:
    """
    Upsert батча записей в таблицу parts по конфликту oem_number.
    Возвращает количество успешно обработанных записей.
    """
    url = cfg["url"]
    key = cfg["key"]
    if not url or not key:
        raise RuntimeError("SUPABASE_URL или SUPABASE_SERVICE_KEY не заданы")

    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation",
    }
    endpoint = f"{url}/rest/v1/parts?on_conflict=oem_number"
    resp = requests.post(endpoint, headers=headers, json=batch, timeout=30)
    resp.raise_for_status()
    return len(batch)


def sync_parts_to_supabase(records: list, cfg: dict, dry_run: bool = False,
                            quiet: bool = False) -> int:
    """
    Отправляет все записи в Supabase батчами по BATCH_SIZE.
    Возвращает суммарное количество успешно загруженных записей.
    """
    if not records:
        if not quiet:
            print("[parts] Нет записей для синхронизации.")
        return 0

    total = 0
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i:i + BATCH_SIZE]
        if dry_run:
            if not quiet:
                print(f"[dry-run] Батч {i // BATCH_SIZE + 1}: {len(batch)} записей (не отправляем)")
            total += len(batch)
        else:
            try:
                n = _sb_upsert_parts(cfg, batch)
                total += n
                if not quiet:
                    print(f"[parts] Батч {i // BATCH_SIZE + 1}: загружено {n} записей")
            except requests.HTTPError as exc:
                print(f"[parts] Ошибка батча {i // BATCH_SIZE + 1}: {exc}", file=sys.stderr)
                if exc.response is not None:
                    print(exc.response.text[:500], file=sys.stderr)
            except Exception as exc:
                print(f"[parts] Неожиданная ошибка: {exc}", file=sys.stderr)
            time.sleep(0.3)

    return total


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Импорт запчастей из CSV/JSON в Supabase parts таблицу"
    )
    parser.add_argument("--input", "-i", required=True,
                        help="Путь к CSV или JSON файлу с запчастями")
    parser.add_argument("--dry-run", action="store_true",
                        help="Показать что будет загружено, не отправляя в Supabase")
    parser.add_argument("--quiet", action="store_true",
                        help="Минимальный вывод (только ошибки)")
    args = parser.parse_args()

    input_path = args.input
    if not os.path.isfile(input_path):
        print(f"[parts] Файл не найден: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Выбор импортёра по расширению
    ext = os.path.splitext(input_path)[1].lower()
    if ext == ".csv":
        importer = CsvPartsImporter()
    elif ext == ".json":
        importer = JsonPartsImporter()
    else:
        print(f"[parts] Неподдерживаемый формат: {ext}. Используйте .csv или .json",
              file=sys.stderr)
        sys.exit(1)

    if not args.quiet:
        print(f"[parts] Загружаем файл: {input_path}")

    try:
        records = importer.load(input_path)
    except Exception as exc:
        print(f"[parts] Ошибка чтения файла: {exc}", file=sys.stderr)
        sys.exit(1)

    if not args.quiet:
        print(f"[parts] Прочитано записей: {len(records)}")

    if not records:
        print("[parts] Нет валидных записей для импорта.")
        sys.exit(0)

    cfg = _load_config()
    total = sync_parts_to_supabase(records, cfg, dry_run=args.dry_run, quiet=args.quiet)

    if not args.quiet:
        action = "Готово (dry-run)" if args.dry_run else "Готово"
        print(f"[parts] {action}: {total} из {len(records)} записей.")


if __name__ == "__main__":
    main()
