#!/usr/bin/env python3
"""
generate_sitemap.py — Генерация sitemap.xml для cmsauto.store (GitHub Pages).

Собирает:
  1. Все статические HTML-страницы из корня репозитория.
  2. (Опционально) Уникальные бренды из cars_georgia_stock.json и cars_europe_new.json
     для дополнительных URL-параметров (не создаёт отдельных страниц — просто записи
     с lastmod на уровне всего каталога).

Запуск:
    python generate_sitemap.py
    python generate_sitemap.py --base-url https://cmsauto.store
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_URL = "https://cmsauto.store"

STATIC_PAGES = [
    ("index.html",           0.9, "daily"),
    ("georgia-catalog.html", 0.85, "hourly"),
    ("georgia-stock.html",   0.8, "hourly"),
    ("europe-orders.html",   0.8, "hourly"),
    ("korea-orders.html",    0.7, "daily"),
    ("usa-orders.html",      0.7, "weekly"),
    ("china-orders.html",    0.7, "weekly"),
    ("parts-orders.html",    0.7, "daily"),
]


def lastmod_for_file(filepath: str) -> str:
    """Дата последнего изменения файла (или сегодняшняя дата)."""
    try:
        mtime = os.path.getmtime(filepath)
        return datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%d")
    except OSError:
        return datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")


def load_json_safe(filepath: str) -> list:
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def generate_sitemap(base_url: str, repo_root: str, output: str) -> int:
    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']

    # Статические страницы
    for page_path, priority, changefreq in STATIC_PAGES:
        full_path = os.path.join(repo_root, page_path)
        lastmod = lastmod_for_file(full_path)
        slug = "" if page_path == "index.html" else page_path
        url = f"{base_url.rstrip('/')}/{slug}".rstrip("/")
        lines.append(f"  <url>")
        lines.append(f"    <loc>{url}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append(f"    <changefreq>{changefreq}</changefreq>")
        lines.append(f"    <priority>{priority:.1f}</priority>")
        lines.append(f"  </url>")

    # Данные из каталогов авто — уникальные марки/модели как дополнительные записи
    georgia = load_json_safe(os.path.join(repo_root, "cars_georgia_stock.json"))
    europe  = load_json_safe(os.path.join(repo_root, "cars_europe_new.json"))
    korea   = load_json_safe(os.path.join(repo_root, "cars_korea_stock.json"))

    # Уникальные бренды Грузии → добавляем URL фильтра ?brand=X на georgia-stock.html
    seen_brands_georgia: set = set()
    for rec in georgia:
        brand = str(rec.get("brand") or "").strip()
        if brand and brand not in seen_brands_georgia:
            seen_brands_georgia.add(brand)
            safe_brand = brand.replace(" ", "%20")
            url = f"{base_url.rstrip('/')}/georgia-stock.html?brand={safe_brand}"
            lines.append(f"  <url>")
            lines.append(f"    <loc>{url}</loc>")
            lines.append(f"    <lastmod>{today}</lastmod>")
            lines.append(f"    <changefreq>daily</changefreq>")
            lines.append(f"    <priority>0.6</priority>")
            lines.append(f"  </url>")

    # Уникальные бренды Европы
    seen_brands_europe: set = set()
    for rec in europe:
        brand = str(rec.get("brand") or "").strip()
        if brand and brand not in seen_brands_europe:
            seen_brands_europe.add(brand)
            safe_brand = brand.replace(" ", "%20")
            url = f"{base_url.rstrip('/')}/europe-orders.html?brand={safe_brand}"
            lines.append(f"  <url>")
            lines.append(f"    <loc>{url}</loc>")
            lines.append(f"    <lastmod>{today}</lastmod>")
            lines.append(f"    <changefreq>daily</changefreq>")
            lines.append(f"    <priority>0.6</priority>")
            lines.append(f"  </url>")

    # Уникальные бренды Кореи
    seen_brands_korea: set = set()
    for rec in korea:
        brand = str(rec.get("brand") or "").strip()
        if brand and brand not in seen_brands_korea:
            seen_brands_korea.add(brand)
            safe_brand = brand.replace(" ", "%20")
            url = f"{base_url.rstrip('/')}/korea-orders.html?brand={safe_brand}"
            lines.append(f"  <url>")
            lines.append(f"    <loc>{url}</loc>")
            lines.append(f"    <lastmod>{today}</lastmod>")
            lines.append(f"    <changefreq>daily</changefreq>")
            lines.append(f"    <priority>0.5</priority>")
            lines.append(f"  </url>")

    lines.append("</urlset>")
    content = "\n".join(lines) + "\n"

    output_path = os.path.join(repo_root, output)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    total_urls = sum(1 for l in lines if "<loc>" in l)
    print(f"sitemap.xml сгенерирован: {output_path} ({total_urls} URL)")
    return total_urls


def main() -> None:
    p = argparse.ArgumentParser(description="Генерация sitemap.xml для cmsauto.store")
    p.add_argument("--base-url", default=BASE_URL, help="Базовый URL сайта")
    p.add_argument("--output", default="sitemap.xml", help="Путь к выходному файлу")
    p.add_argument("--repo-root", default=".", help="Корень репозитория")
    args = p.parse_args()

    total = generate_sitemap(args.base_url, args.repo_root, args.output)
    if total == 0:
        print("ПРЕДУПРЕЖДЕНИЕ: sitemap.xml пустой", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
