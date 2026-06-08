import {
  ADDITIONAL_COSTS_2026,
  CUSTOMS_CLEARANCE_FEES_2026,
  ETT_IMPORT_DUTY_RATES_PASSENGER_CAR,
  EXCISE_RATES_2026,
  PHYSICAL_ETS_3_TO_5_2026,
  PHYSICAL_ETS_OVER_5_2026,
  PHYSICAL_ETS_UNDER_3_2026,
  RECYCLING_BASE_RATE_M1_2026,
  UTIL_COEFFICIENTS_2026_ICE_PHYSICAL,
} from './customsRates.js';
import { resolveAgeBand } from './age.js';
import {
  calculateCustomsValueEur,
  calculateCustomsValueRub,
  getRateToRub,
  roundMoney,
} from './currency.js';

export function calculateCustomsFee(customsValueRub) {
  const row = CUSTOMS_CLEARANCE_FEES_2026.find((item) => customsValueRub <= item.maxRub);
  return row ? row.feeRub : 0;
}

export function convertPowerToHp(value, unit) {
  const power = Number(value || 0);
  return unit === 'kw' ? roundMoney(power * 1.35962) : power;
}

export function calculateExcise(powerHp) {
  const row = EXCISE_RATES_2026.find((item) => powerHp <= item.maxHp);
  return roundMoney(powerHp * (row ? row.rateRubPerHp : 0));
}

export function calculatePhysicalEtsDuty({ customsValueEur, engineCc, ageBand, eurRub }) {
  if (ageBand === 'under_3') {
    const row = PHYSICAL_ETS_UNDER_3_2026.find((item) => customsValueEur <= item.maxValueEur);
    const byPercent = customsValueEur * row.percent;
    const byCc = engineCc * row.minEurPerCc;
    const dutyEur = roundMoney(Math.max(byPercent, byCc));
    return {
      dutyEur,
      dutyRub: roundMoney(dutyEur * eurRub),
      formula: `max(${customsValueEur.toFixed(2)} € × ${row.percent * 100}%, ${engineCc} см³ × ${row.minEurPerCc} €/см³)`,
    };
  }

  const table = ageBand === 'from_3_to_5' ? PHYSICAL_ETS_3_TO_5_2026 : PHYSICAL_ETS_OVER_5_2026;
  const row = table.find((item) => engineCc <= item.maxCc);
  const dutyEur = roundMoney(engineCc * row.rateEurPerCc);
  return {
    dutyEur,
    dutyRub: roundMoney(dutyEur * eurRub),
    formula: `${engineCc} см³ × ${row.rateEurPerCc} €/см³`,
  };
}

export function calculateImportDutyByEtt(params) {
  const {
    customsValueRub,
    customsValueEur,
    engineCc,
    engineType,
    ageBand,
    eurRub,
    tnvedCode,
  } = params;

  if (engineType === 'electric') {
    return {
      dutyRub: roundMoney(customsValueRub * 0.15),
      formula: `${Math.round(customsValueRub).toLocaleString('ru-RU')} ₽ × 15%`,
      warning: '',
    };
  }

  const rateRow = ETT_IMPORT_DUTY_RATES_PASSENGER_CAR.find((row) => {
    return (!row.tnved || row.tnved === tnvedCode)
      && row.engineType === engineType
      && row.ageBand === ageBand
      && engineCc > row.ccMinExclusive
      && engineCc <= row.ccMax;
  });

  if (!rateRow) {
    return {
      dutyRub: null,
      formula: '',
      warning: 'Для юрлица/СТП нужна подтвержденная ставка ЕТТ по точному коду ТН ВЭД. Точный итог не рассчитан.',
    };
  }

  const rate = rateRow.rate;
  if (rate.type === 'percent') {
    return {
      dutyRub: roundMoney(customsValueRub * rate.percent),
      formula: `${Math.round(customsValueRub).toLocaleString('ru-RU')} ₽ × ${rate.percent * 100}%`,
      warning: '',
    };
  }
  if (rate.type === 'specific_eur_per_cc') {
    const dutyRub = engineCc * rate.eurPerCc * eurRub;
    return {
      dutyRub: roundMoney(dutyRub),
      formula: `${engineCc} см³ × ${rate.eurPerCc} €/см³ × курс €`,
      warning: '',
    };
  }
  if (rate.type === 'combined_max') {
    const byPercent = customsValueRub * rate.percent;
    const byCc = engineCc * rate.minEurPerCc * eurRub;
    return {
      dutyRub: roundMoney(Math.max(byPercent, byCc)),
      formula: `max(${customsValueEur.toFixed(2)} € × ${rate.percent * 100}%, ${engineCc} см³ × ${rate.minEurPerCc} €/см³)`,
      warning: '',
    };
  }
  if (rate.type === 'combined_min') {
    const byPercent = customsValueRub * rate.percent;
    const byCc = engineCc * rate.minEurPerCc * eurRub;
    return {
      dutyRub: roundMoney(Math.min(byPercent, byCc)),
      formula: `min(${customsValueEur.toFixed(2)} € × ${rate.percent * 100}%, ${engineCc} см³ × ${rate.minEurPerCc} €/см³)`,
      warning: '',
    };
  }

  return {
    dutyRub: null,
    formula: '',
    warning: 'Неподдерживаемый тип ставки ЕТТ в конфиге.',
  };
}

