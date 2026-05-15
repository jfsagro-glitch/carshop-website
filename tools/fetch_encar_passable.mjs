import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');
const outPath = path.join(rootDir, 'cars_korea_stock.json');
const passableFilterPath = path.join(rootDir, 'data', 'passable_import_filter.json');
const API = 'https://api.encar.com/search/car/list/premium';

const KOREA_RULES = [
  ['Hyundai', 'Avante', '1.6', 'Бензин', 123, 90, ['아반떼']],
  ['Hyundai', 'Elantra', '1.6', 'Бензин', 123, 90, ['엘란트라']],
  ['Hyundai', 'Casper', '1.0', 'Бензин', 76, 56, ['캐스퍼']],
  ['Hyundai', 'Kona', '2.0', 'Бензин', 149, 110, ['코나']],
  ['Hyundai', 'Kona', '1.6', 'Гибрид', 105, 77, ['코나']],
  ['Hyundai', 'Sonata', '2.0', 'Бензин', 160, 116, ['쏘나타']],
  ['Hyundai', 'Venue', '1.6', 'Бензин', 123, 90, ['베뉴']],
  ['KIA', 'K3', '1.6', 'Бензин', 123, 90, ['k3', '케이3']],
  ['KIA', 'K5', '2.0', 'Бензин', 160, 116, ['k5', '케이5']],
  ['KIA', 'Morning', '1.0', 'Бензин', 76, 56, ['모닝']],
  ['KIA', 'Ray', '1.0', 'Бензин', 76, 56, ['레이']],
  ['KIA', 'Seltos', '1.6', 'Бензин', 123, 90, ['셀토스']],
  ['KIA', 'Stonic', '1.0', 'Бензин', 100, 74, ['스토닉']],
  ['KIA', 'Niro', '1.6', 'Гибрид', 105, 77, ['니로']],
  ['Renault Samsung', 'XM3', '1.3', 'Бензин', 152, 112, ['xm3']],
  ['Renault Samsung', 'XM3', '1.6', 'Бензин', 123, 90, ['xm3']],
  ['Renault Samsung', 'SM6', '1.3', 'Бензин', 152, 112, ['sm6']],
  ['Renault Samsung', 'QM6', '2.0', 'Газ/Бензин', 144, 106, ['qm6']],
  ['Chevrolet', 'Spark', '1.0', 'Бензин', 75, 55, ['스파크']],
  ['Chevrolet', 'Trax', '1.4', 'Бензин', 140, 103, ['트랙스']],
  ['Chevrolet', 'Trailblazer', '1.35', 'Бензин', 156, 115, ['트레일블레이저']],
  ['SsangYong', 'Tivoli', '1.6', 'Дизель', 136, 100, ['티볼리']],
  ['SsangYong', 'Korando', '1.6', 'Дизель', 136, 100, ['코란도']],
];

const MANUFACTURERS = {
  현대: 'Hyundai',
  기아: 'KIA',
  쉐보레: 'Chevrolet',
  '쉐보레(GM대우)': 'Chevrolet',
  르노코리아: 'Renault Samsung',
  르노삼성: 'Renault Samsung',
  '르노코리아(삼성)': 'Renault Samsung',
  쌍용: 'SsangYong',
  KG모빌리티: 'SsangYong',
  'KG모빌리티(쌍용)': 'SsangYong',
  BMW: 'BMW',
  벤츠: 'Mercedes-Benz',
  '벤츠 마이바흐': 'Mercedes-Benz',
  아우디: 'Audi',
  폭스바겐: 'Volkswagen',
  미니: 'Mini',
  볼보: 'Volvo',
  푸조: 'Peugeot',
  시트로엥: 'Citroen',
  포드: 'Ford',
  지프: 'Jeep',
  랜드로버: 'Land Rover',
  포르쉐: 'Porsche',
};

