#!/usr/bin/env python3
"""
Targeted OEM gap-driven importer.
Reads oem_gap_worklist.csv and searches suggested sources for missing brand x code pairs.
Focuses on priority gaps and can skip already covered pairs.
"""

from __future__ import annotations

import csv
import logging
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from pathlib import Path
from threading import Lock, local
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import quote, urlparse

import requests

REPO_ROOT = Path(__file__).parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from generate_parts_catalog import get_merged_oem_lookup  # noqa: E402
from tools.oem_validation import is_plausible_oem as is_plausible_oem_for_brand  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = REPO_ROOT / "data"

SEARCH_TEMPLATES = {
    "emex.ru": "https://emex.ru/search?q={query}",
    "exist.ru": "https://exist.ru/search.php?search={query}",
    "realoem.com": "https://www.realoem.com/bmw/enUS/select?q={query}",
    "bmwcats.com": "https://bmwcats.com/search/?q={query}",
    "relines.ru": "https://relines.ru/search?q={query}",
    "xn--80aaonli0a.xn--p1ai": "https://xn--80aaonli0a.xn--p1ai/search?q={query}",
    "autoparts24.eu": "https://www.autoparts24.eu/search?q={query}",
    "japan-parts.eu": "https://www.japan-parts.eu/search?q={query}",
    "alvadi.ee": "https://www.alvadi.ee/search/?q={query}",
    "partsale.eu": "https://partsale.eu/search?q={query}",
    "elcats.ru": "https://elcats.ru/search?q={query}",
    "hondaworld.ru": "https://www.hondaworld.ru/search?q={query}",
    "acurapartswarehouse.com": "https://www.acurapartswarehouse.com/search?q={query}",
    "relines.ru": "https://relines.ru/search?q={query}",
    "exist.ru": "https://exist.ru/price/?pcode={query}",
}

SITE_SEARCH_TEMPLATE = "https://duckduckgo.com/html/?q={query}"
SITE_SEARCH_ENABLED_DOMAINS = {
    "fordparts.com",
    "oemfordpart.com",
    "gmpartsdepartment.com",
    "baxterautoparts.com",
    "factorychryslerparts.com",
    "moparpartsoverstock.com",
    "jeepchryslerparts.eu",
    "hemi.by",
    "service.citroen.com",
    "public.servicebox.peugeot.com",
    "fiatdalys.lt",
    "eper.fiatklubpolska.pl",
    "new.lrcat.com",
    "kia.a-inside.ru",
    "hyundai.a-inside.ru",
    "toyotacarmine.ru",
    "epcdata.ru",
    "hondapartsdeals.com",
    "japancats.ru",
    "needet.ru",
    "mitsubishi-autoparts.com.ua",
    "etk.bmwsar.ru",
    "irito-parts.ru",
    "shop.chinacar-club.ru",
    "autodubok.ru",
    "usa-auto.ru",
    "findpart.org",
    "jedip.ru",
    "auto2.ru",
    "parts.com",
    "avtoto.ru",
    "gmpartsgiant.com",
    "xn--80aaonli0a.xn--p1ai",
    "irito-parts.ru",
    "relines.ru",
    "shop.chinacar-club.ru",
    "haval-service.ru",
    "great-wall-parts.ru",
}

TRUSTED_EXTRACT_DOMAINS = {
    "emex.ru",
    "exist.ru",
    "relines.ru",
    "exist.ru",
    "acurapartswarehouse.com",
    "hondaworld.ru",
    "realoem.com",
    "bmwcats.com",
    "elcats.ru",
    "partsale.eu",
    # Multi-brand Japanese/European OEM catalogs
    "japan-parts.eu",
    "autoparts24.eu",
    "alvadi.ee",
    "relines.ru",
}

COMMON_BAD_OEM_PATTERNS = [
    re.compile(r"20\d{2}[-./]\d{1,2}[-./]\d{1,2}"),
    re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}"),
    re.compile(r"\d{1,2}[A-ZÄÖÜ]{3,}\d{4}"),
    re.compile(r"\d{2,4}X\d{2,4}"),
]

BAD_OEM_WORDS = {
    "CONTENT",
    "SCRIPT",
    "STYLE",
    "WINDOW",
    "RETURN",
    "SEARCH",
    "PARTS",
    "QUERY",
    "INDEX",
    "CLASS",
    "VALUE",
    "FALSE",
    "TRUE",
    "NULL",
    "UNDEFINED",
    "COOKIE",
    "DOCTYPE",
    "PRESET",
    "SPACING",
    "DISPLAY",
    "MARGIN",
    "PADDING",
    "BORDER",
    "INLINE",
}

BAD_DATE_WORDS = {
    "JULI",
    "JANUAR",
    "FEBRUAR",
    "MÄRZ",
    "MAERZ",
    "APRIL",
    "JUNI",
    "AUGUST",
    "SEPTEMBER",
    "OKTOBER",
    "NOVEMBER",
    "DEZEMBER",
}

BRAND_QUERY_HINTS = {
    "AC": ["acura"],
    "HO": ["honda"],
    "BM": ["bmw"],
    "MN": ["mini"],
    "AU": ["audi"],
    "VW": ["volkswagen", "vw"],
    "SK": ["skoda"],
    "SE": ["seat"],
    "TY": ["toyota"],
    "LX": ["lexus"],
    "NI": ["nissan"],
    "IN": ["infiniti"],
    "HY": ["hyundai"],
    "KI": ["kia"],
    "GE": ["genesis"],
    "MA": ["mazda"],
    "MI": ["mitsubishi"],
    "SU": ["subaru"],
    "SZ": ["suzuki"],
    "VO": ["volvo"],
    "FO": ["ford"],
    "LR": ["land rover", "landrover"],
    "OP": ["opel", "vauxhall"],
    "CA": ["cadillac"],
    "BU": ["buick"],
    "CH": ["chevrolet"],
    "GM": ["gmc"],
    "JP": ["jeep"],
    "DG": ["dodge"],
    "CR": ["chrysler"],
    "RE": ["renault"],
    "PE": ["peugeot"],
    "CI": ["citroen"],
    "FI": ["fiat"],
    "PO": ["porsche"],
    "TS": ["tesla"],
    "GL": ["geely"],
    "BY": ["byd"],
    "CG": ["changan"],
    "CY": ["chery", "omoda"],
    "HV": ["haval", "great wall"],
}