export function calculateRecyclingFee(input, ageBand, powerHp) {
  const warnings = [];
  if (input.recyclingFeeAlreadyPaid) {
    return {
      valueRub: 0,
      formula: 'Утильсбор указан как уже уплаченный',
      warnings,
      isComplete: true,
    };
  }

  if (input.vehicleType !== 'passenger_car') {
    warnings.push('Для выбранного типа ТС таблица утильсбора не заполнена. Расчёт неполный.');
    return { valueRub: null, formula: '', warnings, isComplete: false };
  }

  if (input.engineType === 'electric') {
    warnings.push('Для EV нужна актуальная таблица коэффициентов ПП РФ №1291. Утильсбор не включен в точный итог.');
    return { valueRub: null, formula: '', warnings, isComplete: false };
  }

  const engineCc = Number(input.engineCc || 0);
  const isUnder3 = ageBand === 'under_3';
  const eligibleForPersonalRate = input.importerType === 'physical_ets'
    && input.personalUse
    && !input.secondCarInYear
    && !input.plannedSaleWithin12Months
    && engineCc <= 3000
    && powerHp <= 160
    && input.vehicleType === 'passenger_car';

  if (eligibleForPersonalRate) {
    const coefficient = isUnder3 ? 0.17 : 0.26;
    return {
      valueRub: roundMoney(RECYCLING_BASE_RATE_M1_2026 * coefficient),
      formula: `${RECYCLING_BASE_RATE_M1_2026.toLocaleString('ru-RU')} ₽ × ${coefficient}`,
      warnings,
      isComplete: true,
    };
  }

  const ccGroup = UTIL_COEFFICIENTS_2026_ICE_PHYSICAL.find(
    (group) => engineCc > group.ccMinExclusive && engineCc <= group.ccMax,
  );
  const powerBand = ccGroup && ccGroup.powerBands.find((band) => powerHp <= band.maxHp);
  if (!ccGroup || !powerBand) {
    warnings.push('Не найдена таблица утильсбора для заданных объема и мощности. Расчёт неполный.');
    return { valueRub: null, formula: '', warnings, isComplete: false };
  }
  const coefficient = isUnder3 ? powerBand.under3 : powerBand.over3;
  return {
    valueRub: roundMoney(RECYCLING_BASE_RATE_M1_2026 * coefficient),
    formula: `${RECYCLING_BASE_RATE_M1_2026.toLocaleString('ru-RU')} ₽ × ${coefficient}`,
    warnings,
    isComplete: true,
  };
}

