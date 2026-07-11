#!/usr/bin/env node
/** Build compact Europe catalog assets for fast browser loading. */

import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '..');
const sourcePath = path.join(root, 'cars_europe_new.json');
const outputDir = path.join(root, 'data', 'europe_catalog');
const manifestPath = path.join(outputDir, 'manifest.json');
const brandsDir = path.join(outputDir, 'brands');
const detailsDir = path.join(outputDir, 'details');

const source = JSON.parse(fs.readFileSync(sourcePath, 'utf8'));
if (!Array.isArray(source)) throw new Error('cars_europe_new.json must be an array');

const safeKey = (value) => String(value || 'other')
  .toLowerCase()
  .replace(/[^a-z0-9]+/g, '-')
  .replace(/^-+|-+$/g, '') || 'other';

const normalizeImages = (images) => (Array.isArray(images) ? images : [])
  .map((image) => typeof image === 'string' ? image : image?.url)
  .filter((url) => typeof url === 'string' && url.startsWith('http'));

const engineVolumeBucket = (car) => {
  const exactCc = Number(car.engine_cc || car.engine_displacement_cc || 0);
  if (Number.isFinite(exactCc) && exactCc >= 500 && exactCc <= 10000) {
    return (exactCc / 1000).toFixed(1);
  }
  const match = String(car.engine || '').replace(',', '.').match(/\d+(?:\.\d+)?/);
  if (!match) return '';
  let liters = Number(match[0]);
  if (liters > 10) liters /= 1000;
  return liters > 0 && liters <= 8 ? liters.toFixed(1) : '';
};

fs.rmSync(outputDir, { recursive: true, force: true });
fs.mkdirSync(detailsDir, { recursive: true });
fs.mkdirSync(brandsDir, { recursive: true });

const detailsByBrand = new Map();
const compactByBrand = new Map();
const compactCars = source.map((car, position) => {
  const id = String(car.id || car.external_id || car.url || position);
  const brandKey = safeKey(car.brand);
  const images = normalizeImages(car.images);
  if (!detailsByBrand.has(brandKey)) detailsByBrand.set(brandKey, {});
  detailsByBrand.get(brandKey)[id] = { images };

  const compact = {
    id,
    external_id: car.external_id || id,
    brand: car.brand || '',
    model: car.model || '',
    full_title: car.full_title || '',
    price: car.price || 0,
    mileage: car.mileage || 0,
    power_kw: car.power_kw || 0,
    power_hp: car.power_hp || 0,
    engine: car.engine || '',
    engine_cc: car.engine_cc || 0,
    engine_source: car.engine_source || '',
    first_registration: car.first_registration || '',
    first_registration_year: car.first_registration_year || 0,
    transmission: car.transmission || '',
    fuel_type: car.fuel_type || '',
    url: car.url || '',
    source: car.source || '',
    year: car.year || 0,
    month: car.month || 0,
    turnkey_price_rub: car.turnkey_price_rub || 0,
    turnkey_partial_price_rub: car.turnkey_partial_price_rub || 0,
    images: images.slice(0, 1).map((url) => ({ url, order: 1 })),
    image_count: images.length,
    details_file: `details/${brandKey}.json`,
  };
  if (!compactByBrand.has(brandKey)) compactByBrand.set(brandKey, []);
  compactByBrand.get(brandKey).push(compact);
  return compact;
});

for (const [brandKey, cars] of detailsByBrand) {
  fs.writeFileSync(
    path.join(detailsDir, `${brandKey}.json`),
    JSON.stringify({ cars }, null, 0),
  );
}

const brands = [...compactByBrand.entries()]
  .map(([key, cars]) => ({
    key,
    name: cars[0]?.brand || key,
    count: cars.length,
    models: [...new Set(cars.map((car) => car.model).filter(Boolean))].sort((a, b) => a.localeCompare(b, 'ru')),
    file: `brands/${key}.json`,
  }))
  .sort((a, b) => a.name.localeCompare(b.name, 'ru'));
for (const brand of brands) {
  fs.writeFileSync(
    path.join(outputDir, brand.file),
    JSON.stringify({ brand: brand.name, cars: compactByBrand.get(brand.key) }),
  );
}

const payload = {
  generated_at: new Date().toISOString(),
  total: compactCars.length,
  brands,
  filters: {
    transmissions: [...new Set(compactCars.map((car) => car.transmission).filter(Boolean))]
      .sort((a, b) => a.localeCompare(b, 'ru')),
    fuels: [...new Set(compactCars.map((car) => car.fuel_type).filter(Boolean))]
      .sort((a, b) => a.localeCompare(b, 'ru')),
    engine_volumes: [...new Set(compactCars.map(engineVolumeBucket).filter(Boolean))]
      .sort((a, b) => Number(a) - Number(b)),
  },
};
fs.writeFileSync(manifestPath, JSON.stringify(payload));

const manifestBytes = fs.statSync(manifestPath).size;
const indexBytes = brands.reduce(
  (total, brand) => total + fs.statSync(path.join(outputDir, brand.file)).size,
  0,
);
const detailsBytes = [...detailsByBrand.keys()]
  .reduce((total, key) => total + fs.statSync(path.join(detailsDir, `${key}.json`)).size, 0);
console.log(`Europe manifest: ${(manifestBytes / 1024).toFixed(1)} KB; brand indexes: ${(indexBytes / 1024 / 1024).toFixed(2)} MB`);
console.log(`Europe detail galleries: ${(detailsBytes / 1024 / 1024).toFixed(2)} MB across ${detailsByBrand.size} brand files`);
