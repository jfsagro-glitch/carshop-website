#!/usr/bin/env python3
"""
Targeted OEM gap-driven importer.
Reads oem_gap_worklist.csv and searches suggested sources for missing brand×code pairs.
Focuses on high-priority gaps first to maximize coverage improvement.
"""

import csv
import re
import requests
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from urllib.parse import quote
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, local

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / "data"
TOOLS_DIR = REPO_ROOT / "tools"

# Query templates for each domain type
SEARCH_TEMPLATES = {
    "emex.ru": "https://emex.ru/search?q={query}",
    "exist.ru": "https://exist.ru/search.php?search={query}",
    "realoem.com": "https://www.realoem.com/bmw/enUS/select?q={query}",
    "bmwcats.com": "https://bmwcats.com/search/?q={query}",
    "relines.ru": "https://relines.ru/search?q={query}",
    "xn--80aaonli0a.xn--p1ai": "https://xn--80aaonli0a.xn--p1ai/search?q={query}",
    "rockauto.com": "https://www.rockauto.com/en/catalog/",
    "autoparts24.eu": "https://www.autoparts24.eu/search?q={query}",
    "japan-parts.eu": "https://www.japan-parts.eu/search?q={query}",
    "alvadi.ee": "https://www.alvadi.ee/search/?q={query}",
    "partsale.eu": "https://partsale.eu/search?q={query}",
    "trshop.audi.de": "https://www.audi.de/de/brand/de/service-und-zubehoer/ersatzteile.html",
    "elcats.ru": "https://elcats.ru/search?q={query}",
    "hondaworld.ru": "https://www.hondaworld.ru/search?q={query}",
    "acurapartswarehouse.com": "https://www.acurapartswarehouse.com/search?q={query}",
}

TRUSTED_EXTRACT_DOMAINS = {
    "emex.ru",
    "exist.ru",
    "acurapartswarehouse.com",
    "hondaworld.ru",
    "realoem.com",
    "bmwcats.com",
    "elcats.ru",
}

