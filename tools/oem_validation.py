"""Shared OEM number validation used by importers and catalog generation."""
from __future__ import annotations

import re


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

COMMON_BAD_PATTERNS = [
    re.compile(r"20\d{2}[-./]\d{1,2}[-./]\d{1,2}"),
    re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}"),
    re.compile(r"\d{1,2}[A-ZÄÖÜ]{3,}\d{4}"),
    re.compile(r"\d{2,4}X\d{2,4}"),
    re.compile(r"0X[0-9A-F]+"),
]

OEM_FORMAT_PATTERNS = {
    "AC": [re.compile(r"\b\d{5}-[A-Z0-9]{3}-[A-Z0-9]{3}\b"), re.compile(r"\b\d{5}-[A-Z0-9]{2}[0-9]{2}\b")],
    "HO": [re.compile(r"\b\d{5}-[A-Z0-9]{3}-[A-Z0-9]{3}\b"), re.compile(r"\b\d{5}-[A-Z0-9]{2}[0-9]{2}\b")],
    "BM": [re.compile(r"\b\d{11}\b"), re.compile(r"\b\d{2}[\s\-]?\d{2}[\s\-]?\d{6,7}\b")],
    "MN": [re.compile(r"\b\d{11}\b"), re.compile(r"\b\d{2}[\s\-]?\d{2}[\s\-]?\d{6,7}\b")],
    "MB": [re.compile(r"\bA\d{10}\b"), re.compile(r"\bA\d{3}\s?\d{2}\s?\d{2}\s?\d{2}\b")],
    "VW": [re.compile(r"\b[0-9A-Z]{3}[\s\-]?[0-9A-Z]{3}[\s\-]?[0-9A-Z]{3}[\s\-]?[A-Z0-9]{0,2}\b")],
    "AU": [re.compile(r"\b[0-9A-Z]{3}[\s\-]?[0-9A-Z]{3}[\s\-]?[0-9A-Z]{3}[\s\-]?[A-Z0-9]{0,2}\b")],
    "SK": [re.compile(r"\b[0-9A-Z]{3}[\s\-]?[0-9A-Z]{3}[\s\-]?[0-9A-Z]{3}[\s\-]?[A-Z0-9]{0,2}\b")],
    "SE": [re.compile(r"\b[0-9A-Z]{3}[\s\-]?[0-9A-Z]{3}[\s\-]?[0-9A-Z]{3}[\s\-]?[A-Z0-9]{0,2}\b")],
    "TY": [re.compile(r"\b\d{5}-[A-Z0-9]{5}\b"), re.compile(r"\b[A-Z0-9]{4,6}-\d{5}\b")],
    "LX": [re.compile(r"\b\d{5}-[A-Z0-9]{5}\b"), re.compile(r"\b[A-Z0-9]{4,6}-\d{5}\b")],
    "NI": [re.compile(r"\b\d{5}-[A-Z0-9]{4,5}\b")],
    "IN": [re.compile(r"\b\d{5}-[A-Z0-9]{4,5}\b")],
    "HY": [re.compile(r"\b\d{5}-[A-Z0-9]{5}\b"), re.compile(r"\b[A-Z0-9]{4,6}-\d{5}\b")],
    "KI": [re.compile(r"\b\d{5}-[A-Z0-9]{5}\b"), re.compile(r"\b[A-Z0-9]{4,6}-\d{5}\b")],
    "GE": [re.compile(r"\b\d{5}-[A-Z0-9]{5}\b"), re.compile(r"\b[A-Z0-9]{4,6}-\d{5}\b")],
    "MA": [re.compile(r"\b[A-Z0-9]{2,4}-[A-Z0-9]{2,3}-[A-Z0-9]{2,3}\b"), re.compile(r"\b[A-Z]\d{3}-[A-Z0-9]{2}-[A-Z0-9]{3}\b")],
    "MI": [re.compile(r"\bM[NDCROP]\d{6}\b"), re.compile(r"\bMD\d{6}\b"), re.compile(r"\bMR\d{6}\b")],
    "SU": [re.compile(r"\b\d{5}-[A-Z0-9]{5}\b"), re.compile(r"\b\d{8}\b"), re.compile(r"\b[A-Z]{2}\d{6}\b")],
    "SZ": [re.compile(r"\b\d{5}-[A-Z0-9]{5}\b"), re.compile(r"\b\d{8}\b")],
    "VO": [re.compile(r"\b3\d{7}\b"), re.compile(r"\b\d{8}\b")],
    "FO": [re.compile(r"\b[A-Z]\d[A-Z]{2}-[A-Z0-9]{4,5}-[A-Z]{1,2}\b"), re.compile(r"\b[A-Z]{2}\d{7}\b"), re.compile(r"\bF[A-Z0-9]{8,10}\b")],
    "LR": [re.compile(r"\bLR\d{6}\b"), re.compile(r"\b[A-Z]{3}\d{4,5}[A-Z]?\b")],
    "OP": [re.compile(r"\b\d{8,13}\b")],
    "CA": [re.compile(r"\b\d{8,13}\b")],
    "BU": [re.compile(r"\b\d{8,13}\b")],
    "CH": [re.compile(r"\b\d{8,13}\b")],
    "GM": [re.compile(r"\b\d{8,13}\b")],
    "JP": [re.compile(r"\b\d{9,13}\b"), re.compile(r"\b\d{8,10}[A-Z]{1,2}\b"), re.compile(r"\b[A-Z]{2}\d{8,10}\b")],
    "DG": [re.compile(r"\b\d{9,13}\b"), re.compile(r"\b\d{8,10}[A-Z]{1,2}\b")],
    "CR": [re.compile(r"\b\d{9,13}\b"), re.compile(r"\b\d{8,10}[A-Z]{1,2}\b")],
    "RE": [re.compile(r"\b\d{8}\b"), re.compile(r"\b[0-9A-Z]{2}\s\d{3}\s\d{3}\b")],
    "PE": [re.compile(r"\b\d{9,10}\b"), re.compile(r"\b[0-9A-Z]{4}\s[0-9A-Z]{2}\b")],
    "CI": [re.compile(r"\b\d{9,10}\b"), re.compile(r"\b[0-9A-Z]{4}\s[0-9A-Z]{2}\b")],
    "FI": [re.compile(r"\b\d{8,10}\b")],
    "PO": [re.compile(r"\b\d{3}[\.\s]?\d{3}[\.\s]?\d{3}[\.\s]?\d{0,2}\b"), re.compile(r"\b9\d{2}[\s\-\.]\d{3}[\s\-\.]\d{3}[\s\-\.]\d{2}\b")],
    "TS": [re.compile(r"\b[0-9]{7}-[0-9]{2}-[A-Z]\b")],
    "HV": [re.compile(r"\b[0-9]{7,10}-E[GD]\d{2}\b"), re.compile(r"\b[0-9]{7,10}-[A-Z]{2}\d{2}\b")],
    "CY": [re.compile(r"\b[AT]\d{2}-[0-9]{7,10}\b"), re.compile(r"\b[0-9]{3}[HJ]-[0-9]{7,10}\b"), re.compile(r"\bSQRE4[A-Z0-9]{2,10}-[0-9]{7,10}\b")],
    "GL": [re.compile(r"\b[0-9]{10}\b"), re.compile(r"\bJLH-[A-Z0-9]{6,12}\b")],
    "CG": [re.compile(r"\bF01L[0-9]{5,6}\b"), re.compile(r"\bJL[0-9][A-Z][0-9]{2,4}[A-Z]{0,4}\b")],
    "BY": [re.compile(r"\bBYD[0-9]{7,10}\b"), re.compile(r"\b[0-9]{10}(-[0-9]{2})?\b")],
}


