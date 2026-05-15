export function getDefaultInput() {
  const today = new Date().toISOString().slice(0, 10);
  return {
    vehicleType: 'passenger_car',
    importerType: 'physical_ets',
    price: 15000,
    currency: 'USD',
    deliveryToBorder: 0,
    insuranceToBorder: 0,
    engineCc: 1498,
    powerValue: 150,
    powerUnit: 'hp',
    engineType: 'petrol',
    importSource: 'georgia',
    ageBand: 'from_3_to_5',
    manufactureDate: '',
    manufactureMonth: '',
    manufactureYear: '',
    calculationDate: today,
    alreadyClearedInEaeu: false,
    recyclingFeeAlreadyPaid: false,
    personalUse: true,
    secondCarInYear: false,
    plannedSaleWithin12Months: false,
    includeBrokerFee: true,
    includeSbktseptsFee: true,
    includeGeorgiaReexportFee: true,
    includeServiceCommission: true,
    ratesSource: '',
    ratesDate: '',
    tnvedCode: '',
    manualRates: {},
  };
}

export function collectInput(form) {
  const fd = new FormData(form);
  const currency = String(fd.get('currency') || 'USD');
  const manualRates = {
    USD: numberValue(fd.get('rate_USD')),
    EUR: numberValue(fd.get('rate_EUR')),
    CNY: numberValue(fd.get('rate_CNY')),
    KRW: numberValue(fd.get('rate_KRW')),
    JPY: numberValue(fd.get('rate_JPY')),
    GEL: numberValue(fd.get('rate_GEL')),
  };

  return {
    vehicleType: String(fd.get('vehicleType') || 'passenger_car'),
    importerType: String(fd.get('importerType') || 'physical_ets'),
    price: numberValue(fd.get('price')),
    currency,
    deliveryToBorder: numberValue(fd.get('deliveryToBorder')),
    insuranceToBorder: numberValue(fd.get('insuranceToBorder')),
    engineCc: numberValue(fd.get('engineCc')),
    powerValue: numberValue(fd.get('powerValue')),
    powerUnit: String(fd.get('powerUnit') || 'hp'),
    engineType: String(fd.get('engineType') || 'petrol'),
    importSource: String(fd.get('importSource') || 'other'),
    ageBand: String(fd.get('ageBand') || ''),
    manufactureDate: String(fd.get('manufactureDate') || ''),
    manufactureMonth: String(fd.get('manufactureMonth') || ''),
    manufactureYear: integerValue(fd.get('manufactureYear')),
    calculationDate: String(fd.get('calculationDate') || new Date().toISOString().slice(0, 10)),
    alreadyClearedInEaeu: fd.has('alreadyClearedInEaeu'),
    recyclingFeeAlreadyPaid: fd.has('recyclingFeeAlreadyPaid'),
    personalUse: fd.has('personalUse'),
    secondCarInYear: fd.has('secondCarInYear'),
    plannedSaleWithin12Months: fd.has('plannedSaleWithin12Months'),
    includeBrokerFee: fd.has('includeBrokerFee'),
    includeSbktseptsFee: fd.has('includeSbktseptsFee'),
    includeGeorgiaReexportFee: fd.has('includeGeorgiaReexportFee'),
    includeServiceCommission: fd.has('includeServiceCommission'),
    tnvedCode: String(fd.get('tnvedCode') || '').trim(),
    ratesSource: String(fd.get('ratesSource') || ''),
    ratesDate: String(fd.get('ratesDate') || ''),
    manualRates,
  };
}

export function applyInputToForm(form, input) {
  Object.entries(input).forEach(([key, value]) => {
    if (key === 'manualRates') {
      Object.entries(value).forEach(([currency, rate]) => {
        const field = form.elements[`rate_${currency}`];
        if (field) field.value = rate;
      });
      return;
    }
    const field = form.elements[key];
    if (!field) return;
    if (field.type === 'checkbox') {
      field.checked = Boolean(value);
    } else {
      field.value = value ?? '';
    }
  });
}

function numberValue(value) {
  const n = Number(String(value || '').replace(',', '.'));
  return Number.isFinite(n) ? n : 0;
}

function integerValue(value) {
  const n = parseInt(String(value || ''), 10);
  return Number.isFinite(n) ? n : undefined;
}
