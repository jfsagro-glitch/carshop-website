export const RATES_NOTICE = 'Ставки: РФ/ЕАЭС, 2026. Перед оплатой сверяйте с таможенным брокером/ФТС';

export const DEFAULT_CURRENCY_RATES_RUB = {
  RUB: 1,
  USD: 92,
  EUR: 100,
  CNY: 12.7,
  KRW: 0.067,
  JPY: 0.62,
  GEL: 34,
};

export const ADDITIONAL_COSTS_2026 = {
  brokerFeeRub: 37000,
  sbktsEptsFeeRub: 25000,
  georgiaReexportGel: 500,
  serviceCommissionRub: 150000,
  georgiaConversionMarkup: 0.02,
};

export const CUSTOMS_CLEARANCE_FEES_2026 = [
  { maxRub: 200000, feeRub: 1231 },
  { maxRub: 450000, feeRub: 2462 },
  { maxRub: 1200000, feeRub: 4924 },
  { maxRub: 2700000, feeRub: 13541 },
  { maxRub: 4200000, feeRub: 18465 },
  { maxRub: 5500000, feeRub: 21344 },
  { maxRub: 10000000, feeRub: 49240 },
  { maxRub: Infinity, feeRub: 73860 },
];

export const PHYSICAL_ETS_UNDER_3_2026 = [
  { maxValueEur: 8500, percent: 0.54, minEurPerCc: 2.5 },
  { maxValueEur: 16700, percent: 0.48, minEurPerCc: 3.5 },
  { maxValueEur: 42300, percent: 0.48, minEurPerCc: 5.5 },
  { maxValueEur: 84500, percent: 0.48, minEurPerCc: 7.5 },
  { maxValueEur: 169000, percent: 0.48, minEurPerCc: 15 },
  { maxValueEur: Infinity, percent: 0.48, minEurPerCc: 20 },
];

export const PHYSICAL_ETS_3_TO_5_2026 = [
  { maxCc: 1000, rateEurPerCc: 1.5 },
  { maxCc: 1500, rateEurPerCc: 1.7 },
  { maxCc: 1800, rateEurPerCc: 2.5 },
  { maxCc: 2300, rateEurPerCc: 2.7 },
  { maxCc: 3000, rateEurPerCc: 3.0 },
  { maxCc: Infinity, rateEurPerCc: 3.6 },
];

export const PHYSICAL_ETS_OVER_5_2026 = [
  { maxCc: 1000, rateEurPerCc: 3.0 },
  { maxCc: 1500, rateEurPerCc: 3.2 },
  { maxCc: 1800, rateEurPerCc: 3.5 },
  { maxCc: 2300, rateEurPerCc: 4.8 },
  { maxCc: 3000, rateEurPerCc: 5.0 },
  { maxCc: Infinity, rateEurPerCc: 5.7 },
];

export const EXCISE_RATES_2026 = [
  { maxHp: 90, rateRubPerHp: 0 },
  { maxHp: 150, rateRubPerHp: 64 },
  { maxHp: 200, rateRubPerHp: 613 },
  { maxHp: 300, rateRubPerHp: 1004 },
  { maxHp: 400, rateRubPerHp: 1711 },
  { maxHp: 500, rateRubPerHp: 1771 },
  { maxHp: Infinity, rateRubPerHp: 1829 },
];

export const RECYCLING_BASE_RATE_M1_2026 = 20000;

