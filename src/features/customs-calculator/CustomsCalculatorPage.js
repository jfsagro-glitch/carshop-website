import { calculateCustoms } from './customsCalculator.js';
import { RATES_NOTICE } from './customsRates.js';
import { applyInputToForm, collectInput, getDefaultInput } from './CustomsCalculatorForm.js';
import { renderResult, resultToText } from './CustomsCalculatorResult.js';
import { loadCbrRates } from './cbrRates.js';

const devMode = /(?:localhost|127\.0\.0\.1)/.test(location.hostname) || new URLSearchParams(location.search).has('debug');

document.addEventListener('DOMContentLoaded', () => {
  const app = document.getElementById('customsCalculatorApp');
  if (!app) return;

  app.innerHTML = renderPageShell();
  const form = document.getElementById('customsCalculatorForm');
  const resultRoot = document.getElementById('customsCalculatorResult');
  const debugRoot = document.getElementById('customsCalculatorDebug');
  const defaultInput = getDefaultInput();
  applyInputToForm(form, defaultInput);
  const ratesStatus = document.getElementById('cbrRatesStatus');

  loadCbrRates()
    .then((payload) => {
      Object.entries(payload.rates).forEach(([code, rate]) => {
        const field = form.elements[`rate_${code}`];
        if (field) field.value = rate;
      });
      form.elements.ratesSource.value = 'cbr';
      form.elements.ratesDate.value = payload.date || '';
      if (ratesStatus) {
        ratesStatus.textContent = `Курсы ЦБ загружены: ${payload.date || 'сегодня'} (${payload.source})`;
        ratesStatus.classList.remove('cc-rates-status--error');
      }
      update();
    })
    .catch((error) => {
      form.elements.ratesSource.value = '';
      if (ratesStatus) {
        ratesStatus.textContent = `Курсы ЦБ не загружены: ${error.message}`;
        ratesStatus.classList.add('cc-rates-status--error');
      }
      update();
    });

  function update() {
    const input = collectInput(form);
    syncConditionalFields(form, input);
    const result = calculateCustoms(input);
    resultRoot.innerHTML = renderResult(result, input);
    if (devMode) {
      debugRoot.hidden = false;
      debugRoot.textContent = JSON.stringify({ input, result }, null, 2);
    }

    const copyBtn = document.getElementById('copyCalculationBtn');
    if (copyBtn) {
      copyBtn.addEventListener('click', async () => {
        await navigator.clipboard.writeText(resultToText(result));
        copyBtn.innerHTML = '<i class="fas fa-check"></i> Скопировано';
        setTimeout(() => {
          copyBtn.innerHTML = '<i class="fas fa-copy"></i> Скопировать расчёт';
        }, 1600);
      });
    }
    const resetBtn = document.getElementById('resetCalculationBtn');
    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        form.reset();
        applyInputToForm(form, defaultInput);
        update();
      });
    }
  }

  form.addEventListener('input', update);
  form.addEventListener('change', update);
  update();
});