OEM_FORMAT_PATTERNS = {
    "AC": [
        re.compile(r"\b\d{5}-[A-Z0-9]{3}-[A-Z0-9]{3}\b"),
        re.compile(r"\b\d{5}-[A-Z0-9]{2}[0-9]{2}\b"),
    ],
    "HO": [
        re.compile(r"\b\d{5}-[A-Z0-9]{3}-[A-Z0-9]{3}\b"),
        re.compile(r"\b\d{5}-[A-Z0-9]{2}[0-9]{2}\b"),
    ],
    "BM": [
        re.compile(r"\b\d{2}[\s\-]?\d{2}[\s\-]?\d{1,7}\b"),
    ],
    "MN": [
        # Mini uses BMW-style 11-digit numbers
        re.compile(r"\b\d{11}\b"),
        re.compile(r"\b\d{2}[\s\-]?\d{2}[\s\-]?\d{1,7}\b"),
    ],
    "MB": [
        re.compile(r"\bA\d{10}\b"),
        re.compile(r"\bA\d{3}\s?\d{2}\s?\d{2}\s?\d{2}\b"),
    ],
    "VW": [
        re.compile(r"\b[0-9A-Z]{3}[\s\-]?[0-9A-Z]{3}[\s\-]?[0-9A-Z]{3}[\s\-]?[A-Z0-9]{0,2}\b"),
    ],
    "AU": [
        re.compile(r"\b[0-9A-Z]{3}[\s\-]?[0-9A-Z]{3}[\s\-]?[0-9A-Z]{3}[\s\-]?[A-Z0-9]{0,2}\b"),
    ],
    "SK": [
        re.compile(r"\b[0-9A-Z]{3}[\s\-]?[0-9A-Z]{3}[\s\-]?[0-9A-Z]{3}[\s\-]?[A-Z0-9]{0,2}\b"),
    ],
    "SE": [
        re.compile(r"\b[0-9A-Z]{3}[\s\-]?[0-9A-Z]{3}[\s\-]?[0-9A-Z]{3}[\s\-]?[A-Z0-9]{0,2}\b"),
    ],
    # Toyota / Lexus: 5+5 digits with hyphen, e.g. 90311-35006
    "TY": [
        re.compile(r"\b\d{5}-\d{5}\b"),
        re.compile(r"\b\d{5}-[A-Z0-9]{5}\b"),
        re.compile(r"\b\d{5}-\d{4}[A-Z0-9]\b"),
        re.compile(r"\b[A-Z0-9]{4,6}-\d{5}\b"),
    ],
    "LX": [
        re.compile(r"\b\d{5}-\d{5}\b"),
        re.compile(r"\b\d{5}-[A-Z0-9]{5}\b"),
        re.compile(r"\b\d{5}-\d{4}[A-Z0-9]\b"),
        re.compile(r"\b[A-Z0-9]{4,6}-\d{5}\b"),
    ],
    # Nissan / Infiniti: 5+5 or 5+alpha+digits
    "NI": [
        re.compile(r"\b\d{5}-\d{5}\b"),
        re.compile(r"\b\d{5}-[A-Z0-9]{4,5}\b"),
    ],
    "IN": [
        re.compile(r"\b\d{5}-\d{5}\b"),
        re.compile(r"\b\d{5}-[A-Z0-9]{4,5}\b"),
    ],
    # Hyundai / Kia / Genesis: 5+5 digits with hyphen
    "HY": [
        re.compile(r"\b\d{5}-\d{5}\b"),
        re.compile(r"\b\d{5}-[A-Z0-9]{5}\b"),
        re.compile(r"\b\d{5}-\d{4}[A-Z0-9]\b"),
        re.compile(r"\b[A-Z0-9]{4,6}-\d{5}\b"),
    ],
    "KI": [
        re.compile(r"\b\d{5}-\d{5}\b"),
        re.compile(r"\b\d{5}-[A-Z0-9]{5}\b"),
        re.compile(r"\b\d{5}-\d{4}[A-Z0-9]\b"),
        re.compile(r"\b[A-Z0-9]{4,6}-\d{5}\b"),
    ],
    "GE": [
        re.compile(r"\b\d{5}-\d{5}\b"),
        re.compile(r"\b\d{5}-[A-Z0-9]{5}\b"),
        re.compile(r"\b\d{5}-\d{4}[A-Z0-9]\b"),
        re.compile(r"\b[A-Z0-9]{4,6}-\d{5}\b"),
    ],
    # Mazda: letter-prefix codes like BPYN-XX-XXX, LF01-YY-ZZ0
    "MA": [
        re.compile(r"\b[A-Z0-9]{2,4}-[A-Z0-9]{2,3}-[A-Z0-9]{2,3}\b"),
        re.compile(r"\b[A-Z]\d{3}-[A-Z0-9]{2}-[A-Z0-9]{3}\b"),
    ],
    # Mitsubishi: MN/MD/MR + 6 digits
    "MI": [
        re.compile(r"\bM[NDCROP]\d{6}\b"),
        re.compile(r"\bMD\d{6}\b"),
    ],
    # Subaru: 6 digit + suffix or pure numeric
    "SU": [
        re.compile(r"\b\d{5}-\d{5}\b"),
        re.compile(r"\b\d{8}\b"),
        re.compile(r"\b[A-Z]{2}\d{6}\b"),
    ],
    # Suzuki: similar to Toyota-style
    "SZ": [
        re.compile(r"\b\d{5}-\d{5}\b"),
        re.compile(r"\b\d{8}\b"),
    ],
    # Volvo: 8-digit numeric
    "VO": [
        re.compile(r"\b3\d{7}\b"),
        re.compile(r"\b\d{8}\b"),
    ],
    # Ford: alphanumeric with hyphens
    "FO": [
        re.compile(r"\b[A-Z]\d[A-Z]{2}-[A-Z0-9]{4,5}-[A-Z]{1,2}\b"),
        re.compile(r"\b[A-Z]{2}\d{7}\b"),
        re.compile(r"\bF[A-Z0-9]{8,10}\b"),
    ],
    # Land Rover: LR + 6 digits, or ANR/RTC + digits
    "LR": [
        re.compile(r"\bLR\d{6}\b"),
        re.compile(r"\b[A-Z]{3}\d{4,5}[A-Z]?\b"),
    ],
    # Opel / GM-Europe: 8-13 digits
    "OP": [re.compile(r"\b\d{8,13}\b")],
    "CA": [re.compile(r"\b\d{8,13}\b")],
    "BU": [re.compile(r"\b\d{8,13}\b")],
    "CH": [re.compile(r"\b\d{8,13}\b")],
    "GM": [re.compile(r"\b\d{8,13}\b")],
    # Jeep/Dodge/Chrysler (Stellantis/Mopar): numeric 8-13 with optional letter suffix
    "JP": [
        re.compile(r"\b\d{9,13}\b"),
        re.compile(r"\b\d{8,10}[A-Z]{1,2}\b"),
        re.compile(r"\b[A-Z]{2}\d{8,10}\b"),
    ],
    "DG": [
        re.compile(r"\b\d{9,13}\b"),
        re.compile(r"\b\d{8,10}[A-Z]{1,2}\b"),
    ],
    "CR": [
        re.compile(r"\b\d{9,13}\b"),
        re.compile(r"\b\d{8,10}[A-Z]{1,2}\b"),
    ],
    # Renault: 8XXXX pattern
    "RE": [
        re.compile(r"\b\d{8}\b"),
        re.compile(r"\b[0-9A-Z]{2}\s\d{3}\s\d{3}\b"),
    ],
    # Peugeot: 9-digit or alphanumeric
    "PE": [
        re.compile(r"\b\d{9,10}\b"),
        re.compile(r"\b[0-9A-Z]{4}\s[0-9A-Z]{2}\b"),
    ],
    # Citroen: same as Peugeot (Stellantis)
    "CI": [
        re.compile(r"\b\d{9,10}\b"),
        re.compile(r"\b[0-9A-Z]{4}\s[0-9A-Z]{2}\b"),
    ],
    # Fiat: 8-digit numeric
    "FI": [
        re.compile(r"\b\d{8,10}\b"),
    ],
    # Porsche: NNN.NNN.NNN.NN style
    "PO": [
        re.compile(r"\b\d{3}[\.\s]?\d{3}[\.\s]?\d{3}[\.\s]?\d{0,2}\b"),
        re.compile(r"\b9\d{2}[\s\-\.]\d{3}[\s\-\.]\d{3}[\s\-\.]\d{2}\b"),
    ],
    # Haval / Great Wall: XXXXXXXX-EG01 / XXXXXXXX-ED01 pattern
    "HV": [
        re.compile(r"\b[0-9]{7,10}-E[GD]\d{2}\b"),
        re.compile(r"\b[0-9]{7,10}-[A-Z]{2}\d{2}\b"),
    ],
    # Chery / Omoda: A11-XXXXXXX / T11-XXXXXXX pattern
    "CY": [
        re.compile(r"\b[AT]\d{2}-[0-9]{7,10}\b"),
        re.compile(r"\b[0-9]{3}[HJ]-[0-9]{7,10}\b"),
        re.compile(r"\bSQRE4[A-Z0-9]{2,10}-[0-9]{7,10}\b"),
    ],
    # Geely: 10-digit numeric or JLH-prefix
    "GL": [
        re.compile(r"\b[0-9]{10}\b"),
        re.compile(r"\bJLH-[A-Z0-9]{6,12}\b"),
    ],
    # Changan: F01LXXXXX pattern
    "CG": [
        re.compile(r"\bF01L[0-9]{5,6}\b"),
        re.compile(r"\bJL[0-9][A-Z][0-9]{2,4}[A-Z]{0,4}\b"),
    ],
    # BYD: BYD-prefix or 10-digit numeric or XXXXXXXXXX-XX
    "BY": [
        re.compile(r"\bBYD[0-9]{7,10}\b"),
        re.compile(r"\b[0-9]{10}(-[0-9]{2})?\b"),
    ],
    # Tesla: XXXXXXX-XX-X (7-digit + 2-digit + letter)
    "TS": [
        re.compile(r"\b[0-9]{7}-[0-9]{2}-[A-Z]\b"),
    ],
}


