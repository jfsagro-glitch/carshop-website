import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');
const sourcePath = path.join(rootDir, 'cars_europe_new.json');
const outputPath = path.join(rootDir, 'data', 'home_featured_europe.json');
const historyPath = path.join(rootDir, 'data', 'telegram_europe_history.json');
const excludeHistory = process.argv.includes('--exclude-history');

const TARGETS = [
  { brand: 'Audi', model: /(?:^|\s)A4(?:\s|$)/i },
  { brand: 'Audi', model: /(?:^|\s)A3(?:\s|$)/i },
  { brand: 'Audi', model: /(?:^|\s)Q3(?:\s|$)/i },
  { brand: 'BMW', model: /(?:^|\s)(?:3|3er|3[\s-]?series|31[68][di]?|32\d[di]?|33\d[di]?|34\d[di]?)(?:\s|$)/i },
  { brand: 'BMW', model: /(?:^|\s)216[di]?(?:\s|$)/i },
  { brand: 'BMW', model: /(?:^|\s)X1(?:\s|$)/i },
  { brand: 'BMW', model: /(?:^|\s)X2(?:\s|$)/i },
  { brand: 'Mercedes-Benz', model: /(?:^|\s)C\s*180(?:\s|$)/i },
  { brand: 'Mercedes-Benz', model: /(?:^|\s)B\s*180(?:\s|$)/i },
  { brand: 'Mercedes-Benz', model: /(?:^|\s)GLA(?:\s|$)/i },
  { brand: 'Mercedes-Benz', model: /(?:^|\s)GLB\s*180(?:\s|$)/i },
  { brand: 'Volkswagen', model: /(?:^|\s)Arteon(?:\s|$)/i },
  { brand: 'Volkswagen', model: /(?:^|\s)T-?Roc(?:\s|$)/i },
  { brand: 'Volkswagen', model: /(?:^|\s)Golf\s+GTE(?:\s|$)/i },
  { brand: 'Volkswagen', model: /(?:^|\s)T6(?:\.1)?\s+Caravelle(?:\s|$)/i },
  { brand: 'Volkswagen', model: /(?:^|\s)Passat(?:\s|$)/i },
  { brand: 'Opel', model: /(?:^|\s)Mokka(?:\s|$)/i },
  { brand: 'Opel', model: /(?:^|\s)Crossland(?:\s|$)/i },
  { brand: 'Skoda', model: /(?:^|\s)Kodiaq(?:\s|$)/i },
  { brand: 'Skoda', model: /(?:^|\s)Octavia(?:\s|$)/i },
];

function normalize(value) {
  return String(value || '').toLowerCase().replace(/[^a-zа-я0-9]/g, '');
}

function images(car) {
  return (Array.isArray(car.images) ? car.images : [])
    .map((image) => typeof image === 'string' ? image : image?.url)
    .filter(Boolean)
    .slice(0, 12);
}

async function hasReachableImage(car) {
  for (const url of images(car).slice(0, 3)) {
    try {
      const response = await fetch(url, {
        headers: {
          'User-Agent': 'Mozilla/5.0',
          Referer: 'https://www.autoscout24.de/',
        },
      });
      if (response.ok && String(response.headers.get('content-type') || '').startsWith('image/')) {
        await response.body?.cancel();
        return true;
      }
      await response.body?.cancel();
    } catch {
      // Try the next photo or candidate.
    }
  }
  return false;
}

function matches(car, target) {
  const modelText = `${car.model || ''} ${car.full_title || ''}`.trim();
  return normalize(car.brand) === normalize(target.brand) && target.model.test(modelText);
}

function hasAutomaticTransmission(car) {
  const transmission = normalize(car.transmission || car.gearbox || '');
  return transmission.includes('автомат')
    || transmission.includes('automatic')
    || transmission.includes('automatik')
    || transmission.includes('dsg')
    || transmission.includes('stronic')
    || transmission.includes('steptronic')
    || transmission.includes('gtronic')
    || transmission.includes('dct');
}

function engineLabel(car) {
  const cc = Number(car.engine_cc || 0);
  const verified = String(car.engine_source || '').startsWith('autoscout24_');
  if (!verified || cc < 500 || cc > 10000) return 'уточняется';
  const liters = (cc / 1000).toLocaleString('ru-RU', { maximumFractionDigits: 3 });
  return `${liters} ${car.fuel_type || ''}`.trim();
}

function powerLabel(car) {
  const hp = Number(car.power_hp || 0);
  const kw = Number(car.power_kw || 0);
  if (hp && kw) return `${hp} л.с. / ${kw} кВт`;
  if (hp) return `${hp} л.с.`;
  if (kw) return `${kw} кВт`;
  return 'уточняется';
}

function toOffer(car, target) {
  const carImages = images(car);
  const year = car.year || car.first_registration_year || '';
  const title = `${car.brand || target.brand} ${car.model || ''} ${year}`.trim();
  const turnkey = `${Math.round(Number(car.turnkey_price_rub)).toLocaleString('ru-RU')} ₽`;
  const basePrice = `${Number(car.price).toLocaleString('ru-RU')} €`;

  return {
    channel: 'europe_catalog',
    region: 'Европа',
    source: 'AutoScout24',
    source_type: 'europe_catalog',
    source_url: car.url || '',
    title,
    year: String(year),
    price: turnkey,
    base_price: basePrice,
    image: carImages[0],
    images: carImages,
    details: {
      engine: engineLabel(car),
      power: powerLabel(car),
      mileage: `${Number(car.mileage).toLocaleString('ru-RU')} км`,
    },
    text_excerpt: `${car.full_title || title}. Цена в Европе ${basePrice}, стоимость под ключ в РФ ${turnkey}.`,
    facts: ['выгодное предложение', 'пробег до 100 000 км', `цена в Европе: ${basePrice}`],
  };
}

const cars = JSON.parse(await fs.readFile(sourcePath, 'utf8'));
let postedUrls = new Set();
if (excludeHistory) {
  try {
    const history = JSON.parse(await fs.readFile(historyPath, 'utf8'));
    postedUrls = new Set(
      (Array.isArray(history.posts) ? history.posts : [])
        .map((post) => post?.source_url)
        .filter(Boolean),
    );
  } catch (error) {
    if (error?.code !== 'ENOENT') throw error;
  }
}

const offers = [];
for (const target of TARGETS) {
  const candidates = cars
    .filter((car) => matches(car, target))
    .filter((car) => !postedUrls.has(car.url))
    .filter((car) => {
      const mileage = Number(car.mileage || 0);
      return mileage > 0
        && mileage <= 100000
        && Number(car.price || 0) > 0
        && Number(car.turnkey_price_rub || 0) > 0
        && car.turnkey_calculation_complete
        && hasAutomaticTransmission(car)
        && images(car).length > 0;
    })
    .sort((a, b) => Number(a.price) - Number(b.price));
  let selected = null;
  for (const candidate of candidates) {
    if (await hasReachableImage(candidate)) {
      selected = candidate;
      break;
    }
  }
  if (selected) offers.push(toOffer(selected, target));
}

if (offers.length !== TARGETS.length) {
  throw new Error(`Expected ${TARGETS.length} featured Europe offers, got ${offers.length}`);
}

await fs.writeFile(
  outputPath,
  `${JSON.stringify({ generated_at: new Date().toISOString(), offers }, null, 2)}\n`,
  'utf8',
);

console.log(`Saved ${offers.length} featured Europe offers`);
