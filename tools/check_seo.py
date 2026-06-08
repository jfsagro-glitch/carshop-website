#!/usr/bin/env python3
"""Validate public-page SEO metadata and sitemap consistency."""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from bs4 import BeautifulSoup

from apply_seo_metadata import BASE_URL, PAGES


ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def validate_page(filename: str, page: dict, titles: set[str], descriptions: set[str]) -> None:
    soup = BeautifulSoup((ROOT / filename).read_text(encoding="utf-8"), "html.parser")
    title = soup.title.get_text(strip=True) if soup.title else ""
    description = soup.find("meta", attrs={"name": "description"})
    canonical = soup.find("link", attrs={"rel": "canonical"})
    robots = soup.find("meta", attrs={"name": "robots"})
    expected_url = f"{BASE_URL}{page['path']}"

    if not title:
        fail(f"{filename}: missing title")
    elif title in titles:
        fail(f"{filename}: duplicate title: {title}")
    titles.add(title)

    description_value = description.get("content", "").strip() if description else ""
    if not description_value:
        fail(f"{filename}: missing description")
    elif description_value in descriptions:
        fail(f"{filename}: duplicate description")
    descriptions.add(description_value)

    if not canonical or canonical.get("href") != expected_url:
        fail(f"{filename}: canonical must be {expected_url}")
    if not robots or "index" not in robots.get("content", "").lower():
        fail(f"{filename}: missing index robots directive")

    for selector in (
        {"property": "og:title"},
        {"property": "og:description"},
        {"property": "og:image"},
        {"property": "og:url"},
        {"name": "twitter:card"},
        {"name": "twitter:image"},
    ):
        if not soup.find("meta", attrs=selector):
            fail(f"{filename}: missing social tag {selector}")

    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    if not scripts:
        fail(f"{filename}: missing JSON-LD")
    for script in scripts:
        try:
            json.loads(script.string or script.get_text())
        except json.JSONDecodeError as exc:
            fail(f"{filename}: invalid JSON-LD: {exc}")


def validate_sitemap() -> None:
    tree = ET.parse(ROOT / "sitemap.xml")
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locations = [
        item.text.strip()
        for item in tree.findall(".//sm:loc", namespace)
        if item.text
    ]
    expected = [f"{BASE_URL}{page['path']}" for page in PAGES.values()]

    if len(locations) != len(set(locations)):
        fail("sitemap.xml: duplicate URLs")
    if set(locations) != set(expected):
        missing = sorted(set(expected) - set(locations))
        extra = sorted(set(locations) - set(expected))
        fail(f"sitemap.xml: missing={missing}, extra={extra}")
    if any("?" in url or "#" in url for url in locations):
        fail("sitemap.xml: parameter or fragment URLs are not canonical")


def validate_noindex() -> None:
    for filename in ("404.html", "admin.html", "offline.html"):
        soup = BeautifulSoup((ROOT / filename).read_text(encoding="utf-8"), "html.parser")
        robots = soup.find("meta", attrs={"name": "robots"})
        if not robots or "noindex" not in robots.get("content", "").lower():
            fail(f"{filename}: system page must be noindex")


def main() -> None:
    titles: set[str] = set()
    descriptions: set[str] = set()
    for filename, page in PAGES.items():
        validate_page(filename, page, titles, descriptions)
    validate_sitemap()
    validate_noindex()

    if errors:
        print("SEO validation failed:")
        for error in errors:
            print(f" - {error}")
        sys.exit(1)
    print(f"SEO validation passed: {len(PAGES)} public pages")


if __name__ == "__main__":
    main()
