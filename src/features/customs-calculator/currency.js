import { DEFAULT_CURRENCY_RATES_RUB } from './customsRates.js';

export function normalizeRates(manualRates = {}) {
  return { ...DEFAULT_CURRENCY_RATES_RUB, ...manualRates, RUB: 1 };
}

export function getRateToRub(currency, manualRates = {}) {
  const rates = normalizeRates(manualRates);
  const rate = Number(rates[currency]);
  if (!Number.isFinite(rate) || rate <= 0) {
    throw new Error(`Курс ${currency} должен быть больше 0`);
  }
  return rate;
}

export function calculateCustomsValueRub(input) {
  const price = Number(input.price || 0);
  const delivery = Number(input.deliveryToBorder || 0);
  const insurance = Number(input.insuranceToBorder || 0);
  const rate = getRateToRub(input.currency, input.manualRates);
  return roundMoney((price + delivery + insurance) * rate);
}

export function calculateCustomsValueEur(customsValueRub, manualRates = {}) {
  const eurRub = getRateToRub('EUR', manualRates);
  return roundMoney(customsValueRub / eurRub);
}

export function roundMoney(value) {
  return Math.round((Number(value) || 0) * 100) / 100;
}

export function formatRub(value) {
  return `${Math.round(Number(value) || 0).toLocaleString('ru-RU')} ₽`;
}

export function formatEur(value) {
  return `${(Number(value) || 0).toLocaleString('ru-RU', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })} €`;
}