const ENCAR_EUROPE_RULES = [
  ['BMW', '116', '1.5', 'Бензин', 109, 80, ['1시리즈', '116i']],
  ['BMW', '118', '1.5', 'Бензин', 136, 100, ['1시리즈', '118i']],
  ['BMW', '118', '2.0', 'Дизель', 150, 110, ['1시리즈', '118d']],
  ['Mini', 'Cooper', '1.5', 'Бензин', 136, 100, ['쿠퍼']],
  ['Mini', 'Countryman', '1.5', 'Бензин', 136, 100, ['컨트리맨']],
  ['Volkswagen', 'Golf', '1.5', 'Бензин', 150, 110, ['골프', '1.5']],
  ['Volkswagen', 'Golf', '1.0', 'Бензин', 110, 81, ['골프', '1.0']],
  ['Volkswagen', 'Polo', '1.0', 'Бензин', 95, 70, ['폴로']],
  ['Volkswagen', 'Tiguan', '1.5', 'Бензин', 150, 110, ['티구안', '1.5']],
  ['Volkswagen', 'Tiguan', '2.0', 'Дизель', 150, 110, ['티구안', '2.0 tdi']],
  ['Audi', 'A3', '1.0', 'Бензин', 110, 81, ['a3', '30 tfsi']],
  ['Audi', 'Q2', '1.5', 'Бензин', 150, 110, ['q2', '35 tfsi']],
  ['Mercedes-Benz', 'A 180', '1.3', 'Бензин', 136, 100, ['a-클래스', 'a180']],
  ['Mercedes-Benz', 'B 180', '1.3', 'Бензин', 136, 100, ['b-클래스', 'b180']],
  ['Volvo', 'XC40', '1.5', 'Бензин', 129, 95, ['xc40']],
  ['Peugeot', '2008', '1.2', 'Бензин', 130, 96, ['2008']],
  ['Peugeot', '3008', '1.2', 'Бензин', 130, 96, ['3008']],
  ['Citroen', 'C3', '1.2', 'Бензин', 82, 60, ['c3']],
  ['Citroen', 'C4', '1.2', 'Бензин', 131, 96, ['c4']],
  ['Ford', 'Focus', '1.0', 'Бензин', 125, 92, ['포커스']],
];

function norm(value) {
  return String(value || '').toLowerCase().replace(/[^a-zа-я0-9가-힣]+/g, '');
}

function parseEngine(text) {
  const normalized = String(text || '').replace(',', '.');
  const match = normalized.match(/(\d+(?:\.\d+)?)/);
  return match ? match[1] : '';
}

function mapFuel(text) {
  const value = String(text || '').toLowerCase();
  if (value.includes('디젤')) return 'Дизель';
  if (value.includes('하이브리드')) return 'Гибрид';
  if (value.includes('전기')) return 'Электро';
  if (value.includes('lpg')) return 'Газ/Бензин';
  return 'Бензин';
}

function isElectricFuel(value) {
  const text = String(value || '').toLowerCase();
  return /электро|electric|전기|(tesla|leaf|zoe|electric|mokka-e|corsa-e|e-niro|kona electric|ioniq electric|ev6|ev9|id\.[34567])/i.test(text);
}

function findKoreaRule(row) {
  const text = norm(`${row.Model || ''} ${row.Badge || ''} ${row.BadgeDetail || ''}`);
  const fuel = mapFuel(`${row.FuelType || ''} ${row.Badge || ''}`);
  if (isElectricFuel(fuel) || isElectricFuel(`${row.FuelType || ''} ${row.Badge || ''}`)) return null;
  const engine = parseEngine(`${row.Badge || ''} ${row.BadgeDetail || ''}`);
  return KOREA_RULES.find(([brand, , ruleEngine, ruleFuel, , , aliases]) => {
    if (brand !== (MANUFACTURERS[row.Manufacturer] || row.Manufacturer)) return false;
    if (!aliases.some((alias) => text.includes(norm(alias)))) return false;
    if (ruleFuel !== fuel && !(ruleFuel === 'Газ/Бензин' && fuel === 'Бензин')) return false;
    return !engine || Math.abs(Number(engine) - Number(ruleEngine)) <= 0.16;
  });
}

function findEuropeRule(row, whitelist) {
  const brand = MANUFACTURERS[row.Manufacturer] || row.Manufacturer;
  const rowText = norm(`${row.Model || ''} ${row.Badge || ''} ${row.BadgeDetail || ''}`);
  const engine = parseEngine(`${row.Badge || ''} ${row.BadgeDetail || ''}`);
  const fuel = mapFuel(`${row.FuelType || ''} ${row.Badge || ''}`);
  if (isElectricFuel(fuel) || isElectricFuel(`${row.FuelType || ''} ${row.Badge || ''}`)) return null;
  const direct = ENCAR_EUROPE_RULES.find(([ruleBrand, , ruleEngine, ruleFuel, , , aliases]) => {
    if (norm(ruleBrand) !== norm(brand)) return false;
    if (!aliases.every((alias) => rowText.includes(norm(alias)))) return false;
    if (ruleFuel !== fuel && !(ruleFuel === 'Бензин' && fuel === 'Газ/Бензин')) return false;
    return !engine || Math.abs(Number(engine) - Number(ruleEngine)) <= 0.16;
  });
  if (direct) {
    return {
      regions: ['europe'],
      brand: direct[0],
      model: direct[1],
      engine: direct[2],
      fuel: direct[3],
      hp: direct[4],
      kw: direct[5],
    };
  }
  return whitelist.find((rule) => {
    if (!rule.regions?.includes('europe')) return false;
    if (norm(rule.brand) !== norm(brand)) return false;
    if (!rowText.includes(norm(rule.model))) return false;
    if (rule.fuel && fuel !== rule.fuel && !(rule.fuel === 'Бензин' && fuel === 'Газ/Бензин')) return false;
    return !engine || Math.abs(Number(engine) - Number(rule.engine)) <= 0.16;
  });
}