class GapTargetedImporter:
    OEM_TOKEN_RE = re.compile(r"\b[A-Z0-9][A-Z0-9\-]{5,24}\b")
    BAD_OEM_FRAGMENTS = {
        "HTTP",
        "HTTPS",
        "CROPPED",
        "BRAKE",
        "ICON",
        "LOGO",
        "THUMB",
        "AVATAR",
        "PNG",
        "JPG",
        "JPEG",
        "WEBP",
        "SVG",
        "GIF",
    }
    STRICT_DOMAIN_FILTERS = {
        "partsale.eu",
        "duckduckgo.com",
    }

    def __init__(
        self,
        timeout: int = 8,
        max_oem_reuse_per_domain: int = 2,
        lookup_pairs: Optional[Iterable[Tuple[str, str]]] = None,
    ):
        self.timeout = timeout
        self.max_oem_reuse_per_domain = max(1, int(max_oem_reuse_per_domain))
        self._tls = local()
        self._lock = Lock()
        self.results: List[Dict[str, str]] = []
        self.failed_searches: List[Dict[str, str]] = []
        self._lookup_pairs = set(lookup_pairs) if lookup_pairs is not None else set(get_merged_oem_lookup().keys())
        self._domain_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {"attempts": 0, "hits": 0})
        self._domain_oem_pairs: Dict[Tuple[str, str], set[Tuple[str, str]]] = defaultdict(set)

    def _get_session(self) -> requests.Session:
        if not hasattr(self._tls, "session"):
            sess = requests.Session()
            sess.headers.update(
                {
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0 Safari/537.36"
                    )
                }
            )
            self._tls.session = sess
        return self._tls.session

    def _normalize_oem(self, value: str) -> str:
        token = str(value or "").strip().upper()
        token = token.replace("_", "-")
        token = re.sub(r"\s+", "", token)
        token = re.sub(r"[^A-Z0-9\-]", "", token)
        token = re.sub(r"-{2,}", "-", token)
        return token.strip("-")

    def _normalize_domain(self, value: str) -> str:
        text = str(value or "").strip().lower()
        if not text:
            return ""
        if "://" in text:
            parsed = urlparse(text)
            text = parsed.netloc or parsed.path
        text = text.split("/", 1)[0].split("?", 1)[0].strip()
        if text.startswith("www."):
            text = text[4:]
        return text

    def _looks_like_html_or_date_token(self, token: str) -> bool:
        token = self._normalize_oem(token)
        compact = re.sub(r"[^A-Z0-9]", "", token)
        if not token or not compact:
            return True
        if token in BAD_OEM_WORDS:
            return True
        if any(word in token for word in BAD_DATE_WORDS):
            return True
        if any(pattern.fullmatch(token) or pattern.fullmatch(compact) for pattern in COMMON_BAD_OEM_PATTERNS):
            return True
        if token.startswith(("HTTP", "WWW", "IMG", "SRC", "DATA", "WP-", "JS-")):
            return True
        if token.startswith("G-") and len(token) > 8:
            return True
        return False

    def _compact_text(self, value: str) -> str:
        return re.sub(r"[^A-Z0-9А-ЯЁ]", "", str(value or "").upper())

    def _page_has_search_context(
        self,
        text: str,
        query: str,
        part_code: str,
        brand_prefix: str,
        part_name: str,
    ) -> bool:
        page = str(text or "")
        if not page:
            return False

        page_upper = page.upper()
        compact_page = self._compact_text(page)
        compact_part = self._compact_text(part_code)
        compact_query = self._compact_text(query)

        if compact_part and len(compact_part) >= 2 and compact_part in compact_page:
            return True
        if compact_query and len(compact_query) >= 6 and compact_query in compact_page:
            return True

        hints = BRAND_QUERY_HINTS.get(brand_prefix, [])
        brand_hit = any(hint.upper() in page_upper for hint in hints if len(hint) >= 2)
        name_words = [
            w.upper()
            for w in re.findall(r"[A-Za-zА-Яа-яЁё0-9]{4,}", str(part_name or ""))
            if w.upper() not in {"OEM", "ORIGINAL", "PARTS", "ЗАПЧАСТЬ"}
        ]
        part_name_hit = any(word in page_upper for word in name_words[:4])
        return brand_hit and part_name_hit

    def _candidate_tokens(self, html: str) -> Iterable[str]:
        upper = html.upper()
        for token in self.OEM_TOKEN_RE.findall(upper):
            yield token

        # Capture split OEM formats often found in dynamic catalog markup.
        for token in re.findall(r"\b[0-9A-Z]{2,8}[\s\-/][0-9A-Z]{2,8}[\s\-/][0-9A-Z]{2,8}\b", upper):
            yield token

        for token in re.findall(r"\bA\s?\d{3}\s?\d{2}\s?\d{2}\s?\d{2}\b", upper):
            yield token

    def _brand_boost(self, token: str, brand_prefix: str) -> int:
        score = 0
        if any(p.search(token) for p in OEM_FORMAT_PATTERNS.get(brand_prefix, [])):
            score += 4
        if brand_prefix in {"VW", "AU", "SK", "SE"} and len(token) in {9, 10, 11, 12}:
            score += 1
        if brand_prefix in {"AC", "HO"} and token.count("-") >= 2:
            score += 2
        if brand_prefix == "MB" and token.startswith("A"):
            score += 2
        return score

    def _extract_oem_candidates(self, html: str, part_code: str, brand_prefix: str) -> List[str]:
        raw_tokens = [self._normalize_oem(t) for t in self._candidate_tokens(html)]
        tokens = [t for t in raw_tokens if t]
        if not tokens:
            return []

        normalized_part = part_code.strip().upper()
        ranked: List[Tuple[int, str]] = []
        seen = set()
        for token in tokens:
            if token in seen:
                continue
            seen.add(token)

            if self._looks_like_html_or_date_token(token):
                continue
            if "--" in token:
                continue
            if re.fullmatch(r"0X[0-9A-F]+", token):
                continue
            if token == normalized_part:
                continue
            if token.isalpha():
                continue
            if len(token) < 6:
                continue
            if re.fullmatch(r"[A-Z]-[A-Z0-9]{8,}", token):
                continue

            digits = sum(1 for c in token if c.isdigit())
            letters = sum(1 for c in token if c.isalpha())
            if digits < 5:
                continue
            if digits + letters < 6:
                continue
            if "-" not in token and len(token) > 14:
                continue
            if "-" not in token and letters > 6:
                continue

            score = 0
            if "-" in token:
                score += 2
            if letters > 0 and digits > 0:
                score += 3
            if digits >= 5:
                score += 2
            if normalized_part and normalized_part in token:
                score -= 1
            score += self._brand_boost(token, brand_prefix)

            ranked.append((score, token))

        ranked.sort(key=lambda x: x[0], reverse=True)
        shortlisted = [token for score, token in ranked if score >= 4]
        return [token for token in shortlisted if self._is_plausible_oem(token, brand_prefix)][:5]

    def _is_plausible_oem(self, token: str, brand_prefix: str) -> bool:
        token = self._normalize_oem(token)
        if not is_plausible_oem_for_brand(brand_prefix, token, strict_brand=True):
            return False
        if not token or len(token) < 6 or len(token) > 20:
            return False

        if any(part in token for part in self.BAD_OEM_FRAGMENTS):
            return False

        if self._looks_like_html_or_date_token(token):
            return False

        if re.fullmatch(r"[A-Z]{4,}", token):
            return False

        digits = sum(1 for c in token if c.isdigit())
        letters = sum(1 for c in token if c.isalpha())
        hyphens = token.count("-")
        if digits < 3:
            return False

        # Strong brand-specific checks where formats are well-known.
        patterns = OEM_FORMAT_PATTERNS.get(brand_prefix, [])
        if patterns:
            if any(p.search(token) for p in patterns):
                if brand_prefix in {"VW", "AU", "SK", "SE"}:
                    compact = re.sub(r"[^A-Z0-9]", "", token)
                    vag_digits = sum(1 for c in compact if c.isdigit())
                    vag_letters = sum(1 for c in compact if c.isalpha())
                    if vag_digits < 5 or vag_letters > 4:
                        return False
                    if compact and not (compact[0].isdigit() or compact.startswith("N") or compact.startswith("W")):
                        return False
                return True
            if brand_prefix in {"VW", "AU", "SK", "SE"}:
                compact = re.sub(r"[^A-Z0-9]", "", token)
                vag_digits = sum(1 for c in compact if c.isdigit())
                vag_letters = sum(1 for c in compact if c.isalpha())
                if re.fullmatch(r"[0-9A-Z]{9,11}", compact) and vag_digits >= 5 and vag_letters <= 4:
                    if compact and not (compact[0].isdigit() or compact.startswith("N") or compact.startswith("W")):
                        return False
                    return True
            if brand_prefix in {"BM", "MN"}:
                compact = re.sub(r"[^0-9]", "", token)
                if re.fullmatch(r"\d{10,11}", compact):
                    return True
            if brand_prefix in {"AC", "HO"} and hyphens >= 2:
                return True
            return False

        # Conservative generic fallback for brands without strict patterns.
        if hyphens == 0 and letters > 4 and digits < 5:
            return False
        if hyphens == 0 and len(token) > 14:
            return False
        if re.fullmatch(r"[A-Z]{1,2}-[A-Z0-9]{8,}", token):
            return False
        return True

    def _is_domain_allowed_oem(self, domain: str, token: str, brand_prefix: str) -> bool:
        d = self._normalize_domain(domain)
        if d not in self.STRICT_DOMAIN_FILTERS:
            return True

        compact = re.sub(r"[^A-Z0-9]", "", self._normalize_oem(token))
        if not compact:
            return False

        if d == "duckduckgo.com":
            patterns = OEM_FORMAT_PATTERNS.get(brand_prefix, [])
            return any(p.search(token) for p in patterns)

        if d == "partsale.eu" and brand_prefix in {"VW", "AU", "SK", "SE"}:
            digits = sum(1 for c in compact if c.isdigit())
            letters = sum(1 for c in compact if c.isalpha())
            if not re.fullmatch(r"[0-9A-Z]{9,11}", compact):
                return False
            if digits < 5 or letters > 4:
                return False
            if not (compact[0].isdigit() or compact.startswith("N") or compact.startswith("W")):
                return False

        return True

    def parse_suggested_sources(self, sources_str: str) -> List[Tuple[str, str]]:
        if not sources_str:
            return []

        sources = []
        for item in sources_str.split(";"):
            item = item.strip()
            if not item:
                continue
            search_type = ""
            domain = item
            if "(" in item and ")" in item:
                domain = item[: item.index("(")].strip()
                search_type = item[item.index("(") + 1 : item.index(")")].strip()
            domain = self._normalize_domain(domain)
            if domain:
                sources.append((domain, search_type))
        return sources

    def _specialized_queries(
        self,
        domain: str,
        brand: str,
        brand_prefix: str,
        part_code: str,
        part_name: str,
    ) -> List[str]:
        hints = BRAND_QUERY_HINTS.get(brand_prefix, [])

        base = [
            f"{brand} {part_code} {part_name}".strip(),
            f"{brand} {part_code}".strip(),
            f"{part_code} {part_name}".strip(),
            part_code,
        ]

        for hint in hints:
            base.extend(
                [
                    f"{hint} {part_code} {part_name}".strip(),
                    f"{hint} {part_code}".strip(),
                    f"{hint} oem {part_code}".strip(),
                ]
            )

        if domain in {"realoem.com", "bmwcats.com"}:
            base = [f"{part_code} bmw", f"{part_code} mini", f"{part_code} oem"] + base
        elif domain in {"acurapartswarehouse.com", "hondaworld.ru"} and brand_prefix in {"AC", "HO"}:
            base = [f"{part_code} honda", f"{part_code} acura"] + base
        elif domain == "partsale.eu" and brand_prefix in {"VW", "AU", "SK", "SE"}:
            base = [f"{part_code} vag", f"{part_code} audi", f"{part_code} volkswagen"] + base
        elif domain in {"japan-parts.eu", "elcats.ru", "relines.ru"} and brand_prefix in {
            "TY", "LX", "NI", "IN", "HO", "AC", "MA", "MI", "SU", "SZ"
        }:
            brand_hint = BRAND_QUERY_HINTS.get(brand_prefix, [brand.lower()])
            h = brand_hint[0] if brand_hint else brand.lower()
            base = [f"{h} {part_code}", f"{h} oem {part_code}"] + base
        elif domain in {"autoparts24.eu", "alvadi.ee"}:
            brand_hint = BRAND_QUERY_HINTS.get(brand_prefix, [brand.lower()])
            h = brand_hint[0] if brand_hint else brand.lower()
            base = [f"{h} {part_code}", f"{h} {part_code} oem"] + base
        elif domain in {"relines.ru", "xn--80aaonli0a.xn--p1ai", "shop.chinacar-club.ru",
                        "irito-parts.ru", "haval-service.ru", "great-wall-parts.ru"} \
                and brand_prefix in {"GL", "BY", "CG", "CY", "HV"}:
            brand_hint = BRAND_QUERY_HINTS.get(brand_prefix, [brand.lower()])
            h = brand_hint[0] if brand_hint else brand.lower()
            base = [f"{h} {part_code}", f"{h} {part_name} oem", f"{h} запчасти {part_name}"] + base
        elif domain in {"exist.ru", "emex.ru"} and brand_prefix in BRAND_QUERY_HINTS:
            h = BRAND_QUERY_HINTS[brand_prefix][0]
            base = [f"{h} {part_code}", f"{h} {part_name}"] + base
        elif domain in {"avtoto.ru", "gmpartsgiant.com"} and brand_prefix in BRAND_QUERY_HINTS:
            h = BRAND_QUERY_HINTS[brand_prefix][0]
            base = [f"{h} {part_code} original catalog", f"{h} {part_name} OEM"] + base

        out = []
        seen = set()
        for q in base:
            key = q.strip().lower()
            if key and key not in seen:
                seen.add(key)
                out.append(q)
        return out

    def _try_queries(
        self,
        template: str,
        queries: List[str],
        part_code: str,
        brand_prefix: str,
        source_name: str,
        max_retries: int,
        source_domain: str,
        extract_mode: str = "generic",
        part_name: str = "",
    ) -> Optional[Dict[str, str]]:
        def extract_candidates(text: str) -> List[str]:
            if extract_mode == "realoem":
                matches = re.findall(r"\b\d{2}\s?\d{2}\s?\d{6,7}\b", text.upper())
                out = []
                for m in matches:
                    token = self._normalize_oem(m)
                    if len(re.sub(r"[^0-9]", "", token)) >= 10 and self._is_plausible_oem(token, brand_prefix):
                        out.append(token)
                return out[:5]
            if extract_mode == "bmwcats":
                # bmwcats often exposes numeric OEM tokens in href/title attributes.
                tokens = re.findall(r"\b\d{10,11}\b", text.upper())
                out = []
                seen = set()
                for t in tokens:
                    token = self._normalize_oem(t)
                    if token not in seen and self._is_plausible_oem(token, brand_prefix):
                        seen.add(token)
                        out.append(token)
                return out[:5]
            if extract_mode == "hondaworld":
                patterns = [
                    r"\b\d{5}-[A-Z0-9]{3}-[A-Z0-9]{3}\b",
                    r"\b\d{5}-[A-Z0-9]{2}[0-9]{2}\b",
                ]
                out = []
                seen = set()
                up = text.upper()
                for pat in patterns:
                    for m in re.findall(pat, up):
                        token = self._normalize_oem(m)
                        if token and token not in seen and self._is_plausible_oem(token, brand_prefix):
                            seen.add(token)
                            out.append(token)
                return out[:5]
            return self._extract_oem_candidates(text, part_code, brand_prefix)

        for query in queries:
            url = template.format(query=quote(query))
            for attempt in range(max_retries):
                try:
                    r = self._get_session().get(url, timeout=self.timeout)
                    if r.status_code == 200 and len(r.text) > 100:
                        if not self._page_has_search_context(
                            r.text,
                            query=query,
                            part_code=part_code,
                            brand_prefix=brand_prefix,
                            part_name=part_name,
                        ):
                            continue
                        candidates = [
                            c for c in extract_candidates(r.text)
                            if self._is_domain_allowed_oem(source_domain, c, brand_prefix)
                        ]
                        if candidates:
                            return {
                                "oem_number": candidates[0],
                                "source_name": source_name,
                                "source_url": url,
                            }
                except requests.Timeout:
                    if attempt < max_retries - 1:
                        time.sleep(0.7)
                except requests.RequestException:
                    if attempt < max_retries - 1:
                        time.sleep(0.4)
        return None

    def _domain_success_rate(self, domain: str) -> float:
        stats = self._domain_stats.get(domain)
        if not stats:
            return 0.0
        attempts = stats.get("attempts", 0)
        if attempts <= 0:
            return 0.0
        return stats.get("hits", 0) / attempts

    def _adaptive_retries(self, domain: str, base_retries: int) -> int:
        rate = self._domain_success_rate(domain)
        attempts = self._domain_stats.get(domain, {}).get("attempts", 0)
        retries = base_retries
        if attempts >= 15:
            if rate >= 0.20:
                retries += 2
            elif rate >= 0.10:
                retries += 1
            elif rate < 0.03:
                retries -= 1
        return max(1, min(5, retries))

    def _is_noisy_domain(self, domain: str) -> bool:
        stats = self._domain_stats.get(domain, {})
        attempts = stats.get("attempts", 0)
        if attempts < 25:
            return False
        return self._domain_success_rate(domain) < 0.01

    def _accept_result_for_pair(self, domain: str, oem_number: str, pair: Tuple[str, str]) -> bool:
        token = self._normalize_oem(oem_number)
        if not token:
            return False
        key = (domain, token)
        used_pairs = self._domain_oem_pairs[key]
        if pair not in used_pairs and len(used_pairs) >= self.max_oem_reuse_per_domain:
            return False
        used_pairs.add(pair)
        return True

    def search_domain_emex(
        self,
        domain: str,
        brand: str,
        brand_prefix: str,
        part_code: str,
        part_name: str,
        max_retries: int = 3,
    ) -> Optional[Dict[str, str]]:
        queries = self._specialized_queries(domain, brand, brand_prefix, part_code, part_name)
        return self._try_queries(
            "https://emex.ru/search?q={query}",
            queries,
            part_code,
            brand_prefix,
            domain,
            max_retries,
            source_domain=domain,
            part_name=part_name,
        )

    def search_domain_specialized(
        self,
        domain: str,
        brand: str,
        brand_prefix: str,
        part_code: str,
        part_name: str,
        max_retries: int = 3,
    ) -> Optional[Dict[str, str]]:
        template = SEARCH_TEMPLATES.get(domain)
        if not template or "{query}" not in template:
            return None
        queries = self._specialized_queries(domain, brand, brand_prefix, part_code, part_name)
        mode = "generic"
        if domain == "realoem.com":
            mode = "realoem"
        elif domain == "bmwcats.com":
            mode = "bmwcats"
        elif domain == "hondaworld.ru":
            mode = "hondaworld"
        return self._try_queries(
            template,
            queries,
            part_code,
            brand_prefix,
            domain,
            max_retries,
            source_domain=domain,
            extract_mode=mode,
            part_name=part_name,
        )

    def search_domain_generic(
        self,
        domain: str,
        brand: str,
        brand_prefix: str,
        part_code: str,
        part_name: str,
        max_retries: int = 3,
    ) -> Optional[Dict[str, str]]:
        queries = self._specialized_queries(domain, brand, brand_prefix, part_code, part_name)

        if domain in SEARCH_TEMPLATES:
            if domain not in TRUSTED_EXTRACT_DOMAINS:
                return None
            template = SEARCH_TEMPLATES[domain]
            if "{query}" not in template:
                return None
            return self._try_queries(
                template,
                queries,
                part_code,
                brand_prefix,
                domain,
                max_retries,
                source_domain=domain,
                part_name=part_name,
            )

        # Low-overlap domain fallback: site-restricted search over DDG HTML endpoint.
        if domain in SITE_SEARCH_ENABLED_DOMAINS:
            site_queries = [f"site:{domain} {q}" for q in queries]
            return self._try_queries(
                SITE_SEARCH_TEMPLATE,
                site_queries,
                part_code,
                brand_prefix,
                f"{domain}:site_search",
                max_retries,
                source_domain="duckduckgo.com",
                part_name=part_name,
            )
        return None

    def search_gap(
        self,
        brand: str,
        brand_prefix: str,
        part_code: str,
        part_name: str,
        sources: List[Tuple[str, str]],
        priority: str,
        adaptive_retry: bool = True,
    ) -> Optional[Dict[str, str]]:
        ordered_sources = sorted(
            sources,
            key=lambda s: self._domain_success_rate(s[0]),
            reverse=True,
        )

        for domain, _search_type in ordered_sources:
            if not domain.strip():
                continue
            if adaptive_retry and self._is_noisy_domain(domain):
                continue

            logger.info(
                f"Searching {domain} for {brand_prefix}x{part_code} "
                f"({part_name}) [priority={priority}]"
            )

            self._domain_stats[domain]["attempts"] += 1
            retries = self._adaptive_retries(domain, base_retries=3) if adaptive_retry else 3

            if domain == "emex.ru":
                result = self.search_domain_emex(domain, brand, brand_prefix, part_code, part_name, max_retries=retries)
            elif domain in {"realoem.com", "bmwcats.com", "acurapartswarehouse.com", "hondaworld.ru",
                            "partsale.eu", "elcats.ru", "relines.ru", "exist.ru"}:
                result = self.search_domain_specialized(
                    domain,
                    brand,
                    brand_prefix,
                    part_code,
                    part_name,
                    max_retries=retries,
                )
            else:
                result = self.search_domain_generic(
                    domain,
                    brand,
                    brand_prefix,
                    part_code,
                    part_name,
                    max_retries=retries,
                )

            if result:
                pair = (brand_prefix, part_code)
                if not self._accept_result_for_pair(domain, result.get("oem_number", ""), pair):
                    continue
                self._domain_stats[domain]["hits"] += 1
                result.update(
                    {
                        "brand": brand,
                        "brand_prefix": brand_prefix,
                        "part_code": part_code,
                        "part_name": part_name,
                        "priority": priority,
                        "retrieved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    }
                )
                return result

            time.sleep(0.2)

        with self._lock:
            self.failed_searches.append(
                {
                    "brand": brand,
                    "brand_prefix": brand_prefix,
                    "part_code": part_code,
                    "priority": priority,
                }
            )
        return None

    def import_from_gaps(
        self,
        worklist_path: Path,
        max_gaps: Optional[int] = None,
        priority_filter: str = "all",
        priorities: Optional[List[str]] = None,
        workers: int = 8,
        only_uncovered: bool = True,
        top_gaps: Optional[int] = None,
        adaptive_retry: bool = True,
        checkpoint_output: Optional[Path] = None,
        checkpoint_failed_output: Optional[Path] = None,
        checkpoint_every: int = 25,
    ) -> int:
        logger.info(f"Reading gap worklist from {worklist_path}")

        gaps_by_priority: Dict[str, List[Dict[str, str]]] = {"high": [], "medium": [], "low": []}
        seen_pairs = set()

        with worklist_path.open("r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                priority = str(row.get("priority", "low")).lower()
                if priority not in gaps_by_priority:
                    priority = "low"

                pair = (
                    str(row.get("brand_prefix") or "").strip().upper(),
                    str(row.get("part_code") or "").strip().upper(),
                )
                if not all(pair):
                    continue
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)

                if only_uncovered and pair in self._lookup_pairs:
                    continue

                gaps_by_priority[priority].append(row)

        all_gaps: List[Dict[str, str]] = []
        selected_priorities = priorities or ([] if priority_filter == "all" else [priority_filter])
        if not selected_priorities:
            selected_priorities = ["high", "medium", "low"]

        if len(selected_priorities) == 1 and selected_priorities[0] in {"high", "medium", "low"}:
            all_gaps.extend(gaps_by_priority[priority_filter])
        else:
            for p in ["high", "medium", "low"]:
                if p in selected_priorities:
                    all_gaps.extend(gaps_by_priority[p])

        if max_gaps:
            all_gaps = all_gaps[:max_gaps]
        if top_gaps and top_gaps > 0:
            all_gaps = all_gaps[:top_gaps]

        logger.info(
            f"Processing {len(all_gaps)} gaps "
            f"(high={len(gaps_by_priority['high'])} medium={len(gaps_by_priority['medium'])} low={len(gaps_by_priority['low'])})"
        )

        processed = 0
        found = 0
        checkpoint_every = max(0, int(checkpoint_every or 0))

        def write_checkpoint() -> None:
            if checkpoint_output and self.results:
                self.export_results(checkpoint_output)
            if checkpoint_failed_output and self.failed_searches:
                self.export_failed_searches(checkpoint_failed_output)

        def process_gap(gap: Dict[str, str]) -> Optional[Dict[str, str]]:
            sources_str = str(gap.get("suggested_sources") or "")
            sources = self.parse_suggested_sources(sources_str)
            if not sources:
                return None

            return self.search_gap(
                brand=str(gap.get("brand") or ""),
                brand_prefix=str(gap.get("brand_prefix") or "").upper(),
                part_code=str(gap.get("part_code") or "").upper(),
                part_name=str(gap.get("part_name") or ""),
                sources=sources,
                priority=str(gap.get("priority") or "low"),
                adaptive_retry=adaptive_retry,
            )

        with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
            futures = [executor.submit(process_gap, gap) for gap in all_gaps]
            for future in as_completed(futures):
                result = future.result()
                processed += 1
                if result and result.get("oem_number"):
                    with self._lock:
                        self.results.append(result)
                        self._lookup_pairs.add((result.get("brand_prefix", ""), result.get("part_code", "")))
                    found += 1

                if processed % 50 == 0:
                    logger.info(f"Progress: {processed}/{len(all_gaps)} gaps processed, {found} OEM found")
                if checkpoint_every and processed % checkpoint_every == 0:
                    write_checkpoint()

        write_checkpoint()
        logger.info(f"Completed: {processed} gaps searched, {found} OEM found")
        return found

    def export_results(self, output_path: Path) -> None:
        if not self.results:
            logger.warning("No results to export")
            return

        fieldnames = [
            "brand",
            "brand_prefix",
            "part_code",
            "part_name",
            "priority",
            "oem_number",
            "source_name",
            "source_url",
            "retrieved_at",
        ]

        with output_path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for result in self.results:
                row = {k: result.get(k, "") for k in fieldnames}
                writer.writerow(row)

        logger.info(f"Exported {len(self.results)} results to {output_path}")

    def export_failed_searches(self, output_path: Path) -> None:
        if not self.failed_searches:
            return

        with output_path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["brand", "brand_prefix", "part_code", "priority"])
            writer.writeheader()
            writer.writerows(self.failed_searches)

        logger.info(f"Exported {len(self.failed_searches)} failed searches to {output_path}")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Import OEM from gap worklist")
    parser.add_argument(
        "--gap-worklist",
        type=Path,
        default=DATA_DIR / "oem_gap_worklist.csv",
        help="Path to gap worklist CSV",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DATA_DIR / "oem_supplier_targeted_gaps.csv",
        help="Output CSV path",
    )
    parser.add_argument(
        "--failed-output",
        type=Path,
        default=DATA_DIR / "oem_gap_failed_searches.csv",
        help="Failed searches output CSV",
    )
    parser.add_argument("--max-gaps", type=int, default=None, help="Maximum number of gaps to process")
    parser.add_argument(
        "--priority",
        choices=["all", "high", "medium", "low"],
        default="all",
        help="Priority level to process",
    )
    parser.add_argument(
        "--priorities",
        default="",
        help="Comma-separated priorities, e.g. high,medium",
    )
    parser.add_argument("--workers", type=int, default=8, help="Parallel worker threads")
    parser.add_argument("--timeout", type=int, default=8, help="HTTP timeout per request in seconds")
    parser.add_argument("--top-gaps", type=int, default=None, help="Process only first N unresolved gaps")
    parser.add_argument(
        "--max-oem-reuse-per-domain",
        type=int,
        default=2,
        help="Reject OEM token reuse across too many brand_prefix x part_code pairs within one domain",
    )
    parser.add_argument(
        "--no-adaptive-retry",
        action="store_true",
        help="Disable adaptive retry and noisy-domain suppression",
    )
    parser.add_argument(
        "--include-covered",
        action="store_true",
        help="Include pairs already covered in merged lookup",
    )
    parser.add_argument(
        "--checkpoint-output",
        type=Path,
        default=None,
        help="Write partial confirmed OEM results while the parser is still running",
    )
    parser.add_argument(
        "--checkpoint-failed-output",
        type=Path,
        default=None,
        help="Write partial failed searches while the parser is still running",
    )
    parser.add_argument(
        "--checkpoint-every",
        type=int,
        default=25,
        help="Checkpoint every N processed gaps; 0 disables checkpointing",
    )
    args = parser.parse_args()

    importer = GapTargetedImporter(
        timeout=args.timeout,
        max_oem_reuse_per_domain=args.max_oem_reuse_per_domain,
    )
    selected_priorities = [p.strip().lower() for p in str(args.priorities or "").split(",") if p.strip()]
    selected_priorities = [p for p in selected_priorities if p in {"high", "medium", "low"}]
    found = importer.import_from_gaps(
        args.gap_worklist,
        max_gaps=args.max_gaps,
        priority_filter=args.priority,
        priorities=selected_priorities,
        workers=args.workers,
        only_uncovered=not args.include_covered,
        top_gaps=args.top_gaps,
        adaptive_retry=not args.no_adaptive_retry,
        checkpoint_output=args.checkpoint_output,
        checkpoint_failed_output=args.checkpoint_failed_output,
        checkpoint_every=args.checkpoint_every,
    )

    if found > 0:
        importer.export_results(args.output)

    if importer.failed_searches:
        importer.export_failed_searches(args.failed_output)

    logger.info(f"Summary: Found {found} OEM from {len(importer.failed_searches)} failed searches")


if __name__ == "__main__":
    main()
