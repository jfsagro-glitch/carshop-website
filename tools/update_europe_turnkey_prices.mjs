import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { calculateCustoms } from '../src/features/customs-calculator/customsCalculator.js';
import { resolveAgeBand } from '../src/features/customs-calculator/age.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');
const stockPath = path.join(rootDir, 'cars_europe_new.json');
const passableFilterPath = path.join(rootDir, 'data', 'passable_import_filter.json');
const calculationDate = new Date().toISOString().slice(0, 10);

const CBR_URL = 'https://www.cbr.ru/scripts/XML_daily.asp';
const REQUIRED_CODES = ['USD', 'EUR', 'CNY', 'KRW', 'JPY', 'GEL'];
const EUROPE_ROAD_EUR = 3000;

function readTag(xml, tagName) {
  const match = xml.match(new RegExp(`<${tagName}>([\\s\\S]*?)<\\/${tagName}>`, 'i'));
  return match ? match[1].trim() : '';
}

function parseCbrXml(xml) {
  const rates = { RUB: 1 };
  const dateMatch = xml.match(/<ValCurs[^>]*Date="([^"]+)"/i);
  const cbrDate = dateMatch ? dateMatch[1] : calculationDate;
  const valuteBlocks = xml.match(/<Valute[\s\S]*?<\/Valute>/g) || [];

  for (const block of valuteBlocks) {
    const code = readTag(block, 'CharCode');
    if (!REQUIRED_CODES.includes(code)) continue;
    const nominal = Number(readTag(block, 'Nominal').replace(',', '.')) || 1;
    const value = Number(readTag(block, 'Value').replace(',', '.'));
    if (Number.isFinite(value) && value > 0) rates[code] = value / nominal;
  }

  const missing = REQUIRED_CODES.filter((code) => !rates[code]);
  if (missing.length) throw new Error(`CBR response is missing rates: ${missing.join(', ')}`);
  return { rates, cbrDate };
}

async function loadCbrRates() {
  const response = await fetch(CBR_URL, { cache: 'no-store' });
  if (!response.ok) throw new Error(`CBR request failed: ${response.status} ${response.statusText}`);
  return parseCbrXml(await response.text());
}

function normalizeText(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/ё/g, 'е')
    .replace(/[^a-zа-я0-9]/g, '');
}

function normalizeBrand(value) {
  const brand = normalizeText(value);
  if (brand === 'mercedesbenz') return 'mercedesbenz';
  if (brand === 'vw') return 'volkswagen';
  return brand;
}

function fuelMatches(carFuel, ruleFuel) {
  const car = normalizeText(carFuel);
  const rule = normalizeText(ruleFuel);
  if (!car || !rule) return true;
  if (car.includes('elektrobenzin') && rule.includes('гибрид')) return true;
  if (car.includes('elektrodiesel') && rule.includes('гибрид')) return true;
  if (car.includes('autogas') && rule.includes('бензин')) return true;
  return car.includes(rule) || rule.includes(car);
}

function findWhitelistEngine(car, whitelist) {
  const carBrand = normalizeBrand(car.brand);
  const carModel = normalizeText(car.model);
  const carPower = Number(car.power_hp || 0);

  const candidates = whitelist
    .filter((rule) => rule.regions?.includes('europe'))
    .filter((rule) => normalizeBrand(rule.brand) === carBrand)
    .filter((rule) => {
      const ruleModel = normalizeText(rule.model);
      return carModel.startsWith(ruleModel) || ruleModel.startsWith(carModel);
    })
    .filter((rule) => !carPower || !rule.hp || Math.abs(carPower - Number(rule.hp)) <= 8)
    .filter((rule) => fuelMatches(car.fuel_type, rule.fuel));

  return candidates[0]?.engine;
}