export function calculateCustoms(input) {
  const warnings = [];
  const errors = validateInput(input);
  const breakdown = [];
  let isComplete = errors.length === 0;

  if (input.engineType === 'petrol_hybrid' || input.engineType === 'diesel_hybrid') {
    warnings.push('Для гибридов мощность нужно брать из ЭПТС/СБКТС/документов. Не складывай мощности без подтверждения.');
  }
  if (input.engineType === 'electric' || input.vehicleType === 'motorcycle') {
    warnings.push('Для электромобилей/мотоциклов применяется СТП.');
  }
  if (input.alreadyClearedInEaeu) {
    warnings.push('Для автомобилей, растаможенных в Армении/Беларуси/Киргизии/Казахстане, возможны ограничения и доплаты.');
  }
  if (input.importerType === 'legal_stp') {
    warnings.push('Режим юрлица пока справочный: ставки зависят от точного кода ТН ВЭД.');
  }

  let customsValueRub = 0;
  let customsValueEur = 0;
  let eurRub = 0;
  try {
    customsValueRub = calculateCustomsValueRub(input);
    customsValueEur = calculateCustomsValueEur(customsValueRub, input.manualRates);
    eurRub = getRateToRub('EUR', input.manualRates);
  } catch (err) {
    errors.push(err.message);
    isComplete = false;
  }

  const ageBand = resolveAgeBand(input);
  const powerHp = convertPowerToHp(input.powerValue, input.powerUnit);
  const baseResult = {
    customsValueRub,
    customsValueEur,
    customsFeeRub: 0,
    dutyRub: 0,
    dutyEur: 0,
    exciseRub: 0,
    vatRub: 0,
    recyclingFeeRub: 0,
    additionalCostsRub: 0,
    georgiaConversionFeeRub: 0,
    totalPaymentsRub: 0,
    totalWithCarRub: customsValueRub,
    isComplete,
    warnings,
    errors,
    breakdown,
  };

  if (errors.length) {
    return baseResult;
  }

  if (input.vehicleType !== 'passenger_car') {
    warnings.push('На первом этапе полностью реализован только легковой автомобиль. Для выбранного типа ТС расчёт неполный.');
    isComplete = false;
  }

  const cleared = Boolean(input.alreadyClearedInEaeu);
  let customsFeeRub = cleared ? 0 : calculateCustomsFee(customsValueRub);
  let dutyRub = 0;
  let dutyEur = 0;
  let exciseRub = 0;
  let vatRub = 0;
  const gelRub = getRateToRub('GEL', input.manualRates);
  const purchaseRub = roundMoney(Number(input.price || 0) * getRateToRub(input.currency, input.manualRates));
  const georgiaReexportRub = input.importSource === 'georgia' && input.includeGeorgiaReexportFee !== false
    ? roundMoney(ADDITIONAL_COSTS_2026.georgiaReexportGel * gelRub)
    : 0;
  const georgiaConversionFeeRub = input.importSource === 'georgia'
    ? roundMoney((purchaseRub + georgiaReexportRub) * ADDITIONAL_COSTS_2026.georgiaConversionMarkup)
    : 0;
  const serviceCommissionRub = input.importSource === 'georgia' && input.includeServiceCommission !== false
    ? ADDITIONAL_COSTS_2026.serviceCommissionRub
    : 0;
  const additionalCostsRub = roundMoney(
    Number(input.includeBrokerFee === false ? 0 : ADDITIONAL_COSTS_2026.brokerFeeRub)
    + Number(input.includeSbktseptsFee === false ? 0 : ADDITIONAL_COSTS_2026.sbktsEptsFeeRub)
    + georgiaReexportRub
    + georgiaConversionFeeRub
    + serviceCommissionRub,
  );

  if (cleared) {
    warnings.push('Пошлина, НДС, акциз и таможенный сбор обнулены: выбран сценарий растаможки при ввозе в ЕАЭС.');
    breakdown.push({ label: 'Таможенное оформление', formula: 'Авто уже растаможен в ЕАЭС', valueRub: 0 });
  } else if (input.importerType === 'physical_ets' && input.engineType !== 'electric') {
    const duty = calculatePhysicalEtsDuty({
      customsValueEur,
      engineCc: Number(input.engineCc),
      ageBand,
      eurRub,
    });
    dutyRub = duty.dutyRub;
    dutyEur = duty.dutyEur;
    breakdown.push({ label: 'Единая ставка ЕТС', formula: duty.formula, valueRub: dutyRub });
  } else {
    const stpDuty = calculateImportDutyByEtt({
      customsValueRub,
      customsValueEur,
      engineCc: Number(input.engineCc || 0),
      engineType: input.engineType,
      ageBand,
      eurRub,
      tnvedCode: input.tnvedCode || '',
    });
    if (stpDuty.warning) {
      warnings.push(stpDuty.warning);
      isComplete = false;
    } else {
      dutyRub = stpDuty.dutyRub;
      breakdown.push({ label: 'Пошлина СТП/ЕТТ', formula: stpDuty.formula, valueRub: dutyRub });
    }
    exciseRub = calculateExcise(powerHp);
    vatRub = roundMoney((customsValueRub + dutyRub + exciseRub) * 0.22);
  }

  const recycling = calculateRecyclingFee(input, ageBand, powerHp);
  warnings.push(...recycling.warnings);
  if (!recycling.isComplete) {
    isComplete = false;
  }
  const recyclingFeeRub = recycling.valueRub === null ? 0 : recycling.valueRub;

  if (customsFeeRub) {
    breakdown.unshift({ label: 'Таможенный сбор', formula: `Диапазон от ${Math.round(customsValueRub).toLocaleString('ru-RU')} ₽`, valueRub: customsFeeRub });
  }
  if (exciseRub) {
    breakdown.push({ label: 'Акциз', formula: `${powerHp.toFixed(2)} л.с. × ставка по диапазону`, valueRub: exciseRub });
  }
  if (vatRub) {
    breakdown.push({ label: 'НДС', formula: '(таможенная стоимость + пошлина + акциз) × 22%', valueRub: vatRub });
  }
  breakdown.push({ label: 'Утилизационный сбор', formula: recycling.formula || 'Не включен: нет подтвержденной таблицы', valueRub: recyclingFeeRub });
  if (input.includeBrokerFee !== false) {
    breakdown.push({ label: 'Брокер', formula: 'Фиксированный сервисный расход', valueRub: ADDITIONAL_COSTS_2026.brokerFeeRub });
  }
  if (input.includeSbktseptsFee !== false) {
    breakdown.push({ label: 'СБКТС/ЭПТС', formula: 'Оформление СБКТС/ЭПТС', valueRub: ADDITIONAL_COSTS_2026.sbktsEptsFeeRub });
  }
  if (georgiaReexportRub) {
    breakdown.push({ label: 'Реэкспорт из Грузии', formula: `${ADDITIONAL_COSTS_2026.georgiaReexportGel} GEL × курс GEL`, valueRub: georgiaReexportRub });
  }
  if (georgiaConversionFeeRub) {
    breakdown.push({ label: 'Конвертация по Грузии', formula: `(${Math.round(purchaseRub).toLocaleString('ru-RU')} ₽ покупка + ${Math.round(georgiaReexportRub).toLocaleString('ru-RU')} ₽ реэкспорт) × 2%`, valueRub: georgiaConversionFeeRub });
  }
  if (serviceCommissionRub) {
    breakdown.push({ label: 'Комиссия EXPO MIR', formula: 'Фиксированная комиссия за сопровождение сделки', valueRub: serviceCommissionRub });
  }

  const totalPaymentsRub = roundMoney(customsFeeRub + dutyRub + exciseRub + vatRub + recyclingFeeRub + additionalCostsRub);
  return {
    customsValueRub,
    customsValueEur,
    customsFeeRub,
    dutyRub,
    dutyEur,
    exciseRub,
    vatRub,
    recyclingFeeRub,
    additionalCostsRub,
    georgiaConversionFeeRub,
    totalPaymentsRub,
    totalWithCarRub: roundMoney(customsValueRub + totalPaymentsRub),
    isComplete,
    warnings: unique(warnings),
    errors,
    breakdown,
  };
}

