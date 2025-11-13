import json
import pathlib
import re
import shutil

from bs4 import BeautifulSoup


ROOT = pathlib.Path('images/Korea')
DEST = ROOT / 'catalog'
DEST.mkdir(parents=True, exist_ok=True)
for file in DEST.glob('*'):
    if file.is_file():
        file.unlink()


def slugify(*parts: str) -> str:
    base = '-'.join(filter(None, parts))
    base = base.lower()
    base = re.sub(r'[^a-z0-9]+', '-', base).strip('-')
    return base or 'car'


def normalize_text(value: str) -> str:
    return value.replace('\xa0', ' ').strip()


image_lookup = {}
for img_path in ROOT.glob('**/*.jpg'):
    image_lookup.setdefault(img_path.name.lower(), img_path)


cars_map = {}
seen_ids = set()

html_paths = sorted(ROOT.glob('PAN AUTO *.html'), key=lambda p: p.name)

for html_path in html_paths:
    soup = BeautifulSoup(html_path.read_text(encoding='utf-8', errors='ignore'), 'html.parser')
    cards = soup.select('a._carPreview_1ldw6_2')
    for card in cards:
        link = card.get('href', '')
        id_match = re.search(r'(\d+)', link)
        car_id = id_match.group(1) if id_match else None
        if car_id and car_id in seen_ids:
            continue

        name_el = card.select_one('h2._titleXXXS_8e58f_24')
        if not name_el:
            continue
        name = normalize_text(name_el.get_text(' ', strip=True))
        if not name:
            continue

        parts = name.split()
        brand = parts[0]
        model = name[len(brand):].strip()

        spec_entries = []
        spec_paragraphs = card.select('p._textSDefault_g0usn_91')
        if spec_paragraphs:
            primary_text = normalize_text(spec_paragraphs[0].get_text(' ', strip=True))
            main_parts = [normalize_text(part) for part in primary_text.split(',') if part.strip()]
            if len(main_parts) > 0:
                spec_entries.append(f'Мощность: {main_parts[0]}')
            if len(main_parts) > 1:
                spec_entries.append(f'Топливо: {main_parts[1]}')
            if len(main_parts) > 2:
                spec_entries.append(f'Объем двигателя: {main_parts[2]}')
        mileage_text = None
        if len(spec_paragraphs) >= 2:
            mileage_text = normalize_text(spec_paragraphs[1].get_text(' ', strip=True))
            if mileage_text:
                spec_entries.append(f'Пробег: {mileage_text}')
        date_text = None
        if len(spec_paragraphs) >= 3:
            date_text = normalize_text(spec_paragraphs[2].get_text(' ', strip=True))
            if date_text:
                spec_entries.append(f'Дата выпуска: {date_text}')

        price_el = card.select_one('h2._titleXXS_8e58f_28')
        price_text = normalize_text(price_el.get_text(' ', strip=True)) if price_el else ''
        price_digits = re.sub(r'[^0-9]', '', price_text)
        price_value = int(price_digits) if price_digits else None

        city_badges = card.select('div._cityBadge_1ldw6_63')
        if city_badges:
            city_text = normalize_text(city_badges[0].get_text(' ', strip=True))
            if city_text:
                spec_entries.append(f'Логистика: {city_text}')

        description_parts = []
        label_el = card.select_one('p._todayLabel_1ldw6_16')
        if label_el:
            description_parts.append(normalize_text(label_el.get_text(' ', strip=True)))

        new_fee_el = card.select_one('p._newFeeText_1ldw6_70')
        if new_fee_el:
            duty_text = normalize_text(new_fee_el.get_text(' ', strip=True))
            duty_date = ''
            if len(city_badges) > 1:
                duty_date = normalize_text(city_badges[1].get_text(' ', strip=True))
            duty_parts = [part for part in (duty_text, duty_date) if part]
            if duty_parts:
                description_parts.append(f"Пошлина: {' '.join(duty_parts)}")

        badge_texts = [normalize_text(badge.get_text(' ', strip=True)) for badge in card.select('div._badge_12nz8_86')]
        for badge in badge_texts:
            if not badge:
                continue
            if '₽' in badge:
                spec_entries.append(f'Дополнительная цена: {badge}')
            elif badge not in description_parts:
                description_parts.append(badge)

        seen_spec = set()
        filtered_specs = []
        for spec in spec_entries:
            if spec and spec not in seen_spec:
                filtered_specs.append(spec)
                seen_spec.add(spec)

        image_el = card.find('img', class_='_image_zdk07_9')
        if not image_el:
            continue
        src = image_el.get('src', '')
        filename = src.split('/')[-1].split('?')[0].lower()
        source_path = image_lookup.get(filename)
        if not source_path or not source_path.exists():
            continue

        mileage_value = None
        if mileage_text:
            mileage_digits = re.sub(r'[^\d]', '', mileage_text)
            if mileage_digits:
                try:
                    mileage_value = int(mileage_digits)
                except ValueError:
                    mileage_value = None

        year_value = None
        if date_text:
            year_match = re.search(r'(\d{4})', date_text)
            if year_match:
                try:
                    year_value = int(year_match.group(1))
                except ValueError:
                    year_value = None

        entry = {
            '_id': car_id,
            'name': name,
            'brand': brand,
            'model': model,
            'priceFrom': price_value,
            'priceLabel': price_text or None,
            'link': link or None,
            'specs': filtered_specs,
            'description': ' · '.join(dict.fromkeys(description_parts)) if description_parts else None,
            '_mileage': mileage_value,
            '_year': year_value,
            '_source_path': source_path,
            '_slug': slugify(brand, model or (car_id or name)),
        }

        key = (brand, model)
        existing = cars_map.get(key)

        def is_better(candidate, existing_entry):
            if existing_entry is None:
                return True
            cp = candidate['priceFrom']
            ep = existing_entry['priceFrom']
            if cp is not None and ep is not None:
                if cp < ep:
                    return True
                if cp > ep:
                    return False
            elif cp is not None:
                return True
            elif ep is not None:
                return False

            cm = candidate['_mileage']
            em = existing_entry.get('_mileage')
            if cm is not None and em is not None:
                if cm < em:
                    return True
                if cm > em:
                    return False
            elif cm is not None:
                return True
            elif em is not None:
                return False

            cy = candidate['_year']
            ey = existing_entry.get('_year')
            if cy is not None and ey is not None:
                if cy > ey:
                    return True
                if cy < ey:
                    return False
            elif cy is not None:
                return True
            elif ey is not None:
                return False

            return False

        if is_better(entry, existing):
            cars_map[key] = entry
            if car_id:
                seen_ids.add(car_id)


def format_price_label(value: int) -> str:
    return f"{value:,}".replace(',', ' ') + " ₽"


cars = []
for _, entry in sorted(cars_map.items(), key=lambda item: (item[0][0], item[0][1])):
    source_path = entry.pop('_source_path', None)
    if not source_path:
        continue
    slug = entry.pop('_slug', slugify(entry['brand'], entry['model']))
    dest_path = DEST / f'{slug}{source_path.suffix.lower()}'
    counter = 2
    while dest_path.exists():
        dest_path = DEST / f'{slug}-{counter}{source_path.suffix.lower()}'
        counter += 1
    shutil.copy2(source_path, dest_path)

    entry['image'] = f'images/korea/catalog/{dest_path.name}'
    if entry.get('priceFrom') is not None and not entry.get('priceLabel'):
        entry['priceLabel'] = format_price_label(entry['priceFrom'])
    if not entry.get('description'):
        entry.pop('description', None)
    entry.pop('_mileage', None)
    entry.pop('_year', None)
    entry.pop('_id', None)
    cars.append(entry)


output_path = ROOT / 'korea_processed.json'
output_path.write_text(json.dumps(cars, ensure_ascii=False, indent=2), encoding='utf-8')

