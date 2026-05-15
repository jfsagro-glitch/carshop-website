import test from 'node:test';
import assert from 'node:assert/strict';

import { getAgeBand, resolveManufactureDate } from '../age.js';
import {
  calculateCustoms,
  calculateCustomsFee,
  calculateExcise,
  calculateRecyclingFee,
} from '../customsCalculator.js';

const rates = { EUR: 100, USD: 90, CNY: 12.7, KRW: 0.067, JPY: 0.62, GEL: 34 };

function base(overrides = {}) {
  return {
    vehicleType: 'passenger_car',
    importerType: 'physical_ets',
    price: 15000,
    currency: 'EUR',
    deliveryToBorder: 0,
    insuranceToBorder: 0,
    engineCc: 1498,
    powerValue: 150,
    powerUnit: 'hp',
    engineType: 'petrol',
    ageBand: 'from_3_to_5',
    calculationDate: '2026-05-15',
    alreadyClearedInEaeu: false,
    recyclingFeeAlreadyPaid: false,
    personalUse: true,
    secondCarInYear: false,
    plannedSaleWithin12Months: false,
    manualRates: rates,
    ratesSource: 'cbr',
    ...overrides,
  };
}

test('physical ETS 3-5 years 1498 cc', () => {
  const result = calculateCustoms(base({ engineCc: 1498 }));
  assert.equal(result.dutyEur, 1498 * 1.7);
  assert.equal(result.exciseRub, 0);
  assert.equal(result.vatRub, 0);
});

test('physical ETS 3-5 years 1998 cc', () => {
  const result = calculateCustoms(base({ engineCc: 1998 }));
  assert.equal(result.dutyEur, 1998 * 2.7);
});

test('physical ETS older than 5 years 1998 cc', () => {
  const result = calculateCustoms(base({ engineCc: 1998, ageBand: 'from_5_to_7' }));
  assert.equal(result.dutyEur, 1998 * 4.8);
});

test('physical ETS under 3 max percent or cc minimum', () => {
  const result = calculateCustoms(base({ ageBand: 'under_3', price: 15000, engineCc: 1200 }));
  assert.equal(result.dutyEur, Math.max(15000 * 0.48, 1200 * 3.5));
});

test('customs clearance fee brackets', () => {
  assert.equal(calculateCustomsFee(199000), 1231);
  assert.equal(calculateCustomsFee(300000), 2462);
  assert.equal(calculateCustomsFee(6000000), 49240);
  assert.equal(calculateCustomsFee(11000000), 73860);
});

test('excise brackets', () => {
  assert.equal(calculateExcise(89), 0);
  assert.equal(calculateExcise(120), 120 * 64);
  assert.equal(calculateExcise(180), 180 * 613);
  assert.equal(calculateExcise(250), 250 * 1004);
});

test('personal recycling fee under 3 and older than 3', () => {
  const under3 = calculateRecyclingFee(base({
    ageBand: 'under_3',
    engineCc: 1998,
    powerValue: 150,
  }), 'under_3', 150);
  assert.equal(under3.valueRub, 3400);

  const older = calculateRecyclingFee(base({
    ageBand: 'from_3_to_5',
    engineCc: 1998,
    powerValue: 150,
  }), 'from_3_to_5', 150);
  assert.equal(older.valueRub, 5200);
});

test('increased recycling fee', () => {
  const fee = calculateRecyclingFee(base({
    engineCc: 1500,
    powerValue: 180,
    personalUse: false,
  }), 'from_3_to_5', 180);
  assert.equal(fee.valueRub, 20000 * 74.64);
});

test('additional broker and SBKTS/EPTS costs are included by default', () => {
  const result = calculateCustoms(base({ importSource: 'other' }));
  assert.equal(result.additionalCostsRub, 62000);
  assert.ok(result.totalPaymentsRub >= result.customsFeeRub + result.dutyRub + result.recyclingFeeRub + 62000 - 1);
});

test('georgia reexport and service commission are included for Georgia source', () => {
  const result = calculateCustoms(base({ importSource: 'georgia' }));
  const conversion = (15000 * rates.EUR + 500 * rates.GEL) * 0.02;
  assert.equal(result.georgiaConversionFeeRub, conversion);
  assert.equal(result.additionalCostsRub, 62000 + 500 * rates.GEL + conversion + 150000);
});

test('calculation is incomplete without CBR rates source', () => {
  const result = calculateCustoms(base({ ratesSource: '' }));
  assert.equal(result.isComplete, false);
  assert.ok(result.errors.some((item) => item.includes('курсы ЦБ')));
});

test('manufacture date resolution and age', () => {
  assert.equal(resolveManufactureDate({ manufactureYear: 2023 }), '2023-07-01');
  assert.equal(resolveManufactureDate({ manufactureMonth: '2023-08', manufactureYear: 2023 }), '2023-08-15');
  assert.equal(getAgeBand('2023-07-01', '2026-07-01'), 'under_3');
  assert.equal(getAgeBand('2023-06-30', '2026-07-01'), 'from_3_to_5');
});
