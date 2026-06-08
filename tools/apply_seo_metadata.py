#!/usr/bin/env python3
"""Apply consistent SEO and entity metadata to public HTML pages."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://cmsauto.store"
EXPO_IMAGE = f"{BASE_URL}/images/logo.png"
AVTOSTOK_IMAGE = f"{BASE_URL}/images/avtostok63/avtostok63-og.png?v=20260608"

PAGES = {
    "index.html": {
        "path": "/",
        "title": "EXPO MIR — автомобили из Грузии, Европы и США под ключ",
        "description": "Актуальные автомобили из Грузии, Европы и США с фото и расчётом стоимости под ключ в РФ. Подбор, проверка, доставка и таможенное оформление.",
        "name": "Автомобили из Грузии, Европы и США под ключ",
        "kind": "WebPage",
        "service": "Подбор и доставка автомобилей под ключ",
    },
    "georgia-stock.html": {
        "path": "/georgia-stock.html",
        "title": "Автомобили из Грузии в наличии и под заказ — EXPO MIR",
        "description": "Актуальный каталог автомобилей из Грузии с фото, пробегом, характеристиками и расчётом цены под ключ в РФ. Проверка и доставка без предоплаты.",
        "name": "Автомобили из Грузии",
        "kind": "CollectionPage",
        "service": "Подбор и доставка автомобилей из Грузии",
    },
    "europe-orders.html": {
        "path": "/europe-orders.html",
        "title": "Автомобили из Европы под ключ в РФ — каталог EXPO MIR",
        "description": "Каталог автомобилей из Германии и Европы: реальные фото, пробег, объём двигателя и цена под ключ в рублях. Подбор, проверка истории и доставка.",
        "name": "Автомобили из Европы",
        "kind": "CollectionPage",
        "service": "Подбор и доставка автомобилей из Европы",
    },
    "usa-orders.html": {
        "path": "/usa-orders.html",
        "title": "Автомобили из США с аукционов под ключ — EXPO MIR",
        "description": "Подбор автомобилей из США на Copart и IAAI, проверка VIN и истории, расчёт доставки и таможенных платежей. Заказ автомобиля под ключ.",
        "name": "Автомобили из США",
        "kind": "CollectionPage",
        "service": "Подбор и доставка автомобилей из США",
    },
    "korea-orders.html": {
        "path": "/korea-orders.html",
        "title": "Автомобили из Кореи под заказ — каталог EXPO MIR",
        "description": "Автомобили Hyundai, Kia, Genesis и других марок из Кореи: фото, характеристики, проверка истории и расчёт доставки под ключ.",
        "name": "Автомобили из Кореи",
        "kind": "CollectionPage",
        "service": "Подбор и доставка автомобилей из Кореи",
    },
    "china-orders.html": {
        "path": "/china-orders.html",
        "title": "Автомобили из Китая под заказ и под ключ — EXPO MIR",
        "description": "Подбор новых и подержанных автомобилей из Китая. Проверка комплектации, расчёт доставки, таможенных платежей и итоговой цены под ключ.",
        "name": "Автомобили из Китая",
        "kind": "CollectionPage",
        "service": "Подбор и доставка автомобилей из Китая",
    },
    "parts-orders.html": {
        "path": "/parts-orders.html",
        "title": "OEM номера и оригинальные автозапчасти — EXPO MIR",
        "description": "Каталог оригинальных автозапчастей по марке, модели и группе. Поиск конкретного OEM номера детали и заявка на подбор запчасти.",
        "name": "OEM номера и автозапчасти",
        "kind": "CollectionPage",
        "service": "Подбор оригинальных автозапчастей и OEM номеров",
    },
    "customs-calculator.html": {
        "path": "/customs-calculator.html",
        "title": "Таможенный калькулятор автомобиля РФ и ЕАЭС 2026 — EXPO MIR",
        "description": "Онлайн-расчёт таможенной пошлины, сбора, акциза, НДС и утильсбора автомобиля для ввоза в РФ и ЕАЭС в 2026 году.",
        "name": "Таможенный калькулятор автомобиля",
        "kind": "WebApplication",
        "service": "Расчёт таможенных платежей автомобиля",
    },
    "avtostok63-europe.html": {
        "path": "/avtostok63-europe.html",
        "title": "Avtostok63 — автомобили из Европы с доставкой в Самару",
        "description": "Актуальные автомобили из Европы от Avtostok63: реальные фото, характеристики, цена под ключ и доставка в Самару.",
        "name": "Автомобили из Европы Avtostok63",
        "kind": "CollectionPage",
        "service": "Подбор и доставка автомобилей из Европы в Самару",
        "brand": "avtostok",
    },
    "avtostok63-premium.html": {
        "path": "/avtostok63-premium.html",
        "title": "Avtostok63 Premium — новые премиальные автомобили",
        "description": "Новые премиальные автомобили Avtostok63 со всего мира: актуальное наличие, реальные фото, цены и заявка на доставку под ключ.",
        "name": "Avtostok63 Premium",
        "kind": "CollectionPage",
        "service": "Подбор премиальных автомобилей со всего мира",
        "brand": "avtostok",
    },
}

MANAGED_TAGS = re.compile(
    r"\s*<(?:meta|link)\b[^>]*\bdata-seo-managed=[\"']true[\"'][^>]*>\s*"
    r"|\s*<script\b[^>]*\bdata-seo-managed=[\"']true[\"'][^>]*>.*?</script>\s*",
    re.IGNORECASE | re.DOTALL,
)

LEGACY_TAGS = [
    r"<title>.*?</title>",
    r"<meta\s+name=[\"']description[\"'][^>]*>",
    r"<meta\s+name=[\"']keywords[\"'][^>]*>",
    r"<meta\s+name=[\"']robots[\"'][^>]*>",
    r"<meta\s+name=[\"']author[\"'][^>]*>",
    r"<meta\s+name=[\"']twitter:(?:card|title|description|image)[\"'][^>]*>",
    r"<meta\s+property=[\"']og:[^\"']+[\"'][^>]*>",
    r"<link\s+rel=[\"']canonical[\"'][^>]*>",
    r"<script\s+type=[\"']application/ld\+json[\"'][^>]*>.*?</script>",
]


def expo_organization() -> dict:
    return {
        "@type": "Organization",
        "@id": f"{BASE_URL}/#organization",
        "name": "EXPO MIR",
        "url": f"{BASE_URL}/",
        "logo": {"@type": "ImageObject", "url": EXPO_IMAGE},
        "image": EXPO_IMAGE,
        "email": "carexportgeo@bk.ru",
        "telephone": ["+37368925626", "+79184140636"],
        "sameAs": ["https://t.me/expo_mir"],
        "contactPoint": [
            {
                "@type": "ContactPoint",
                "telephone": "+37368925626",
                "contactType": "sales",
                "availableLanguage": ["ru"],
            },
            {
                "@type": "ContactPoint",
                "telephone": "+79184140636",
                "contactType": "sales",
                "availableLanguage": ["ru"],
            },
        ],
    }


def avtostok_organization() -> dict:
    return {
        "@type": "Organization",
        "@id": f"{BASE_URL}/avtostok63-europe.html#organization",
        "name": "Avtostok63",
        "url": f"{BASE_URL}/avtostok63-europe.html",
        "logo": {"@type": "ImageObject", "url": AVTOSTOK_IMAGE},
        "image": AVTOSTOK_IMAGE,
        "telephone": "+79178177711",
        "sameAs": ["https://t.me/Avtostok163"],
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": "+79178177711",
            "contactType": "sales",
            "availableLanguage": ["ru"],
        },
    }


def schema_for(page: dict) -> dict:
    url = f"{BASE_URL}{page['path']}"
    avtostok = page.get("brand") == "avtostok"
    org = avtostok_organization() if avtostok else expo_organization()
    org_id = org["@id"]
    site_id = (
        f"{BASE_URL}/avtostok63-europe.html#website"
        if avtostok
        else f"{BASE_URL}/#website"
    )
    image = AVTOSTOK_IMAGE if avtostok else EXPO_IMAGE

    graph = [
        org,
        {
            "@type": "WebSite",
            "@id": site_id,
            "url": org["url"],
            "name": org["name"],
            "inLanguage": "ru-RU",
            "publisher": {"@id": org_id},
        },
        {
            "@type": page["kind"],
            "@id": f"{url}#webpage",
            "url": url,
            "name": page["name"],
            "description": page["description"],
            "inLanguage": "ru-RU",
            "isPartOf": {"@id": site_id},
            "about": {"@id": org_id},
            "primaryImageOfPage": {"@type": "ImageObject", "url": image},
            "breadcrumb": {"@id": f"{url}#breadcrumb"},
        },
        {
            "@type": "BreadcrumbList",
            "@id": f"{url}#breadcrumb",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": org["name"],
                    "item": org["url"],
                },
                *(
                    []
                    if page["path"] == "/"
                    else [
                        {
                            "@type": "ListItem",
                            "position": 2,
                            "name": page["name"],
                            "item": url,
                        }
                    ]
                ),
            ],
        },
        {
            "@type": "Service",
            "@id": f"{url}#service",
            "name": page["service"],
            "description": page["description"],
            "url": url,
            "provider": {"@id": org_id},
            "areaServed": {"@type": "Country", "name": "Россия"},
        },
    ]

    if page["path"] == "/":
        graph.append(
            {
                "@type": "OfferCatalog",
                "@id": f"{BASE_URL}/#catalog",
                "name": "Каталоги автомобилей EXPO MIR",
                "itemListElement": [
                    {
                        "@type": "Offer",
                        "itemOffered": {
                            "@type": "Service",
                            "name": label,
                            "url": f"{BASE_URL}/{path}",
                        },
                    }
                    for path, label in (
                        ("georgia-stock.html", "Автомобили из Грузии"),
                        ("europe-orders.html", "Автомобили из Европы"),
                        ("usa-orders.html", "Автомобили из США"),
                        ("customs-calculator.html", "Таможенный калькулятор"),
                    )
                ],
            }
        )
        graph.append(
            {
                "@type": "FAQPage",
                "@id": f"{BASE_URL}/#faq",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": "Что входит в стоимость автомобиля под ключ?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Расчёт включает цену автомобиля, доставку, таможенные платежи и обязательные расходы, указанные для конкретного предложения.",
                        },
                    },
                    {
                        "@type": "Question",
                        "name": "Из каких стран можно заказать автомобиль?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "EXPO MIR подбирает автомобили из Грузии, стран Европы, США, Кореи и Китая.",
                        },
                    },
                    {
                        "@type": "Question",
                        "name": "Можно ли проверить автомобиль до покупки?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Да. Для доступных предложений проверяются VIN, история, характеристики, фотографии и сведения продавца.",
                        },
                    },
                    {
                        "@type": "Question",
                        "name": "Как получить точный расчёт?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Выберите автомобиль в каталоге или отправьте заявку с желаемой маркой, моделью и бюджетом.",
                        },
                    },
                ],
            }
        )

    return {"@context": "https://schema.org", "@graph": graph}


def metadata_block(page: dict) -> str:
    url = f"{BASE_URL}{page['path']}"
    image = AVTOSTOK_IMAGE if page.get("brand") == "avtostok" else EXPO_IMAGE
    site_name = "Avtostok63" if page.get("brand") == "avtostok" else "EXPO MIR"
    schema = json.dumps(schema_for(page), ensure_ascii=False, indent=2)
    return f"""    <title data-seo-managed="true">{page['title']}</title>
    <meta data-seo-managed="true" name="description" content="{page['description']}">
    <meta data-seo-managed="true" name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
    <meta data-seo-managed="true" name="author" content="{site_name}">
    <link data-seo-managed="true" rel="canonical" href="{url}">
    <meta data-seo-managed="true" property="og:type" content="website">
    <meta data-seo-managed="true" property="og:locale" content="ru_RU">
    <meta data-seo-managed="true" property="og:site_name" content="{site_name}">
    <meta data-seo-managed="true" property="og:title" content="{page['title']}">
    <meta data-seo-managed="true" property="og:description" content="{page['description']}">
    <meta data-seo-managed="true" property="og:url" content="{url}">
    <meta data-seo-managed="true" property="og:image" content="{image}">
    <meta data-seo-managed="true" property="og:image:alt" content="{site_name}: {page['name']}">
    <meta data-seo-managed="true" name="twitter:card" content="summary_large_image">
    <meta data-seo-managed="true" name="twitter:title" content="{page['title']}">
    <meta data-seo-managed="true" name="twitter:description" content="{page['description']}">
    <meta data-seo-managed="true" name="twitter:image" content="{image}">
    <script data-seo-managed="true" type="application/ld+json">
{schema}
    </script>
"""


def apply_to_file(filename: str, page: dict) -> None:
    path = ROOT / filename
    html = path.read_text(encoding="utf-8")
    html = MANAGED_TAGS.sub("\n", html)
    for pattern in LEGACY_TAGS:
        html = re.sub(pattern, "", html, flags=re.IGNORECASE | re.DOTALL)

    viewport = re.search(r"<meta\s+name=[\"']viewport[\"'][^>]*>", html, re.IGNORECASE)
    if not viewport:
        raise RuntimeError(f"{filename}: viewport meta tag not found")
    insert_at = viewport.end()
    html = html[:insert_at] + "\n" + metadata_block(page) + html[insert_at:]
    html = re.sub(r"\n[ \t]*\n[ \t]*\n", "\n\n", html)
    html = "\n".join(line.rstrip() for line in html.splitlines()) + "\n"
    path.write_text(html, encoding="utf-8", newline="\n")
    print(f"Updated {filename}")


def main() -> None:
    for filename, page in PAGES.items():
        apply_to_file(filename, page)


if __name__ == "__main__":
    main()