function validateInput(input) {
  const errors = [];
  if (!Number.isFinite(Number(input.price)) || Number(input.price) <= 0) {
    errors.push('Стоимость автомобиля должна быть больше 0.');
  }
  if (!input.currency) {
    errors.push('Выберите валюту стоимости.');
  }
  if (input.ratesSource !== 'cbr') {
    errors.push('Для расчёта нужны актуальные курсы ЦБ РФ. Дождитесь загрузки курсов.');
  }
  if (!input.powerUnit) {
    errors.push('Выберите единицу мощности.');
  }
  if (input.engineType !== 'electric' && (!Number.isFinite(Number(input.engineCc)) || Number(input.engineCc) <= 0)) {
    errors.push('Объем двигателя обязателен для ДВС и гибридов.');
  }
  if (!Number.isFinite(Number(input.powerValue)) || Number(input.powerValue) <= 0) {
    errors.push('Мощность обязательна для утильсбора, акциза и EV.');
  }
  if (!input.ageBand && !input.manufactureDate && !input.manufactureMonth && !input.manufactureYear) {
    errors.push('Укажите возраст или дату выпуска.');
  }
  if (input.vehicleType !== 'passenger_car') {
    errors.push('Для выбранного типа ТС пока нет подтвержденной таблицы ставок.');
  }
  return errors;
}

function unique(items) {
  return Array.from(new Set(items.filter(Boolean)));
}
