import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { calculateCustoms } from '../src/features/customs-calculator/customsCalculator.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');
const stockPath = path.join(rootDir, 'cars_georgia_stock.json');
const calculationDate = new Date().toISOString().slice(0, 10);

const CBR_URL = 'https://www.cbr.ru/scripts/XML_daily.asp';
const REQUIRED_CODES = ['USD', 'EUR', 'CNY', 'KRW', 'JPY', 'GEL'];

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
    if (Number.isFinite(value) && value > 0) {
      rates[code] = value / nominal;
    }
  }

  const missing = REQUIRED_CODES.filter((code) => !rates[code]);
  if (missing.length) {
    throw new Error(`CBR response is missing rates: ${missing.join(', ')}`);
  }

  return { rates, cbrDate };
}

function readTag(xml, tagName) {
  const match = xml.match(new RegExp(`<${tagName}>([\\s\\S]*?)<\\/${tagName}>`, 'i'));
  return match ? match[1].trim() : '';
}

async function loadCbrRates() {
  const response = await fetch(CBR_URL, { cache: 'no-store' });
  if (!response.ok) {
    throw new Error(`CBR request failed: ${response.status} ${response.statusText}`);
  }
  const xml = await response.text();
  return parseCbrXml(xml);
}

function parseEngineCc(engine) {
  const text = String(engine || '').replace(',', '.');
  const liters = Number((text.match(/\d+(?:\.\d+)?/) || [])[0]);
  if (!Number.isFinite(liters) || liters <= 0) return undefined;
  return Math.round(liters * 1000);
}

function mapEngineType(car) {
  const fuel = String(car.fuel_type || car.fuel || '').toLowerCase();
  if (fuel.includes('электро')) return 'electric';
  if (fuel.includes('гибрид') && fuel.includes('диз')) return 'diesel_hybrid';
  if (fuel.includes('гибрид')) return 'petrol_hybrid';
  if (fuel.includes('диз')) return 'diesel';
  return 'petrol';
}

function isElectricCar(car) {
  const fuel = String(car.fuel_type || car.fuel || car.engineType || car.engine_type || '').toLowerCase();
  const model = [car.brand, car.model, car.fullName, car.full_title, car.title]
    .map((value) => String(value || '').toLowerCase())
    .join(' ');
  if (/электро|electric|전기/.test(fuel) && !/гибрид|hybrid|бензин|diesel|дизель/.test(fuel)) return true;
  return /(tesla|leaf|zoe|electric|mokka-e|corsa-e|e-niro|kona electric|ioniq electric|ev6|ev9|id\.[34567])/i.test(model);
}

function buildManufactureFields(car) {
  const year = Number(car.year);
  const month = Number(car.month);
  if (year && month >= 1 && month <= 12) {
    return {
      manufactureYear: year,
      manufactureMonth: `${year}-${String(month).padStart(2, '0')}`,
    };
  }
  if (year) {
    return { manufactureYear: year };
  }
  return {};
}

function roundRub(value) {
  return Math.round(Number(value) || 0);
}

function summarizeResult(result) {
  return {
    turnkey_price_rub: roundRub(result.totalWithCarRub),
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

function buildCalculatorInput(car, rates) {
  const engineType = mapEngineType(car);
  return {
    vehicleType: 'passenger_car',
    importerType: engineType === 'electric' ? 'legal_stp' : 'physical_ets',
    price: Number(car.price || 0),
    currency: car.price_currency || car.currency || 'USD',
    deliveryToBorder: 0,
    insuranceToBorder: 0,
    engineCc: engineType === 'electric' ? undefined : parseEngineCc(car.engine),
    powerValue: Number(car.power_hp || car.hp || 0),
    powerUnit: 'hp',
    engineType,
    ...buildManufactureFields(car),
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

const { rates, cbrDate } = await loadCbrRates();
const cars = JSON.parse(await fs.readFile(stockPath, 'utf8'));
const sourceCars = cars.filter((car) => !isElectricCar(car));
let completeCount = 0;

const updated = sourceCars.map((car) => {
  const result = calculateCustoms(buildCalculatorInput(car, rates));
  if (result.isComplete) completeCount += 1;
  return {
    ...car,
    ...summarizeResult(result),
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

await fs.writeFile(stockPath, `${JSON.stringify(updated, null, 2)}\n`, 'utf8');

console.log(`Updated ${updated.length} Georgia cars`);
console.log(`Removed electric cars: ${cars.length - sourceCars.length}`);
console.log(`Complete calculations: ${completeCount}/${updated.length}`);
console.log(`CBR date: ${cbrDate}`);
console.log(`Rates: USD ${rates.USD.toFixed(4)}, EUR ${rates.EUR.toFixed(4)}, GEL ${rates.GEL.toFixed(4)}`);