export const UTIL_COEFFICIENTS_2026_ICE_PHYSICAL = [
  {
    ccMinExclusive: 0,
    ccMax: 1000,
    powerBands: [
      { maxHp: 160, under3: 0.17, over3: 0.26 },
      { maxHp: 190, under3: 15.36, over3: 28.43 },
      { maxHp: 220, under3: 15.84, over3: 29.28 },
      { maxHp: 250, under3: 16.2, over3: 30.12 },
      { maxHp: Infinity, under3: 17.28, over3: 30.12 },
    ],
  },
  {
    ccMinExclusive: 1000,
    ccMax: 2000,
    powerBands: [
      { maxHp: 160, under3: 0.17, over3: 0.26 },
      { maxHp: 190, under3: 45, over3: 74.64 },
      { maxHp: 220, under3: 47.64, over3: 79.2 },
      { maxHp: 250, under3: 50.52, over3: 83.88 },
      { maxHp: 280, under3: 57.12, over3: 91.92 },
      { maxHp: 310, under3: 64.56, over3: 100.56 },
      { maxHp: 340, under3: 72.96, over3: 110.16 },
      { maxHp: 370, under3: 83.16, over3: 120.6 },
      { maxHp: 400, under3: 94.8, over3: 132 },
      { maxHp: 430, under3: 108, over3: 144.6 },
      { maxHp: 460, under3: 123.24, over3: 158.4 },
      { maxHp: 500, under3: 140.4, over3: 173.4 },
      { maxHp: Infinity, under3: 160.08, over3: 189.84 },
    ],
  },
  {
    ccMinExclusive: 2000,
    ccMax: 3000,
    powerBands: [
      { maxHp: 160, under3: 0.17, over3: 0.26 },
      { maxHp: 190, under3: 115.34, over3: 172.8 },
      { maxHp: 220, under3: 118.2, over3: 175.08 },
      { maxHp: 250, under3: 120.12, over3: 177.6 },
      { maxHp: 280, under3: 126, over3: 183 },
      { maxHp: 310, under3: 131.04, over3: 188.52 },
      { maxHp: 340, under3: 136.32, over3: 193.68 },
      { maxHp: 370, under3: 141.72, over3: 199.08 },
      { maxHp: 400, under3: 147.48, over3: 204.72 },
      { maxHp: 430, under3: 153.36, over3: 210.48 },
      { maxHp: 460, under3: 159.48, over3: 216.36 },
      { maxHp: 500, under3: 165.84, over3: 222.36 },
      { maxHp: Infinity, under3: 172.44, over3: 228.6 },
    ],
  },
  {
    ccMinExclusive: 3000,
    ccMax: 3500,
    powerBands: [
      { maxHp: 160, under3: 129.2, over3: 197.81 },
      { maxHp: 190, under3: 131.76, over3: 200.04 },
      { maxHp: 220, under3: 134.4, over3: 202.2 },
      { maxHp: 250, under3: 137.16, over3: 204.36 },
      { maxHp: 280, under3: 140.52, over3: 207.24 },
      { maxHp: 310, under3: 144, over3: 212.4 },
      { maxHp: 340, under3: 151.92, over3: 217.8 },
      { maxHp: 370, under3: 160.32, over3: 224.28 },
      { maxHp: 400, under3: 169.2, over3: 231 },
      { maxHp: 430, under3: 178.44, over3: 237.96 },
      { maxHp: 460, under3: 188.28, over3: 245.04 },
      { maxHp: 500, under3: 198.6, over3: 252.48 },
      { maxHp: Infinity, under3: 209.52, over3: 260.04 },
    ],
  },
  {
    ccMinExclusive: 3500,
    ccMax: Infinity,
    powerBands: [
      { maxHp: 160, under3: 164.53, over3: 216.29 },
      { maxHp: 190, under3: 167.28, over3: 219.48 },
      { maxHp: 220, under3: 170.16, over3: 222.84 },
      { maxHp: 250, under3: 173.04, over3: 226.2 },
      { maxHp: 280, under3: 176.52, over3: 231.36 },
      { maxHp: 310, under3: 180, over3: 236.64 },
      { maxHp: 340, under3: 186.36, over3: 249.6 },
      { maxHp: 370, under3: 192.88, over3: 263.4 },
      { maxHp: 400, under3: 199.68, over3: 277.92 },
      { maxHp: 430, under3: 206.64, over3: 293.16 },
      { maxHp: 460, under3: 213.84, over3: 309.36 },
      { maxHp: 500, under3: 221.28, over3: 326.4 },
      { maxHp: Infinity, under3: 229.08, over3: 344.28 },
    ],
  },
];

export const ETT_IMPORT_DUTY_RATES_PASSENGER_CAR = [
  // TODO_RATE_UPDATE: fill confirmed ETT/TN VED rates for legal entities by exact TN VED code.
  // Example shape:
  // { tnved: '870323', engineType: 'petrol', ageBand: 'from_3_to_5', ccMinExclusive: 1500, ccMax: 3000, rate: { type: 'combined_max', percent: 0.15, minEurPerCc: 0.6 } }
];
