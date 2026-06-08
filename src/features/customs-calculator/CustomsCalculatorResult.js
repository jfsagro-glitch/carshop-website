import { formatEur, formatRub } from './currency.js';

export function renderResult(result, input) {
  const status = result.isComplete && !result.errors.length ? 'Точный расчёт по заполненным ставкам' : 'Расчёт неполный';
  const statusClass = result.isComplete && !result.errors.length ? 'ok' : 'warn';
  const cards = [
    ['Пошлина', formatRub(result.dutyRub), result.dutyEur ? formatEur(result.dutyEur) : ''],
    ['Сбор', formatRub(result.customsFeeRub), 'таможенное оформление'],
    ['Утильсбор', formatRub(result.recyclingFeeRub), input.recyclingFeeAlreadyPaid ? 'указан как уплаченный' : 'по условиям ввоза'],
    ['Доп. расходы', formatRub(result.additionalCostsRub || 0), 'сервисные расходы'],
    ['Акциз', formatRub(result.exciseRub), 'по мощности'],
    ['НДС', formatRub(result.vatRub), '22% для СТП'],
    ['Итого', formatRub(result.totalPaymentsRub), status],
  ];

  return `
    <section class="cc-result-panel" aria-live="polite">
      <div class="cc-result-head">
        <div>
          <span class="cc-status cc-status--${statusClass}">${status}</span>
          <h2>Результат расчёта</h2>
        </div>
        <div class="cc-total">
          <span>Цена авто + платежи</span>
          <strong>${formatRub(result.totalWithCarRub)}</strong>
        </div>
      </div>

      ${renderMessages(result)}

      <div class="cc-summary-grid">
        <article class="cc-summary-card cc-summary-card--wide">
          <span>Таможенная стоимость</span>
          <strong>${formatRub(result.customsValueRub)}</strong>
          <small>${formatEur(result.customsValueEur)}</small>
        </article>
        ${cards.map(([label, value, note]) => `
          <article class="cc-summary-card">
            <span>${escapeHtml(label)}</span>
            <strong>${escapeHtml(value)}</strong>
            <small>${escapeHtml(note || '')}</small>
          </article>
        `).join('')}
      </div>

      <div class="cc-breakdown">
        <h3>Как посчитали</h3>
        <div class="cc-breakdown-table" role="table">
          ${result.breakdown.map((row) => `
            <div class="cc-breakdown-row" role="row">
              <div role="cell"><strong>${escapeHtml(row.label)}</strong><span>${escapeHtml(row.formula)}</span></div>
              <div role="cell">${formatRub(row.valueRub)}</div>
            </div>
          `).join('')}
        </div>
      </div>

      <div class="cc-actions-row">
        <button class="cc-btn cc-btn--primary" type="button" id="copyCalculationBtn">
          <i class="fas fa-copy"></i> Скопировать расчёт
        </button>
        <button class="cc-btn" type="button" id="resetCalculationBtn">
          <i class="fas fa-rotate-left"></i> Сбросить
        </button>
      </div>
    </section>
  `;
}

export function resultToText(result) {
  const lines = [
    `Таможенная стоимость: ${formatRub(result.customsValueRub)} (${formatEur(result.customsValueEur)})`,
    `Таможенный сбор: ${formatRub(result.customsFeeRub)}`,
    `Пошлина/ЕТС: ${formatRub(result.dutyRub)}`,
    `Акциз: ${formatRub(result.exciseRub)}`,
    `НДС: ${formatRub(result.vatRub)}`,
    `Утильсбор: ${formatRub(result.recyclingFeeRub)}`,
    `Дополнительные расходы: ${formatRub(result.additionalCostsRub || 0)}`,
    `Конвертация по Грузии: ${formatRub(result.georgiaConversionFeeRub || 0)}`,
    `Итого платежи: ${formatRub(result.totalPaymentsRub)}`,
    `Цена авто + платежи: ${formatRub(result.totalWithCarRub)}`,
  ];
  if (result.warnings.length) {
    lines.push('', 'Важно:', ...result.warnings.map((item) => `- ${item}`));
  }
  return lines.join('\n');
}

function renderMessages(result) {
  const errors = result.errors.map((item) => `<li>${escapeHtml(item)}</li>`).join('');
  const warnings = result.warnings.map((item) => `<li>${escapeHtml(item)}</li>`).join('');
  return `
    ${errors ? `<div class="cc-message cc-message--error"><strong>Проверьте поля</strong><ul>${errors}</ul></div>` : ''}
    ${warnings ? `<div class="cc-message"><strong>Важно</strong><ul>${warnings}</ul></div>` : ''}
  `;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}
