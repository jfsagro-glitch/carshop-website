const CBR_XML_URL = 'https://www.cbr.ru/scripts/XML_daily.asp';
const CBR_DAILY_JSON_MIRROR = 'https://www.cbr-xml-daily.ru/daily_json.js';

const REQUIRED_CODES = ['USD', 'EUR', 'CNY', 'KRW', 'JPY', 'GEL'];

export async function loadCbrRates() {
  try {
    const response = await fetch(CBR_XML_URL, { cache: 'no-store' });
    if (!response.ok) throw new Error(`CBR XML HTTP ${response.status}`);
    const buffer = await response.arrayBuffer();
    const text = new TextDecoder('windows-1251').decode(buffer);
    return parseCbrXml(text, 'cbr.ru');
  } catch (officialError) {
    const response = await fetch(CBR_DAILY_JSON_MIRROR, { cache: 'no-store' });
    if (!response.ok) throw new Error(`Не удалось загрузить курсы ЦБ: ${officialError.message}; mirror HTTP ${response.status}`);
    const payload = await response.json();
    return parseCbrDailyJson(payload, 'cbr-xml-daily.ru');
  }
}

export function parseCbrXml(xmlText, source = 'cbr.ru') {
  const doc = new DOMParser().parseFromString(xmlText, 'application/xml');
  const root = doc.querySelector('ValCurs');
  const rates = { RUB: 1 };
  REQUIRED_CODES.forEach((code) => {
    const node = Array.from(doc.querySelectorAll('Valute')).find((item) => item.querySelector('CharCode')?.textContent === code);
    if (!node) throw new Error(`В ответе ЦБ нет курса ${code}`);
    rates[code] = parseCbrNumber(node.querySelector('VunitRate')?.textContent || node.querySelector('Value')?.textContent);
  });
  return {
    rates,
    date: root?.getAttribute('Date') || '',
    source,
  };
}

export function parseCbrDailyJson(payload, source = 'cbr-xml-daily.ru') {
  const rates = { RUB: 1 };
  REQUIRED_CODES.forEach((code) => {
    const row = payload.Valute?.[code];
    if (!row || !Number.isFinite(Number(row.Value))) {
      throw new Error(`В daily_json нет курса ${code}`);
    }
    rates[code] = Number(row.Value) / Number(row.Nominal || 1);
  });
  return {
    rates,
    date: payload.Date ? new Date(payload.Date).toLocaleDateString('ru-RU') : '',
    source,
  };
}

function parseCbrNumber(value) {
  const n = Number(String(value || '').replace(',', '.'));
  if (!Number.isFinite(n) || n <= 0) {
    throw new Error(`Некорректный курс ЦБ: ${value}`);
  }
  return n;
}
