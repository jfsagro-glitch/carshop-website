import json
import pathlib
import re

def format_brand(key: str) -> str:
    mapping = {
        'NISSAN': 'Nissan',
        'VOLKSWAGEN': 'Volkswagen',
        'HONDA': 'Honda',
        'MAZDA': 'Mazda',
        'JETTA': 'Jetta',
        'HYUNDAI': 'Hyundai',
        'SKODA': 'Skoda',
        'TOYOTA': 'Toyota',
        'KIA': 'Kia',
        'GEELY': 'Geely',
        'MERCEDES-BENZ': 'Mercedes-Benz',
        'MG': 'MG',
        'BYD': 'BYD',
        'AION': 'Aion',
        'BAOJUN': 'Baojun',
        'JAC': 'JAC'
    }
    return mapping.get(key, key.title())

UPPER_TOKENS = {
    'EV', 'DM-I', 'DM-I', 'DM-P', 'DM', 'GT', 'MPV', 'SUV', 'AWD', 'PHEV',
    'VA7', 'VS8', 'BZ3X', 'EZ-6', 'MG4', 'UT', 'UP', 'L'
}


def format_token(token: str) -> str:
    if token.upper() in UPPER_TOKENS:
        return token.upper()
    if token.isupper() and len(token) <= 3 and token.upper() not in UPPER_TOKENS:
        return token.capitalize()
    if re.search(r'[0-9]', token):
        return token.upper()
    if '-' in token:
        return '-'.join(format_token(part) for part in token.split('-'))
    return token.capitalize()

def format_model(text: str) -> str:
    if not text:
        return ''
    tokens = [t for t in re.split(r'\s+', text.strip()) if t]
    return ' '.join(format_token(token) for token in tokens)

def normalize_spec_key(text: str) -> str:
    return re.sub(r'[^a-z0-9а-яё]+', '', text.lower())


SPEC_MAP = {
    normalize_spec_key('Тип двигателя'): ('engineType', ''),
    normalize_spec_key('Мощность, л.с.'): ('power', ' л.с.'),
    normalize_spec_key('Мощность, кВт'): ('power', ' кВт'),
    normalize_spec_key('Макс. скорость, км/ч'): ('maxSpeed', ' км/ч'),
    normalize_spec_key('Привод'): ('drive', ''),
    normalize_spec_key('Объем двигателя'): ('engineVolume', ''),
    normalize_spec_key('Трансмиссия'): ('transmission', ''),
    normalize_spec_key('Разгон 0-100 км, сек'): ('acceleration', ' с'),
    normalize_spec_key('Расход топлива'): ('consumption', ' л/100 км'),
    normalize_spec_key('Запас хода, км'): ('range', ' км'),
    normalize_spec_key('Энергия аккумулятора, кВтч'): ('battery', ' кВт·ч'),
    normalize_spec_key('Энергия батареи, кВтч'): ('battery', ' кВт·ч'),
    normalize_spec_key('Батарея, кВтч'): ('battery', ' кВт·ч')
}

def main():
    root = pathlib.Path('images/china')
    items = json.loads((root / 'china_catalog.json').read_text(encoding='utf-8'))
    processed = []
    for item in items:
        raw_name = item.get('name', '').strip()
        if not raw_name:
            continue
        parts = raw_name.split(' ', 1)
        brand_key = parts[0]
        model_raw = parts[1] if len(parts) > 1 else ''
        brand = format_brand(brand_key)
        model = format_model(model_raw)
        entry = {
            'name': ('{} {}'.format(brand, model)).strip(),
            'brand': brand,
            'model': model,
            'image': item.get('image'),
            'priceFrom': item.get('price') or None,
            'specs': item.get('specs', [])
        }
        for spec in item.get('specs', []):
            if ':' not in spec:
                continue
            key, value = [part.strip() for part in spec.split(':', 1)]
            mapped = SPEC_MAP.get(normalize_spec_key(key))
            if mapped and value:
                field, suffix = mapped
                cleaned = value.replace('\u00a0', ' ').replace('\u202f', ' ').strip()
                if cleaned in {'-', '—', '–'}:
                    entry[field] = cleaned
                elif cleaned and suffix and suffix.strip() not in cleaned:
                    entry[field] = '{}{}'.format(cleaned, suffix)
                else:
                    entry[field] = cleaned
        processed.append(entry)
    (root / 'china_processed.json').write_text(json.dumps(processed, ensure_ascii=False, indent=2), encoding='utf-8')
    print('processed', len(processed))

if __name__ == '__main__':
    main()