function inferEngineLitersFromText(car) {
  const text = `${car.full_title || ''} ${car.model || ''}`.replace(',', '.');
  const fuelText = normalizeText(car.fuel_type || car.fuel);
  const decimal = text.match(/(?:^|[\s|/-])([0-3]\.\d)\s*(?:tsi|tdi|tfsi|tfsie|turbo|eb|gdi|hdi|bluehdi|dci|puretech|multijet|mpi|tce|cvt|hybrid|phev|benz|s&s|ss|aut|dsg|edc)?/i);
  if (decimal) return decimal[1];

  const lower = text.toLowerCase();
  if (/\b35\s*tdi\b/.test(lower)) return '2.0';
  if (/\b30\s*tdi\b/.test(lower)) return '2.0';
  if (/\b40\s*tdi\b/.test(lower)) return '2.0';
  if (/\b30\s*tfsi\b/.test(lower)) return '1.0';
  if (/\b35\s*tfsi\b/.test(lower)) return '1.5';
  if (/\b40\s*tfsi\b/.test(lower)) return '2.0';
  if (/\b45\s*tfsi\s*e\b/.test(lower)) return '1.4';
  if (/\b250\s*e\b/.test(lower) || /\ba\s*250\b/.test(lower)) return '1.3';
  if (/\b(?:sdrive\s*)?18\s*d\b/.test(lower) || /\b118d\b/.test(lower) || /\b116d\b/.test(lower) || /\b318d\b/.test(lower)) return '2.0';
  if (/\b(?:sdrive\s*)?18\s*i\b/.test(lower) || /\b116i\b/.test(lower) || /\b118i\b/.test(lower)) return '1.5';
  if (/\b318\b/.test(lower) && Number(car.power_hp || 0) <= 160) return '2.0';
  if (/\b114\s*cdi\b/.test(lower) || /\b116\s*cdi\b/.test(lower)) return '2.0';
  if (/\b(?:a|b|cla|gla|glb)\s*180(?:\s*d)?\b/.test(lower) && /диз|diesel/.test(fuelText)) return '1.95';
  if (/\b(?:a|b|cla|gla|glb)\s*180\b/.test(lower)) return '1.3';
  if (/\bpuretech\s*130\b/.test(lower) || /\b130\s*s&s\b/.test(lower)) return '1.2';
  if (/\btce\s*110\b/.test(lower)) return '1.0';
  if (/\btce\s*130\b/.test(lower) || /\btce\s*150\b/.test(lower)) return '1.3';
  if (/\b1\.0\s*eb\b/.test(lower) || /\bpuma\b/.test(lower) && Number(car.power_hp || 0) <= 160) return '1.0';
  if (/\btsi\b/.test(lower) && Number(car.power_hp || 0) <= 116) return '1.0';
  if (/\btsi\b/.test(lower) && Number(car.power_hp || 0) > 116) return '1.5';

  const brand = normalizeBrand(car.brand);
  const model = normalizeText(car.model);
  const power = Number(car.power_hp || 0);
  const fuel = normalizeText(car.fuel_type);
  if (brand === 'citroen' && fuel.includes('бензин') && power >= 120 && power <= 135) return '1.2';
  if (brand === 'peugeot' && fuel.includes('бензин') && power >= 120 && power <= 135) return '1.2';
  if (brand === 'opel' && fuel.includes('бензин') && power >= 100 && power <= 131) return '1.2';
  if (brand === 'volkswagen' && model.includes('crafter')) return '2.0';
  if (brand === 'mercedesbenz' && model.includes('vito')) return '2.0';

  return '';
}