class GapTargetedImporter:
    OEM_TOKEN_RE = re.compile(r"\b[A-Z0-9][A-Z0-9\-]{5,24}\b")

    def __init__(self, timeout: int = 8):
        self.timeout = timeout
        self._tls = local()
        self._lock = Lock()
        self.results = []
        self.failed_searches = []

    def _get_session(self) -> requests.Session:
        if not hasattr(self._tls, "session"):
            s = requests.Session()
            s.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            self._tls.session = s
        return self._tls.session

    def _extract_oem_candidate(self, html: str, part_code: str) -> Optional[str]:
        tokens = self.OEM_TOKEN_RE.findall(html.upper())
        if not tokens:
            return None

        normalized_part = part_code.strip().upper()
        blacklist = {
            "HTTP", "HTTPS", "CONTENT", "SCRIPT", "STYLE", "WINDOW", "RETURN",
            "SEARCH", "PARTS", "QUERY", "INDEX", "CLASS", "VALUE", "FALSE", "TRUE",
            "PRESET", "SPACING", "DISPLAY", "MARGIN", "PADDING", "BORDER", "INLINE",
        }

        ranked = []
        for token in tokens:
            if token in blacklist:
                continue
            if "--" in token:
                continue
            if token.startswith("WP-") or token.startswith("JS-"):
                continue
            if re.fullmatch(r"\d{2,4}X\d{2,4}", token):
                continue
            if token == normalized_part:
                continue
            if token.isalpha():
                continue
            if len(token) < 6:
                continue
            digits = sum(1 for c in token if c.isdigit())
            letters = sum(1 for c in token if c.isalpha())
            if digits < 3:
                continue
            if digits + letters < 6:
                continue
            if "-" not in token and len(token) > 12:
                continue
            if "-" not in token and letters > 4:
                continue
            # Prefer tokens that look like real OEM: contain both digits and letters.
            score = 0
            if "-" in token:
                score += 2
            if letters > 0 and digits > 0:
                score += 3
            if digits >= 5:
                score += 2
            if normalized_part and normalized_part in token:
                score -= 1
            ranked.append((score, token))

        if not ranked:
            return None

        ranked.sort(key=lambda x: x[0], reverse=True)
        best_score, best_token = ranked[0]
        return best_token if best_score >= 4 else None
        
    def parse_suggested_sources(self, sources_str: str) -> List[Tuple[str, str]]:
        """
        Parse suggested_sources column.
        Format: "domain1 (type1); domain2 (type2); ..."
        Returns list of (domain, search_type) tuples.
        """
        if not sources_str:
            return []
        
        sources = []
        for item in sources_str.split(';'):
            item = item.strip()
            if '(' in item and ')' in item:
                domain = item[:item.index('(')].strip()
                search_type = item[item.index('(')+1:item.index(')')].strip()
                sources.append((domain, search_type))
        return sources
    
    def search_domain_emex(self, domain: str, brand: str, part_code: str, 
                           part_name: str, max_retries: int = 3) -> Optional[Dict]:
        """Search emex.ru API for OEM number"""
        try:
            # Try generic query first: brand + part code
            query = f"{brand} {part_code}".strip()
            url = f"https://emex.ru/search?q={quote(query)}"
            
            for attempt in range(max_retries):
                try:
                    r = self._get_session().get(url, timeout=self.timeout)
                    if r.status_code == 200:
                        oem_number = self._extract_oem_candidate(r.text, part_code)
                        if oem_number:
                            return {
                                'oem_number': oem_number,
                                'source_name': domain,
                                'source_url': url,
                            }
                except requests.Timeout:
                    if attempt < max_retries - 1:
                        time.sleep(0.7)
                    continue
            return None
        except Exception as e:
            logger.debug(f"Error searching {domain}: {e}")
            return None
    
    def search_domain_generic(self, domain: str, brand: str, part_code: str,
                             part_name: str, max_retries: int = 3) -> Optional[Dict]:
        """Generic domain search (fallback)"""
        try:
            if domain not in SEARCH_TEMPLATES:
                return None
            if domain not in TRUSTED_EXTRACT_DOMAINS:
                return None
            
            template = SEARCH_TEMPLATES[domain]
            query = f"{brand} {part_code} {part_name}".strip()
            
            # Skip if URL requires no query parameter
            if "{query}" not in template:
                return None
            
            url = template.format(query=quote(query))
            
            for attempt in range(max_retries):
                try:
                    r = self._get_session().get(url, timeout=self.timeout)
                    if r.status_code == 200 and len(r.text) > 100:
                        oem_number = self._extract_oem_candidate(r.text, part_code)
                        if oem_number:
                            return {
                                'oem_number': oem_number,
                                'source_name': domain,
                                'source_url': url,
                            }
                except requests.Timeout:
                    if attempt < max_retries - 1:
                        time.sleep(0.7)
                    continue
            return None
        except Exception as e:
            logger.debug(f"Error on generic search {domain}: {e}")
            return None
    
    def search_gap(self, brand: str, brand_prefix: str, part_code: str, 
                   part_name: str, sources: List[Tuple[str, str]],
                   priority: str) -> Optional[Dict]:
        """
        Search suggested sources for a gap.
        Returns first successful result or None.
        """
        for domain, search_type in sources:
            if not domain.strip():
                continue
            
            logger.info(f"Searching {domain} for {brand_prefix}×{part_code} "
                       f"({part_name}) [priority={priority}]")
            
            # Try domain-specific search
            if domain == "emex.ru":
                result = self.search_domain_emex(domain, brand, part_code, part_name)
            else:
                result = self.search_domain_generic(domain, brand, part_code, part_name)
            
            if result:
                result.update({
                    'brand': brand,
                    'brand_prefix': brand_prefix,
                    'part_code': part_code,
                    'part_name': part_name,
                    'priority': priority,
                    'retrieved_at': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                })
                return result
            
            time.sleep(0.2)
        
        with self._lock:
            self.failed_searches.append({
                'brand': brand,
                'brand_prefix': brand_prefix,
                'part_code': part_code,
                'priority': priority,
            })
        return None
    
    def import_from_gaps(self, worklist_path: Path, max_gaps: Optional[int] = None,
                        priority_filter: str = "all", workers: int = 8) -> int:
        """
        Import from oem_gap_worklist.csv.
        Process high-priority gaps first.
        """
        logger.info(f"Reading gap worklist from {worklist_path}")
        
        gaps_by_priority = {'high': [], 'medium': [], 'low': []}
        
        with worklist_path.open('r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                priority = row.get('priority', 'low').lower()
                if priority not in gaps_by_priority:
                    priority = 'low'
                gaps_by_priority[priority].append(row)
        
        # Process in priority order, optionally filtered.
        all_gaps = []
        if priority_filter in {"high", "medium", "low"}:
            all_gaps.extend(gaps_by_priority[priority_filter])
        else:
            for p in ['high', 'medium', 'low']:
                all_gaps.extend(gaps_by_priority[p])
        
        if max_gaps:
            all_gaps = all_gaps[:max_gaps]
        
        logger.info(f"Processing {len(all_gaps)} gaps (high={len(gaps_by_priority['high'])} "
                   f"medium={len(gaps_by_priority['medium'])} low={len(gaps_by_priority['low'])})")
        
        processed = 0
        found = 0

        def process_gap(gap: Dict[str, str]) -> Optional[Dict]:
            sources_str = gap.get('suggested_sources', '')
            sources = self.parse_suggested_sources(sources_str)
            
            if not sources:
                return None

            return self.search_gap(
                brand=gap['brand'],
                brand_prefix=gap['brand_prefix'],
                part_code=gap['part_code'],
                part_name=gap.get('part_name', ''),
                sources=sources,
                priority=gap.get('priority', 'low'),
            )

        with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
            futures = [executor.submit(process_gap, gap) for gap in all_gaps]
            for future in as_completed(futures):
                result = future.result()
                processed += 1
                if result and result.get('oem_number'):
                    with self._lock:
                        self.results.append(result)
                    found += 1
                if processed % 50 == 0:
                    logger.info(
                        f"Progress: {processed}/{len(all_gaps)} gaps processed, {found} OEM found"
                    )
        
        logger.info(f"Completed: {processed} gaps searched, {found} OEM found")
        return found
    
    def export_results(self, output_path: Path) -> None:
        """Export results to CSV"""
        if not self.results:
            logger.warning("No results to export")
            return
        
        fieldnames = [
            'brand', 'brand_prefix', 'part_code', 'part_name', 'priority',
            'oem_number', 'source_name', 'source_url', 'retrieved_at'
        ]
        
        with output_path.open('w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in self.results:
                row = {k: result.get(k, '') for k in fieldnames}
                writer.writerow(row)
        
        logger.info(f"Exported {len(self.results)} results to {output_path}")
    
    def export_failed_searches(self, output_path: Path) -> None:
        """Export gaps that had no hits"""
        if not self.failed_searches:
            return
        
        with output_path.open('w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['brand', 'brand_prefix', 'part_code', 'priority'])
            writer.writeheader()
            writer.writerows(self.failed_searches)
        
        logger.info(f"Exported {len(self.failed_searches)} failed searches to {output_path}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Import OEM from gap worklist')
    parser.add_argument('--gap-worklist', type=Path, 
                       default=DATA_DIR / 'oem_gap_worklist.csv',
                       help='Path to gap worklist CSV')
    parser.add_argument('--output', type=Path,
                       default=DATA_DIR / 'oem_supplier_targeted_gaps.csv',
                       help='Output CSV path')
    parser.add_argument('--failed-output', type=Path,
                       default=DATA_DIR / 'oem_gap_failed_searches.csv',
                       help='Failed searches output CSV')
    parser.add_argument('--max-gaps', type=int, default=None,
                       help='Maximum number of gaps to process (for testing)')
    parser.add_argument('--priority', choices=['all', 'high', 'medium', 'low'], default='all',
                       help='Priority level to process')
    parser.add_argument('--workers', type=int, default=8,
                       help='Parallel worker threads')
    parser.add_argument('--timeout', type=int, default=8,
                       help='HTTP timeout per request in seconds')
    args = parser.parse_args()
    
    importer = GapTargetedImporter(timeout=args.timeout)
    found = importer.import_from_gaps(
        args.gap_worklist,
        max_gaps=args.max_gaps,
        priority_filter=args.priority,
        workers=args.workers,
    )
    
    if found > 0:
        importer.export_results(args.output)
    
    if importer.failed_searches:
        importer.export_failed_searches(args.failed_output)
    
    logger.info(f"Summary: Found {found} OEM from {len(importer.failed_searches)} failed searches")


if __name__ == '__main__':
    main()
