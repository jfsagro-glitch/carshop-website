#!/usr/bin/env python3
"""
Probe for VAG (Volkswagen, Audi, Skoda, Seat) and Mercedes OEM sources.
Tests alternative domains, APIs, and workarounds for SSL-blocked sites.
"""

import requests
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin
import warnings

# Suppress SSL warnings for this probe
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / "data"

# Alternative VAG sources to test
VAG_SOURCES = {
    'volkswagen_partsinfo': {
        'domains': [
            'https://parts.volkswagen.de/sitemap.xml',
            'https://parts.vw.de/sitemap.xml',
            'https://partsinfo.volkswagen.de/sitemap.xml',
        ],
        'description': 'Official VW Parts sitemaps'
    },
    'audi_partsinfo': {
        'domains': [
            'https://parts.audi.de/sitemap.xml',
            'https://partsinfo.audi.de/sitemap.xml',
            'https://parts.audi.com/sitemap.xml',
        ],
        'description': 'Official Audi Parts sitemaps'
    },
    'skoda_partsinfo': {
        'domains': [
            'https://parts.skoda.de/sitemap.xml',
            'https://partsinfo.skoda.de/sitemap.xml',
            'https://parts.skoda.com/sitemap.xml',
        ],
        'description': 'Official Skoda Parts sitemaps'
    },
    'seat_partsinfo': {
        'domains': [
            'https://parts.seat.de/sitemap.xml',
            'https://partsinfo.seat.de/sitemap.xml',
            'https://parts.seat.com/sitemap.xml',
        ],
        'description': 'Official Seat Parts sitemaps'
    },
    'porsche_partsinfo': {
        'domains': [
            'https://parts.porsche.de/sitemap.xml',
            'https://partsinfo.porsche.de/sitemap.xml',
        ],
        'description': 'Official Porsche Parts sitemaps'
    },
}

MERCEDES_SOURCES = {
    'mercedes_partsinfo': {
        'domains': [
            'https://parts.mercedes-benz.de/sitemap.xml',
            'https://partsinfo.mercedes-benz.de/sitemap.xml',
            'https://parts.mercedes-benz.com/sitemap.xml',
        ],
        'description': 'Official Mercedes Parts sitemaps'
    },
    'amg_partsinfo': {
        'domains': [
            'https://parts.amg.de/sitemap.xml',
            'https://partsinfo.amg.de/sitemap.xml',
        ],
        'description': 'Official AMG Parts sitemaps'
    },
}

PARTNER_APIS = {
    'elcats_ru': {
        'url': 'https://elcats.ru/api/oem',
        'description': 'ELCats Russian catalog API',
        'requires_auth': False,
    },
    'exist_ru_api': {
        'url': 'https://exist.ru/api/search',
        'description': 'Exist.ru catalog API',
        'requires_auth': True,
    },
    'emex_ru_api': {
        'url': 'https://api.emex.ru/search',
        'description': 'Emex.ru catalog API',
        'requires_auth': True,
    },
}


