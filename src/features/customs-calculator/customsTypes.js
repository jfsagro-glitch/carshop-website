/**
 * @typedef {'RUB' | 'USD' | 'EUR' | 'CNY' | 'KRW' | 'JPY' | 'GEL'} CurrencyCode
 * @typedef {'physical_ets' | 'legal_stp'} ImporterType
 * @typedef {'petrol' | 'diesel' | 'petrol_hybrid' | 'diesel_hybrid' | 'electric'} EngineType
 * @typedef {'under_3' | 'from_3_to_5' | 'from_5_to_7' | 'over_7'} AgeBand
 * @typedef {'passenger_car' | 'pickup' | 'quad' | 'snowmobile' | 'truck' | 'motorcycle' | 'bus' | 'trailer'} VehicleType
 *
 * @typedef {Object} CalculatorInput
 * @property {VehicleType} vehicleType
 * @property {ImporterType} importerType
 * @property {number} price
 * @property {CurrencyCode} currency
 * @property {number=} deliveryToBorder
 * @property {number=} insuranceToBorder
 * @property {number=} engineCc
 * @property {number=} powerValue
 * @property {'hp' | 'kw'} powerUnit
 * @property {EngineType} engineType
 * @property {AgeBand=} ageBand
 * @property {string=} manufactureDate
 * @property {string=} manufactureMonth
 * @property {number=} manufactureYear
 * @property {string} calculationDate
 * @property {boolean} alreadyClearedInEaeu
 * @property {boolean} recyclingFeeAlreadyPaid
 * @property {boolean} personalUse
 * @property {boolean} secondCarInYear
 * @property {boolean} plannedSaleWithin12Months
 * @property {boolean=} includeBrokerFee
 * @property {boolean=} includeSbktseptsFee
 * @property {'georgia' | 'usa' | 'korea' | 'china' | 'europe' | 'other'=} importSource
 * @property {boolean=} includeGeorgiaReexportFee
 * @property {boolean=} includeServiceCommission
 * @property {Partial<Record<CurrencyCode, number>>=} manualRates
 * @property {string=} tnvedCode
 *
 * @typedef {Object} BreakdownRow
 * @property {string} label
 * @property {string} formula
 * @property {number} valueRub
 *
 * @typedef {Object} CalculatorResult
 * @property {number} customsValueRub
 * @property {number} customsValueEur
 * @property {number} customsFeeRub
 * @property {number} dutyRub
 * @property {number=} dutyEur
 * @property {number} exciseRub
 * @property {number} vatRub
 * @property {number} recyclingFeeRub
 * @property {number} additionalCostsRub
 * @property {number} totalPaymentsRub
 * @property {number} totalWithCarRub
 * @property {boolean} isComplete
 * @property {string[]} warnings
 * @property {string[]} errors
 * @property {BreakdownRow[]} breakdown
 */

export const CUSTOMS_TYPES_MODULE = true;