function photoUrls(row) {
  const photos = Array.isArray(row.Photos) ? row.Photos : [];
  return photos
    .sort((a, b) => Number(a.ordering || 0) - Number(b.ordering || 0))
    .map((photo) => photo.location ? `https://ci.encar.com${photo.location}` : '')
    .filter(Boolean)
    .slice(0, 12);
}

function transform(row, rule) {
  const yearMonth = Number(row.Year || 0);
  const year = Math.floor(yearMonth / 100);
  const month = Math.round(yearMonth % 100);
  const priceKrw = Math.round(Number(row.Price || 0) * 10000);
  return {
    id: String(row.Id),
    brand: rule.brand,
    model: rule.model,
    full_title: `${row.Manufacturer || ''} ${row.Model || ''} ${row.Badge || ''}`.trim(),
    year,
    month,
    productionDate: `${String(month).padStart(2, '0')}.${year}`,
    price: Math.round(priceKrw * 0.00073),
    price_krw: priceKrw,
    price_type: 'fixed',
    mileage: Math.round(Number(row.Mileage || 0)),
    engine: rule.engine,
    fuel_type: rule.fuel,
    transmission: String(row.Transmission || '').includes('오토') ? 'Автомат' : 'Механика',
    color: '',
    drive: '',
    url: `https://www.encar.com/dc/dc_cardetailview.do?carid=${row.Id}`,
    images: photoUrls(row),
    region: 'korea',
    source: 'encar',
    power_hp: rule.hp,
    power_kw: rule.kw,
    power: `${rule.hp} л.с. / ${rule.kw} кВт`,
    power_source: rule.source,
    regionCode: 'korea',
  };
}

async function fetchBatch(carType, offset, limit = 100) {
  const q = `(And.Hidden.N._.CarType.${carType}._.Year.range(202105..202305)._.Mileage.range(0..100000).)`;
  const url = `${API}?count=true&q=${encodeURIComponent(q)}&sr=%7CModifiedDate%7C${offset}%7C${limit}`;
  const response = await fetch(url, {
    headers: { accept: 'application/json', 'user-agent': 'Mozilla/5.0' },
  });
  if (!response.ok) throw new Error(`Encar API failed: ${response.status}`);
  return response.json();
}

const passableFilter = JSON.parse(await fs.readFile(passableFilterPath, 'utf8'));
const whitelist = passableFilter.vehicle_whitelist || [];
const rows = [];
for (const carType of ['Y', 'N']) {
  for (let offset = 0; offset < 1200; offset += 100) {
    const payload = await fetchBatch(carType, offset, 100);
    rows.push(...(payload.SearchResults || []));
  }
}

const seen = new Set();
const cars = [];
for (const row of rows) {
  const koreanRule = findKoreaRule(row);
  const europeRule = !koreanRule ? findEuropeRule(row, whitelist) : null;
  const sourceRule = koreanRule
    ? {
      brand: koreanRule[0],
      model: koreanRule[1],
      engine: koreanRule[2],
      fuel: koreanRule[3],
      hp: koreanRule[4],
      kw: koreanRule[5],
      source: 'catalog:korea',
    }
    : europeRule
      ? { ...europeRule, hp: europeRule.hp, kw: europeRule.kw, source: 'catalog:europe-passable' }
      : null;
  if (!sourceRule || seen.has(String(row.Id))) continue;
  const images = photoUrls(row);
  if (!images.length) continue;
  const car = transform(row, sourceRule);
  if (!car.year || !car.month || !car.price_krw || !car.power_hp || car.power_hp > 160) continue;
  seen.add(String(row.Id));
  cars.push(car);
}

cars.sort((a, b) => (a.price_krw - b.price_krw) || (a.mileage - b.mileage));
await fs.writeFile(outPath, `${JSON.stringify(cars.slice(0, 300), null, 2)}\n`, 'utf8');
console.log(`Fetched ${rows.length} Encar rows`);
console.log(`Matched brands: ${Array.from(new Set(cars.map((car) => car.brand))).sort().join(', ')}`);
console.log(`Saved ${Math.min(cars.length, 300)} passable cars -> cars_korea_stock.json`);