class VAGMercedesProbe:
    def __init__(self, verify_ssl: bool = True):
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        self.results = {
            'accessible_sitemaps': [],
            'blocked_sitemaps': [],
            'api_endpoints': [],
            'status_summary': {},
        }
    
    def probe_sitemap(self, url: str, brand_group: str, timeout: int = 10) -> Optional[Dict]:
        """
        Probe a sitemap URL for accessibility.
        Returns status info or None if unreachable.
        """
        try:
            logger.info(f"Probing sitemap: {url}")
            r = self.session.get(url, timeout=timeout, verify=self.verify_ssl)
            
            result = {
                'url': url,
                'brand_group': brand_group,
                'status_code': r.status_code,
                'accessible': r.status_code in [200, 301, 302],
                'error': None,
                'ssl_verified': self.verify_ssl,
            }
            
            if r.status_code == 200:
                # Check if it's valid XML
                try:
                    r.xml
                    result['valid_xml'] = True
                    result['size_bytes'] = len(r.content)
                except:
                    result['valid_xml'] = False
                    logger.warning(f"Response not valid XML: {url}")
            
            logger.info(f"  Status: {r.status_code}, Accessible: {result['accessible']}")
            return result
        
        except requests.exceptions.SSLError as e:
            logger.warning(f"SSL Error on {url}: {str(e)[:100]}")
            return {
                'url': url,
                'brand_group': brand_group,
                'accessible': False,
                'error': f'SSLError: {str(e)[:100]}',
                'ssl_verified': True,
                'status_code': None,
            }
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Connection Error on {url}: {str(e)[:100]}")
            return {
                'url': url,
                'brand_group': brand_group,
                'accessible': False,
                'error': f'ConnectionError: {str(e)[:100]}',
                'ssl_verified': True,
                'status_code': None,
            }
        except requests.exceptions.Timeout as e:
            logger.warning(f"Timeout on {url}")
            return {
                'url': url,
                'brand_group': brand_group,
                'accessible': False,
                'error': 'Timeout',
                'ssl_verified': True,
                'status_code': None,
            }
        except Exception as e:
            logger.error(f"Unexpected error on {url}: {e}")
            return {
                'url': url,
                'brand_group': brand_group,
                'accessible': False,
                'error': f'Error: {str(e)[:100]}',
                'ssl_verified': True,
                'status_code': None,
            }
    
    def probe_api_endpoint(self, api_url: str, service_name: str, 
                          requires_auth: bool = False, timeout: int = 10) -> Optional[Dict]:
        """
        Probe an API endpoint for accessibility.
        """
        try:
            logger.info(f"Probing API: {api_url}")
            
            headers = dict(self.session.headers)
            if requires_auth:
                # Try with placeholder auth
                headers['Authorization'] = 'Bearer test_token'
            
            r = self.session.get(api_url, headers=headers, timeout=timeout, 
                               verify=self.verify_ssl)
            
            result = {
                'url': api_url,
                'service': service_name,
                'status_code': r.status_code,
                'accessible': r.status_code in [200, 401, 403],  # Even 401 means endpoint exists
                'error': None,
                'requires_auth': requires_auth,
            }
            
            logger.info(f"  Status: {r.status_code}, Accessible: {result['accessible']}")
            return result
        
        except Exception as e:
            logger.warning(f"Error probing {api_url}: {e}")
            return {
                'url': api_url,
                'service': service_name,
                'accessible': False,
                'error': str(e)[:100],
                'requires_auth': requires_auth,
            }
    
    def probe_vag_sources(self) -> None:
        """Probe all VAG alternative sources"""
        logger.info("="*60)
        logger.info("Probing VAG (VW/Audi/Skoda/Seat) sources")
        logger.info("="*60)
        
        vag_accessible = []
        vag_blocked = []
        
        for group, config in VAG_SOURCES.items():
            logger.info(f"\nProbing {group}: {config['description']}")
            
            for domain in config['domains']:
                result = self.probe_sitemap(domain, f"VAG-{group}")
                
                if result:
                    if result['accessible']:
                        vag_accessible.append(result)
                    else:
                        vag_blocked.append(result)
                
                time.sleep(1)
        
        self.results['vag_accessible'] = vag_accessible
        self.results['vag_blocked'] = vag_blocked
        
        logger.info(f"\nVAG Summary: {len(vag_accessible)} accessible, "
                   f"{len(vag_blocked)} blocked")
    
    def probe_mercedes_sources(self) -> None:
        """Probe all Mercedes alternative sources"""
        logger.info("="*60)
        logger.info("Probing Mercedes sources")
        logger.info("="*60)
        
        mercedes_accessible = []
        mercedes_blocked = []
        
        for group, config in MERCEDES_SOURCES.items():
            logger.info(f"\nProbing {group}: {config['description']}")
            
            for domain in config['domains']:
                result = self.probe_sitemap(domain, f"Mercedes-{group}")
                
                if result:
                    if result['accessible']:
                        mercedes_accessible.append(result)
                    else:
                        mercedes_blocked.append(result)
                
                time.sleep(1)
        
        self.results['mercedes_accessible'] = mercedes_accessible
        self.results['mercedes_blocked'] = mercedes_blocked
        
        logger.info(f"\nMercedes Summary: {len(mercedes_accessible)} accessible, "
                   f"{len(mercedes_blocked)} blocked")
    
    def probe_partner_apis(self) -> None:
        """Probe partner APIs"""
        logger.info("="*60)
        logger.info("Probing Partner APIs")
        logger.info("="*60)
        
        api_results = []
        
        for service, config in PARTNER_APIS.items():
            logger.info(f"\nProbing {service}: {config['description']}")
            
            result = self.probe_api_endpoint(
                config['url'],
                service,
                requires_auth=config.get('requires_auth', False)
            )
            
            if result:
                api_results.append(result)
            
            time.sleep(1)
        
        self.results['partner_apis'] = api_results
    
    def run_full_probe(self) -> None:
        """Run complete probe of all sources"""
        logger.info("\n" + "="*60)
        logger.info("STARTING FULL VAG/MERCEDES PROBE")
        logger.info("SSL Verification: " + ("Enabled" if self.verify_ssl else "Disabled"))
        logger.info("="*60 + "\n")
        
        try:
            self.probe_vag_sources()
            time.sleep(2)
            self.probe_mercedes_sources()
            time.sleep(2)
            self.probe_partner_apis()
        except KeyboardInterrupt:
            logger.info("\nProbe interrupted by user")
        except Exception as e:
            logger.error(f"Probe error: {e}")
    
    def export_results(self, output_path: Path) -> None:
        """Export probe results to JSON"""
        with output_path.open('w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\nExported probe results to {output_path}")
    
    def print_summary(self) -> None:
        """Print summary of probe results"""
        logger.info("\n" + "="*60)
        logger.info("PROBE SUMMARY")
        logger.info("="*60)
        
        vag_accessible = self.results.get('vag_accessible', [])
        vag_blocked = self.results.get('vag_blocked', [])
        mercedes_accessible = self.results.get('mercedes_accessible', [])
        mercedes_blocked = self.results.get('mercedes_blocked', [])
        api_results = self.results.get('partner_apis', [])
        
        logger.info(f"\nVAG Sources:")
        logger.info(f"  ✓ Accessible: {len(vag_accessible)}")
        for result in vag_accessible:
            logger.info(f"    - {result['url']}")
        
        logger.info(f"  ✗ Blocked: {len(vag_blocked)}")
        for result in vag_blocked[:5]:  # Show first 5
            logger.info(f"    - {result['url']} ({result.get('error', 'Unknown')[:50]})")
        
        logger.info(f"\nMercedes Sources:")
        logger.info(f"  ✓ Accessible: {len(mercedes_accessible)}")
        for result in mercedes_accessible:
            logger.info(f"    - {result['url']}")
        
        logger.info(f"  ✗ Blocked: {len(mercedes_blocked)}")
        for result in mercedes_blocked[:5]:
            logger.info(f"    - {result['url']} ({result.get('error', 'Unknown')[:50]})")
        
        logger.info(f"\nPartner APIs:")
        for result in api_results:
            status = "✓ Accessible" if result['accessible'] else "✗ Blocked"
            logger.info(f"  {status}: {result['service']}")
        
        logger.info("\n" + "="*60)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Probe VAG and Mercedes OEM sources')
    parser.add_argument('--skip-ssl', action='store_true',
                       help='Skip SSL verification (for blocked domains)')
    parser.add_argument('--output', type=Path,
                       default=DATA_DIR / 'vag_mercedes_probe_results.json',
                       help='Output JSON path')
    args = parser.parse_args()
    
    probe = VAGMercedesProbe(verify_ssl=not args.skip_ssl)
    probe.run_full_probe()
    probe.print_summary()
    probe.export_results(args.output)


if __name__ == '__main__':
    main()
