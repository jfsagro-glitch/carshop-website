#!/usr/bin/env python3
"""Generate a sitemap containing only canonical, indexable pages."""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone


BASE_URL = "https://cmsauto.store"

STATIC_PAGES = [
    ("index.html", 1.0, "daily"),
    ("georgia-stock.html", 0.9, "daily"),
    ("europe-orders.html", 0.9, "daily"),
    ("usa-orders.html", 0.8, "daily"),
    ("korea-orders.html", 0.7, "daily"),
    ("china-orders.html", 0.7, "daily"),
    ("parts-orders.html", 0.7, "weekly"),
    ("customs-calculator.html", 0.8, "weekly"),
    ("premium.html", 0.8, "daily"),
    ("avtostok63-europe.html", 0.8, "daily"),
    ("avtostok63-premium.html", 0.7, "daily"),
]


def lastmod_for_file(filepath: str) -> str:
    try:
        mtime = os.path.getmtime(filepath)
        return datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%d")
    except OSError:
        return datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")


def generate_sitemap(base_url: str, repo_root: str, output: str) -> int:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    seen: set[str] = set()

    for page_path, priority, changefreq in STATIC_PAGES:
        full_path = os.path.join(repo_root, page_path)
        if not os.path.exists(full_path):
            print(f"WARNING: missing public page {page_path}", file=sys.stderr)
            continue

        slug = "" if page_path == "index.html" else page_path
        url = f"{base_url.rstrip('/')}/{slug}"
        if url in seen:
            raise ValueError(f"Duplicate canonical URL: {url}")
        seen.add(url)

        lines.extend(
            [
                "  <url>",
                f"    <loc>{url}</loc>",
                f"    <lastmod>{lastmod_for_file(full_path)}</lastmod>",
                f"    <changefreq>{changefreq}</changefreq>",
                f"    <priority>{priority:.1f}</priority>",
                "  </url>",
            ]
        )

    lines.append("</urlset>")
    output_path = os.path.join(repo_root, output)
    with open(output_path, "w", encoding="utf-8", newline="\n") as file:
        file.write("\n".join(lines) + "\n")

    print(f"Generated {output_path}: {len(seen)} canonical URLs")
    return len(seen)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate sitemap.xml")
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--output", default="sitemap.xml")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    if generate_sitemap(args.base_url, args.repo_root, args.output) == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