function renderPageShell() {
  return `
    <div class="cc-page-grid">
      <form class="cc-form" id="customsCalculatorForm">
        <div class="cc-form-head">
          <span>${RATES_NOTICE}</span>
          <h2>Параметры автомобиля</h2>
        </div>

        <fieldset class="cc-fieldset">
          <legend>Основное</legend>
          <label>Тип ТС
            <select name="vehicleType">
              <option value="passenger_car">Легковой автомобиль</option>
              <option value="pickup" disabled>Пикап — скоро</option>
              <option value="quad" disabled>Квадроцикл — скоро</option>
              <option value="snowmobile" disabled>Снегоход — скоро</option>
              <option value="truck" disabled>Грузовик — скоро</option>
              <option value="motorcycle" disabled>Мотоцикл — скоро</option>
              <option value="bus" disabled>Автобус — скоро</option>
              <option value="trailer" disabled>Прицеп — скоро</option>
            </select>
          </label>
          <label>Ввозит
            <select name="importerType">
              <option value="physical_ets">Физическое лицо / ЕТС</option>
              <option value="legal_stp">Юридическое лицо / СТП</option>
            </select>
          </label>
          <label>Направление / источник авто
            <select name="importSource">
              <option value="georgia">Грузия</option>
              <option value="usa">США</option>
              <option value="korea">Корея</option>
              <option value="china">Китай</option>
              <option value="europe">Европа</option>
              <option value="other">Другое</option>
            </select>
          </label>
          <label>Код ТН ВЭД для СТП
            <input name="tnvedCode" inputmode="numeric" placeholder="Например, 870323">
          </label>
        </fieldset>

        <fieldset class="cc-fieldset">
          <legend>Стоимость и курсы</legend>
          <label>Стоимость автомобиля
            <input name="price" type="number" min="0" step="0.01">
          </label>
          <label>Валюта
            <select name="currency">
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
              <option value="RUB">RUB</option>
              <option value="CNY">CNY</option>
              <option value="KRW">KRW</option>
              <option value="JPY">JPY</option>
              <option value="GEL">GEL</option>
            </select>
          </label>
          <label>Доставка до границы
            <input name="deliveryToBorder" type="number" min="0" step="0.01">
          </label>
          <label>Страховка/расходы до границы
            <input name="insuranceToBorder" type="number" min="0" step="0.01">
          </label>
          <div class="cc-rate-grid">
            ${['USD', 'EUR', 'CNY', 'KRW', 'JPY', 'GEL'].map((code) => `
              <label>Курс ${code}
                <input name="rate_${code}" type="number" min="0" step="0.0001" readonly>
              </label>
            `).join('')}
          </div>
          <input name="ratesSource" type="hidden">
          <input name="ratesDate" type="hidden">
          <p class="cc-help" id="cbrRatesStatus">Загружаем актуальные курсы ЦБ РФ…</p>
        </fieldset>

        <fieldset class="cc-fieldset">
          <legend>Двигатель и возраст</legend>
          <label>Тип двигателя
            <select name="engineType">
              <option value="petrol">Бензиновый</option>
              <option value="diesel">Дизельный</option>
              <option value="petrol_hybrid">Бензиновый гибрид</option>
              <option value="diesel_hybrid">Дизельный гибрид</option>
              <option value="electric">Электрический</option>
            </select>
          </label>
          <label>Объём двигателя, см³
            <input name="engineCc" type="number" min="0" step="1">
          </label>
          <label>Мощность
            <input name="powerValue" type="number" min="0" step="0.01">
          </label>
          <label>Единица мощности
            <select name="powerUnit">
              <option value="hp">л.с.</option>
              <option value="kw">кВт</option>
            </select>
          </label>
          <label>Возраст
            <select name="ageBand">
              <option value="">Определить по дате</option>
              <option value="under_3">Менее 3 лет</option>
              <option value="from_3_to_5">3–5 лет</option>
              <option value="from_5_to_7">5–7 лет</option>
              <option value="over_7">Более 7 лет</option>
            </select>
          </label>
          <label>Точная дата выпуска
            <input name="manufactureDate" type="date">
          </label>
          <label>Месяц/год выпуска
            <input name="manufactureMonth" type="month">
          </label>
          <label>Только год выпуска
            <input name="manufactureYear" type="number" min="1950" max="2035" step="1" placeholder="2023">
          </label>
          <label>Дата расчёта
            <input name="calculationDate" type="date">
          </label>
          <p class="cc-help">Для гибридов вводите мощность из ЭПТС/СБКТС/официальных документов.</p>
        </fieldset>

        <fieldset class="cc-fieldset cc-checks">
          <legend>Сценарии</legend>
          ${checkbox('alreadyClearedInEaeu', 'Авто растаможен при ввозе в ЕАЭС')}
          ${checkbox('recyclingFeeAlreadyPaid', 'Утильсбор уже уплачен')}
          ${checkbox('personalUse', 'Автомобиль для личного пользования')}
          ${checkbox('secondCarInYear', 'Это второй автомобиль за год')}
          ${checkbox('plannedSaleWithin12Months', 'Планируется продажа/отчуждение в течение 12 месяцев')}
          ${checkbox('includeBrokerFee', 'Добавить брокера — 37 000 ₽')}
          ${checkbox('includeSbktseptsFee', 'Добавить СБКТС/ЭПТС — 25 000 ₽')}
          ${checkbox('includeGeorgiaReexportFee', 'Для Грузии: реэкспорт — 500 GEL')}
          ${checkbox('includeServiceCommission', 'Для Грузии: комиссия EXPO MIR — 150 000 ₽')}
        </fieldset>
      </form>

      <div>
        <div id="customsCalculatorResult"></div>
        <pre id="customsCalculatorDebug" class="cc-debug" hidden></pre>
      </div>
    </div>
  `;
}

function checkbox(name, label) {
  return `
    <label class="cc-check">
      <input name="${name}" type="checkbox">
      <span>${label}</span>
    </label>
  `;
}

function syncConditionalFields(form, input) {
  const engineCcField = form.elements.engineCc;
  if (engineCcField) {
    engineCcField.disabled = input.engineType === 'electric';
    if (input.engineType === 'electric') engineCcField.value = '';
  }
}
