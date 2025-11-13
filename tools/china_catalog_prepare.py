import json
import pathlib
import re
import shutil

def main():
    root = pathlib.Path('images/china')
    src_dir = next(root.glob('*_files'))
    products = json.loads((root / 'china_cars.json').read_text(encoding='utf-8'))
    dest_dir = root / 'catalog'
    dest_dir.mkdir(exist_ok=True)
    used = set()
    missing = []
    for product in products:
        image = product.get('image')
        if not image:
            continue
        filename = pathlib.Path(image).name
        src = src_dir / filename
        if not src.exists():
            missing.append(filename)
            continue
        parts = product['name'].split(' ', 1)
        brand_key = parts[0]
        rest = parts[1] if len(parts) > 1 else ''
        base = ('{}-{}').format(brand_key.lower(), rest.lower()) if rest else brand_key.lower()
        base = re.sub(r'[^a-z0-9]+', '-', base).strip('-') or 'car'
        slug = base
        idx = 2
        while slug in used:
            slug = '{}-{}'.format(base, idx)
            idx += 1
        used.add(slug)
        dest = dest_dir / '{}.webp'.format(slug)
        shutil.copy2(src, dest)
        product['image'] = 'images/china/catalog/{}'.format(dest.name)
    (root / 'china_catalog.json').write_text(json.dumps(products, ensure_ascii=False, indent=2), encoding='utf-8')
    if missing:
        print('Missing images:', missing)
    print('Processed', len(products), 'items')

if __name__ == '__main__':
    main()