function parseEngineCc(car, whitelist) {
  const exactCc = Number(car.engine_cc || car.engine_displacement_cc || 0);
  if (
    Number.isFinite(exactCc)
    && exactCc >= 500
    && exactCc <= 10000
    && String(car.engine_source || '').startsWith('autoscout24_')
  ) {
    return Math.round(exactCc);
  }
  const sourceText = `${car.source || ''} ${car.url || ''}`.toLowerCase();
  if (sourceText.includes('autoscout24')) return undefined;

  const inferredEngine = inferEngineLitersFromText(car);
  const isMercedes180Diesel = inferredEngine === '1.95'
    && normalizeBrand(car.brand) === 'mercedesbenz';
  const engine = isMercedes180Diesel
    ? inferredEngine
    : car.engine || findWhitelistEngine(car, whitelist) || inferredEngine;
  const liters = Number(String(engine || '').replace(',', '.').match(/\d+(?:\.\d+)?/)?.[0]);
  if (!Number.isFinite(liters) || liters <= 0) return undefined;
  return Math.round(liters * 1000);
}

function mapEngineType(car) {
  const fuel = String(car.fuel_type || '').toLowerCase();
  if (fuel.includes('электро') || fuel.includes('elektro') && !fuel.includes('benzin') && !fuel.includes('diesel')) {
    return 'electric';
  }
  if (fuel.includes('diesel') && fuel.includes('elektro')) return 'diesel_hybrid';
  if (fuel.includes('гибрид') || fuel.includes('hybrid') || fuel.includes('benzin') && fuel.includes('elektro')) return 'petrol_hybrid';
  if (fuel.includes('диз') || fuel.includes('diesel')) return 'diesel';
  return 'petrol';
}

function isElectricCar(car) {
  const fuel = String(car.fuel_type || car.fuel || car.engineType || car.engine_type || '').toLowerCase();
  const model = [car.brand, car.model, car.full_title, car.title]
    .map((value) => String(value || '').toLowerCase())
    .join(' ');
  if (/электро|electric|전기/.test(fuel) && !/гибрид|hybrid|бензин|diesel|дизель/.test(fuel)) return true;
  return /(tesla|leaf|zoe|electric|mokka-e|corsa-e|e-niro|kona electric|ioniq electric|ev6|ev9|id\.[34567])/i.test(model);
}

function manufactureFields(car) {
  const firstRegistration = String(car.first_registration || '');
  const monthYear = firstRegistration.match(/^(\d{1,2})\/(\d{4})$/);
  if (monthYear) {
    const month = Number(monthYear[1]);
    const year = Number(monthYear[2]);
    return {
      manufactureYear: year,
      manufactureMonth: `${year}-${String(month).padStart(2, '0')}`,
    };
  }
  const year = Number(car.year || car.first_registration_year);
  return year ? { manufactureYear: year } : {};
}

function roundRub(value) {
  return Math.round(Number(value) || 0);
}

function summarize(result) {
  const totalWithCarRub = roundRub(result.totalWithCarRub);
  const complete = Boolean(result.isComplete);
  return {
    turnkey_price_rub: complete ? totalWithCarRub : null,
    turnkey_partial_price_rub: complete ? null : totalWithCarRub,
    turnkey_payments_rub: roundRub(result.totalPaymentsRub),
    customs_value_rub: roundRub(result.customsValueRub),
    customs_value_eur: Number((result.customsValueEur || 0).toFixed(2)),
    customs_fee_rub: roundRub(result.customsFeeRub),
    customs_duty_rub: roundRub(result.dutyRub),
    customs_duty_eur: Number((result.dutyEur || 0).toFixed(2)),
    excise_rub: roundRub(result.exciseRub),
    vat_rub: roundRub(result.vatRub),
    recycling_fee_rub: roundRub(result.recyclingFeeRub),
    additional_costs_rub: roundRub(result.additionalCostsRub),
    georgia_conversion_fee_rub: roundRub(result.georgiaConversionFeeRub),
    turnkey_calculation_complete: Boolean(result.isComplete),
    turnkey_calculation_warnings: result.warnings || [],
    turnkey_calculation_errors: result.errors || [],
  };
}

