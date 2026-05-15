import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');

const SOURCES = [
  { file: 'cars_georgia_stock.json', channel: 'myauto_georgia', region: 'Грузия', source: 'MyAuto Georgia', currency: 'USD' },
  { file: 'cars_korea_stock.json', channel: 'encar_korea', region: 'Корея', source: 'Encar Korea', currency: 'KRW' },
  { file: 'cars_europe_new.json', channel: 'europe_catalog', region: 'Европа', source: 'AutoScout24 / mobile.de', currency: 'EUR' },
];

function imageList(car) {
  const images = Array.isArray(car.images) ? car.images : [];
  return images
    .map((image) => typeof image === 'string' ? image : image?.url)
    .filter(Boolean)
    .slice(0, 12);
}

function formatRub(value) {
  return `${Math.round(Number(value) || 0).toLocaleString('ru-RU')} ₽`;
}

function formatBasePrice(car, currency) {
  if (currency === 'KRW') {
    return car.price_krw ? `${Math.round(car.price_krw / 10000).toLocaleString('ru-RU')} 만₩` : 'Цена по запросу';
  }
  const symbol = currency === 'EUR' ? '€' : '$';
  return car.price ? `${symbol}${Number(car.price).toLocaleString('ru-RU')}` : 'Цена по запросу';
}

function formatPower(car) {
  const hp = Number(car.power_hp || 0);
  const kw = Number(car.power_kw || 0);
  if (hp && kw) return `${hp} л.с. / ${kw} кВт`;
  if (hp) return `${hp} л.с.`;
  if (kw) return `${kw} кВт`;
  const value = String(car.power || '').trim();
  return value && !value.includes('?') ? value : 'уточняется';
}

function isElectricCar(car) {
  const fuel = String(car.fuel_type || car.fuel || car.engineType || car.engine_type || '').toLowerCase();
  const model = [car.brand, car.model, car.full_title, car.title]
    .map((value) => String(value || '').toLowerCase())
    .join(' ');
  if (/электро|electric|전기/.test(fuel) && !/гибрид|hybrid|бензин|diesel|дизель/.test(fuel)) return true;
  return /(tesla|leaf|zoe|electric|mokka-e|corsa-e|e-niro|kona electric|ioniq electric|ev6|ev9|id\.[34567])/i.test(model);
}

function isBlockedGeorgia(car) {
  const text = `${car.status || ''} ${car.description || ''} ${car.full_title || ''} ${car.fullName || ''}`.toLowerCase();
  if (/в пути|on\s*the\s*way|ожидает|транзит|coming| onderweg/.test(text)) return true;
  if (car.in_transit || car.is_in_transit || car.status_id === 2) return true;
  return false;
}

function score(car, region) {
  const turnkey = Number(car.turnkey_price_rub || 0);
  const mileage = Number(car.mileage || 0);
  const year = Number(car.year || car.first_registration_year || 0);
  const regionBoost = region === 'Корея' ? -50000 : region === 'Грузия' ? -30000 : 0;
  return turnkey + mileage * 1.8 - (year - 2021) * 65000 + regionBoost;
}

function toOffer(car, source) {
  const images = imageList(car);
  const title = `${car.brand || ''} ${car.model || ''} ${car.year || car.first_registration_year || ''}`.trim();
  const engine = `${car.engine || ''}${car.fuel_type ? ` ${car.fuel_type}` : ''}`.trim() || 'уточняется';
  const power = formatPower(car);
  const mileage = car.mileage ? `${Number(car.mileage).toLocaleString('ru-RU')} км` : 'уточняется';
  const turnkey = formatRub(car.turnkey_price_rub);
  const base = formatBasePrice(car, source.currency);
  const facts = [
    'проходной возраст 3-5 лет',
    'до 160 л.с. / 116 кВт',
    `под ключ в РФ: ${turnkey}`,
  ];
  if (source.region === 'Европа') facts.push('доставка 3000 € включена');
  if (source.region === 'Корея') facts.push('Encar, доставка 3000 € включена');

  return {
    channel: source.channel,
    region: source.region,
    source: source.source,
    source_type: 'catalog_best_turnkey',
    source_url: car.url || car.link || '',
    title,
    year: String(car.year || car.first_registration_year || ''),
    price: turnkey,
    base_price: base,
    image: images[0],
    images,
    details: { engine, power, mileage },
    text_excerpt: `${title}: выгодное проходное предложение ${source.region}, база ${base}, расчёт под ключ в РФ ${turnkey}.`,
    facts,
    score: Math.round(10000000 - score(car, source.region)),
    quality: 'turnkey_catalog',
    telegram_post: `🔥 ${title}\n\n📍 Направление: ${source.region}\n💰 Под ключ в РФ: ${turnkey}\nБазовая цена: ${base}\n⚙️ Двигатель: ${engine}\n🐎 Мощность: ${power}\n🛣️ Пробег: ${mileage}\n\n${facts.map((fact) => `• ${fact}`).join('\n')}\n\n📲 Напишите менеджеру: https://wa.me/996755666805\nИсточник: ${source.source}`,
  };
}

const offers = [];
for (const source of SOURCES) {
  const cars = JSON.parse(await fs.readFile(path.join(rootDir, source.file), 'utf8'));
  const filtered = cars
    .filter((car) => car.turnkey_calculation_complete && car.turnkey_price_rub && imageList(car).length)
    .filter((car) => !isElectricCar(car))
    .filter((car) => source.region !== 'Грузия' || !isBlockedGeorgia(car))
    .sort((a, b) => score(a, source.region) - score(b, source.region))
    .slice(0, source.region === 'Корея' ? 12 : 8)
    .map((car) => toOffer(car, source));
  offers.push(...filtered);
}

const diversified = [];
const seenModels = new Set();
for (const offer of offers.sort((a, b) => b.score - a.score)) {
  const key = `${offer.region}:${offer.title.replace(/\s+20\d{2}$/, '').toLowerCase()}`;
  if (seenModels.has(key) && diversified.length < 8) continue;
  seenModels.add(key);
  diversified.push(offer);
  if (diversified.length >= 8) break;
}

const payload = {
  generated_at: new Date().toISOString(),
  source_count: SOURCES.length,
  parsed_posts: 0,
  displayed_count: diversified.length,
  errors: [],
  offers: diversified,
};

await fs.writeFile(path.join(rootDir, 'data', 'telegram_top_offers.json'), `${JSON.stringify(payload, null, 2)}\n`, 'utf8');
await fs.writeFile(
  path.join(rootDir, 'data', 'telegram_top_posts.md'),
  `# Telegram top offers\n\nGenerated: ${payload.generated_at}\n\n${diversified.map((item, index) => `## ${index + 1}. ${item.title}\n\n${item.telegram_post}`).join('\n\n')}\n`,
  'utf8',
);

console.log(`Saved ${diversified.length} home top offers`);

