const CBR_XML_URL = 'https://www.cbr.ru/scripts/XML_daily.asp';
const CBR_DAILY_JSON_MIRROR = 'https://www.cbr-xml-daily.ru/daily_json.js';
const REQUIRED_CODES = ['USD', 'EUR', 'CNY', 'KRW', 'JPY', 'GEL'];

const wait = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));

function readTag(xml, tagName) {
  const match = xml.match(new RegExp(`<${tagName}>([\\s\\S]*?)<\\/${tagName}>`, 'i'));
  return match ? match[1].trim() : '';
}

function validateRates(rates) {
  const missing = REQUIRED_CODES.filter((code) => !Number.isFinite(Number(rates[code])) || Number(rates[code]) <= 0);
  if (missing.length) throw new Error(`Missing CBR rates: ${missing.join(', ')}`);
  return rates;
}

function parseCbrXml(xml, fallbackDate) {
  const rates = { RUB: 1 };
  const dateMatch = xml.match(/<ValCurs[^>]*Date="([^"]+)"/i);
  const valuteBlocks = xml.match(/<Valute[\s\S]*?<\/Valute>/g) || [];
  for (const block of valuteBlocks) {
    const code = readTag(block, 'CharCode');
    if (!REQUIRED_CODES.includes(code)) continue;
    const nominal = Number(readTag(block, 'Nominal').replace(',', '.')) || 1;
    const value = Number(readTag(block, 'VunitRate').replace(',', '.')) || Number(readTag(block, 'Value').replace(',', '.'));
    if (Number.isFinite(value) && value > 0) rates[code] = value / nominal;
  }
  return { rates: validateRates(rates), cbrDate: dateMatch?.[1] || fallbackDate, source: 'cbr.ru' };
}

function parseDailyJson(payload, fallbackDate) {
  const rates = { RUB: 1 };
  for (const code of REQUIRED_CODES) {
    const row = payload.Valute?.[code];
    const value = Number(row?.Value);
    const nominal = Number(row?.Nominal || 1);
    if (Number.isFinite(value) && value > 0 && Number.isFinite(nominal) && nominal > 0) rates[code] = value / nominal;
  }
  const cbrDate = payload.Date ? new Date(payload.Date).toLocaleDateString('ru-RU') : fallbackDate;
  return { rates: validateRates(rates), cbrDate, source: 'cbr-xml-daily.ru' };
}

async function fetchWithTimeout(url, timeoutMs = 15000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(url, { cache: 'no-store', signal: controller.signal });
    if (!response.ok) throw new Error(`HTTP ${response.status} ${response.statusText}`);
    return response;
  } finally {
    clearTimeout(timer);
  }
}

function cachedRatesFromCars(cars) {
  for (const car of cars || []) {
    if (!car?.turnkey_rates) continue;
    try {
      return {
        rates: validateRates({ RUB: 1, ...car.turnkey_rates }),
        cbrDate: car.turnkey_rates_cbr_date || car.turnkey_calculation_date || 'previous successful update',
        source: 'previous-successful-catalog-update',
      };
    } catch {
      // Try the next catalog entry with saved rates.
    }
  }
  return null;
}

export async function loadResilientCbrRates({ fallbackDate, cachedCars = [] } = {}) {
  const errors = [];
  for (let attempt = 1; attempt <= 3; attempt += 1) {
    try {
      const response = await fetchWithTimeout(CBR_XML_URL);
      const result = parseCbrXml(await response.text(), fallbackDate);
      console.log(`CBR rates loaded from ${result.source} on attempt ${attempt}.`);
      return result;
    } catch (error) {
      errors.push(`cbr.ru attempt ${attempt}: ${error.message}`);
      if (attempt < 3) await wait(attempt * 1500);
    }
  }
  for (let attempt = 1; attempt <= 2; attempt += 1) {
    try {
      const response = await fetchWithTimeout(CBR_DAILY_JSON_MIRROR);
      const result = parseDailyJson(await response.json(), fallbackDate);
      console.log(`CBR rates loaded from ${result.source} on mirror attempt ${attempt}.`);
      return result;
    } catch (error) {
      errors.push(`mirror attempt ${attempt}: ${error.message}`);
      if (attempt < 2) await wait(attempt * 1500);
    }
  }
  const cached = cachedRatesFromCars(cachedCars);
  if (cached) {
    console.warn(`CBR endpoints are temporarily unavailable; using ${cached.source} (${cached.cbrDate}).`);
    return cached;
  }
  throw new Error(`Unable to load CBR rates after retries: ${errors.join('; ')}`);
}