function buildInput(car, rates, whitelist) {
  const engineType = mapEngineType(car);
  return {
    vehicleType: 'passenger_car',
    importerType: engineType === 'electric' ? 'legal_stp' : 'physical_ets',
    price: Number(car.price || 0),
    currency: 'EUR',
    deliveryToBorder: EUROPE_ROAD_EUR,
    insuranceToBorder: 0,
    engineCc: engineType === 'electric' ? undefined : parseEngineCc(car, whitelist),
    powerValue: Number(car.power_hp || 0),
    powerUnit: 'hp',
    engineType,
    ...manufactureFields(car),
    calculationDate,
    alreadyClearedInEaeu: false,
    recyclingFeeAlreadyPaid: false,
    personalUse: true,
    secondCarInYear: false,
    plannedSaleWithin12Months: false,
    manualRates: rates,
    ratesSource: 'cbr',
    importSource: 'georgia',
  };
}

const [{ rates, cbrDate }, cars, passableFilter] = await Promise.all([
  loadCbrRates(),
  fs.readFile(stockPath, 'utf8').then(JSON.parse),
  fs.readFile(passableFilterPath, 'utf8').then(JSON.parse),
]);

const whitelist = passableFilter.vehicle_whitelist || [];
let completeCount = 0;

const sourceCars = cars.filter((car) => !isElectricCar(car));

const updated = sourceCars.map((car) => {
  const input = buildInput(car, rates, whitelist);
  const result = calculateCustoms(input);
  const ageBand = resolveAgeBand(input);
  const isAutoScout = `${car.source || ''} ${car.url || ''}`.toLowerCase().includes('autoscout24');
  if (result.isComplete) completeCount += 1;
  return {
    ...car,
    engine: input.engineCc
      ? (input.engineCc / 1000).toLocaleString('ru-RU', { maximumFractionDigits: 3 })
      : (isAutoScout ? '' : car.engine),
    engine_cc: input.engineCc || (isAutoScout ? null : car.engine_cc),
    engine_source: input.engineCc ? car.engine_source : (isAutoScout ? '' : car.engine_source),
    customs_age_band: ageBand,
    ...summarize(result),
    europe_road_eur: EUROPE_ROAD_EUR,
    turnkey_cost_profile: 'europe_plus_georgia_costs',
    turnkey_calculation_date: calculationDate,
    turnkey_rates_source: 'CBR',
    turnkey_rates_cbr_date: cbrDate,
    turnkey_rates: {
      USD: Number(rates.USD.toFixed(4)),
      EUR: Number(rates.EUR.toFixed(4)),
      GEL: Number(rates.GEL.toFixed(4)),
      CNY: Number(rates.CNY.toFixed(4)),
      KRW: Number(rates.KRW.toFixed(6)),
      JPY: Number(rates.JPY.toFixed(4)),
    },
  };
});

const published = updated.filter((car) => {
  const isAutoScout = `${car.source || ''} ${car.url || ''}`.toLowerCase().includes('autoscout24');
  const hasVerifiedEngine = !isAutoScout || (
    Number(car.engine_cc || 0) >= 500
    && String(car.engine_source || '').startsWith('autoscout24_')
  );
  return hasVerifiedEngine
    && car.turnkey_calculation_complete
    && Number(car.turnkey_price_rub || 0) > 0;
});
const removedIncomplete = updated.length - published.length;

await fs.writeFile(stockPath, `${JSON.stringify(published, null, 2)}\n`, 'utf8');

console.log(`Updated ${published.length} Europe cars`);
console.log(`Removed electric cars: ${cars.length - sourceCars.length}`);
console.log(`Removed without verified engine/turnkey price: ${removedIncomplete}`);
console.log(`Complete calculations: ${completeCount}/${updated.length}`);
console.log(`Road cost: ${EUROPE_ROAD_EUR} EUR`);
console.log(`CBR date: ${cbrDate}`);
console.log(`Rates: USD ${rates.USD.toFixed(4)}, EUR ${rates.EUR.toFixed(4)}, GEL ${rates.GEL.toFixed(4)}`);