def norm_oem(value: str) -> str:
    value = str(value or "").strip().upper().replace("_", "-")
    value = re.sub(r"\s+", "", value)
    value = re.sub(r"[^A-Z0-9\-\.]", "", value)
    value = re.sub(r"-{2,}", "-", value)
    return value.strip("-")


def split_oem_candidates(value: object) -> list[str]:
    """Split supplier fields that contain several interchange/OEM numbers."""
    if isinstance(value, (list, tuple, set)):
        raw_values = [str(item or "") for item in value]
    else:
        raw_values = [str(value or "")]

    candidates: list[str] = []
    for raw in raw_values:
        for item in re.split(r"[,;/|]+", raw):
            token = norm_oem(item)
            if token and token not in candidates:
                candidates.append(token)
    return candidates


def is_obvious_bad_token(value: str) -> bool:
    token = norm_oem(value)
    compact = re.sub(r"[^A-Z0-9]", "", token)
    if not token or not compact:
        return True
    if token in BAD_OEM_WORDS:
        return True
    if any(fragment in token for fragment in BAD_OEM_FRAGMENTS):
        return True
    if any(word in token for word in BAD_DATE_WORDS):
        return True
    if any(pattern.fullmatch(token) or pattern.fullmatch(compact) for pattern in COMMON_BAD_PATTERNS):
        return True
    if token.startswith(("HTTP", "WWW", "IMG", "SRC", "DATA", "WP-", "JS-")):
        return True
    if token.startswith("G-") and len(token) > 8:
        return True
    if re.fullmatch(r"[A-Z]+", compact):
        return True
    if len(set(compact)) <= 2:
        return True
    return False


def is_plausible_oem(prefix: str, value: str, *, strict_brand: bool = True) -> bool:
    prefix = str(prefix or "").strip().upper()
    token = norm_oem(value)
    compact = re.sub(r"[^A-Z0-9]", "", token)
    if len(compact) < 6 or len(compact) > 24:
        return False
    if is_obvious_bad_token(token):
        return False
    if not re.search(r"\d", compact):
        return False

    patterns = OEM_FORMAT_PATTERNS.get(prefix, [])
    if patterns:
        if not any(pattern.search(token) for pattern in patterns):
            return False if strict_brand else _generic_plausible(token)
        if prefix in {"VW", "AU", "SK", "SE"}:
            digits = sum(1 for c in compact if c.isdigit())
            letters = sum(1 for c in compact if c.isalpha())
            if digits < 5 or letters < 1 or letters > 4:
                return False
            if not (compact[0].isdigit() or compact.startswith("N") or compact.startswith("W")):
                return False
        return True

    return _generic_plausible(token)


def _generic_plausible(token: str) -> bool:
    compact = re.sub(r"[^A-Z0-9]", "", token)
    digits = sum(1 for c in compact if c.isdigit())
    letters = sum(1 for c in compact if c.isalpha())
    if digits < 3:
        return False
    if "-" not in token and len(token) > 14:
        return False
    if "-" not in token and letters > 6 and digits < 5:
        return False
    if re.fullmatch(r"[A-Z]{1,2}-[A-Z0-9]{8,}", token):
        return False
    return True
