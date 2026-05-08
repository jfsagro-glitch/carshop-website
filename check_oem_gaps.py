import json
import re
from pathlib import Path

cat = json.load(open('data/parts_catalog.json', encoding='utf-8'))
template_codes = [p['code'] for p in cat['parts_template']]

content = open('generate_parts_catalog.py', encoding='utf-8').read()
keys = re.findall(r'\("([A-Z]+)",\s*"([A-Z0-9]+)"\)', content)
covered_codes = set(code for _, code in keys)

overrides_path = Path('data/oem_lookup_overrides.json')
override_codes = set()
if overrides_path.exists():
    raw = json.load(open(overrides_path, encoding='utf-8'))
    lookup = raw.get('lookup', raw)
    for brand_codes in lookup.values():
        if isinstance(brand_codes, dict):
            override_codes.update(str(code).upper() for code in brand_codes)

covered_codes |= override_codes
missing_codes = [c for c in template_codes if c not in covered_codes]

print(f"Template codes: {len(template_codes)}")
print(f"Codes with OEM entries including overrides: {len(covered_codes)}")
print(f"Codes covered by overrides: {len(override_codes)}")
print(f"Codes WITHOUT OEM entries ({len(missing_codes)}):")
for c in missing_codes:
    name = next((p['name'] for p in cat['parts_template'] if p['code']==c), '')
    print(f"  {c}: {name}")
