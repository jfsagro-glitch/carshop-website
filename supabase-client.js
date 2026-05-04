/**
 * supabase-client.js — EXPO MIR Supabase REST клиент
 * Vanilla JS, без зависимостей. Используется на всех страницах сайта.
 */
'use strict';

const SUPABASE_URL = 'https://jolyujjfxzhkswflqodz.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpvbHl1ampmeHpoa3N3Zmxxb2R6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc4NDQ1NjEsImV4cCI6MjA5MzQyMDU2MX0.LJt1YGmO2REOhSdoFAk_liWJiD9RjtR6zkmrDITTT-E';

const _sbHeaders = {
    'apikey': SUPABASE_ANON_KEY,
    'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
    'Content-Type': 'application/json'
};

/**
 * Внутренний хелпер: GET запрос к таблице с автоматическим подсчётом
 * @returns {{ data: any[], total: number }}
 */
async function _sbGet(table, params) {
    const url = `${SUPABASE_URL}/rest/v1/${table}?${params}`;
    const res = await fetch(url, {
        headers: { ..._sbHeaders, 'Prefer': 'count=exact' }
    });
    if (!res.ok) {
        const err = await res.text();
        throw new Error(`Supabase ${table} GET ${res.status}: ${err}`);
    }
    const total = parseInt(res.headers.get('Content-Range')?.split('/')[1] ?? '0', 10);
    const data = await res.json();
    return { data, total };
}

// ── CARS ─────────────────────────────────────────────────────────────────────

/**
 * Запрос каталога авто с фильтрами и пагинацией.
 *
 * @param {object} opts
 * @param {string} [opts.region]      — 'georgia' | 'europe'
 * @param {string} [opts.brand]       — точное совпадение
 * @param {string} [opts.model]       — точное совпадение
 * @param {number} [opts.priceFrom]
 * @param {number} [opts.priceTo]
 * @param {number} [opts.mileageTo]
 * @param {number} [opts.yearFrom]
 * @param {number} [opts.yearTo]
 * @param {string} [opts.fuelType]
 * @param {string} [opts.transmission]
 * @param {string} [opts.search]      — полнотекстовый поиск (brand + model)
 * @param {number} [opts.page=0]      — страница (0-based)
 * @param {number} [opts.limit=24]
 * @returns {Promise<{data: object[], total: number, page: number, limit: number}>}
 */
async function sbQueryCars(opts = {}) {
    const {
        region, brand, model, priceFrom, priceTo, mileageTo,
        yearFrom, yearTo, fuelType, transmission, search,
        page = 0, limit = 24
    } = opts;

    const p = [
        ['select', 'id,external_id,brand,model,year,price,currency,mileage,engine,fuel_type,transmission,power_kw,power_hp,color,drive,vin,url,images,specs'],
        ['is_active', 'eq.true'],
        ['order', 'year.desc,price.asc'],
        ['limit', String(limit)],
        ['offset', String(page * limit)]
    ];

    if (region)       p.push(['region',       `eq.${region}`]);
    if (brand)        p.push(['brand',         `eq.${brand}`]);
    if (model)        p.push(['model',         `eq.${model}`]);
    if (priceFrom)    p.push(['price',         `gte.${priceFrom}`]);
    if (priceTo)      p.push(['price',         `lte.${priceTo}`]);
    if (mileageTo)    p.push(['mileage',       `lte.${mileageTo}`]);
    if (yearFrom)     p.push(['year',          `gte.${yearFrom}`]);
    if (yearTo)       p.push(['year',          `lte.${yearTo}`]);
    if (fuelType)     p.push(['fuel_type',     `eq.${fuelType}`]);
    if (transmission) p.push(['transmission',  `eq.${transmission}`]);
    if (search)       p.push(['fts',           `plfts.${search}`]);

    const params = new URLSearchParams(p);
    return _sbGet('cars', params);
}

/**
 * Список уникальных марок для фильтра.
 * @param {string} [region]
 * @returns {Promise<string[]>}
 */
async function sbGetBrands(region) {
    const p = new URLSearchParams([
        ['select', 'brand'],
        ['is_active', 'eq.true'],
        ['order', 'brand.asc'],
        ['limit', '200']
    ]);
    if (region) p.set('region', `eq.${region}`);
    const { data } = await _sbGet('cars', p);
    return [...new Set(data.map(r => r.brand).filter(Boolean))];
}

/**
 * Список уникальных моделей для марки.
 * @param {string} brand
 * @param {string} [region]
 * @returns {Promise<string[]>}
 */
async function sbGetModels(brand, region) {
    const p = new URLSearchParams([
        ['select', 'model'],
        ['is_active', 'eq.true'],
        ['brand', `eq.${brand}`],
        ['order', 'model.asc'],
        ['limit', '200']
    ]);
    if (region) p.append('region', `eq.${region}`);
    const { data } = await _sbGet('cars', p);
    return [...new Set(data.map(r => r.model).filter(Boolean))];
}

/**
 * Подсчёт авто по региону (для счётчиков на главной).
 * @param {string} region
 * @returns {Promise<number>}
 */
async function sbCountCars(region) {
    const res = await fetch(
        `${SUPABASE_URL}/rest/v1/cars?is_active=eq.true&region=eq.${region}&select=id`,
        { headers: { ..._sbHeaders, 'Prefer': 'count=exact', 'Range': '0-0' } }
    );
    if (!res.ok) return 0;
    return parseInt(res.headers.get('Content-Range')?.split('/')[1] ?? '0', 10);
}

// ── LEADS ────────────────────────────────────────────────────────────────────

/**
 * Отправка заявки (замена FormSubmit.co).
 *
 * @param {object} opts
 * @param {string} [opts.type='car_order']   — тип заявки
 * @param {string} opts.name
 * @param {string} opts.phone
 * @param {string} [opts.email]
 * @param {string} [opts.message]
 * @param {number} [opts.carId]              — id из таблицы cars
 * @param {object} [opts.carInfo]            — snapshot авто
 * @param {string} [opts.sourcePage]         — страница источника
 * @returns {Promise<void>}
 */
async function sbSubmitLead(opts) {
    const { type = 'car_order', name, phone, email, message, carId, carInfo, sourcePage } = opts;
    const res = await fetch(`${SUPABASE_URL}/rest/v1/leads`, {
        method: 'POST',
        headers: { ..._sbHeaders, 'Prefer': 'return=minimal' },
        body: JSON.stringify({
            type,
            name,
            phone,
            email,
            message,
            car_id: carId || null,
            car_info: carInfo || null,
            source_page: sourcePage || location.pathname.replace(/^\//, '') || null
        })
    });
    if (!res.ok) {
        const err = await res.text();
        throw new Error(`Заявка не отправлена (${res.status}): ${err}`);
    }
}

// ── PARTS ─────────────────────────────────────────────────────────────────────

/**
 * Запрос каталога запчастей с фильтрами.
 *
 * @param {object} opts
 * @param {string} [opts.brand]
 * @param {string} [opts.category]
 * @param {string} [opts.search]      — поиск по названию (ilike)
 * @param {string} [opts.oem]         — точный OEM номер
 * @param {number} [opts.page=0]
 * @param {number} [opts.limit=24]
 * @returns {Promise<{data: object[], total: number}>}
 */
async function sbQueryParts(opts = {}) {
    const { brand, category, search, oem, page = 0, limit = 24 } = opts;

    const p = [
        ['select', 'id,oem_number,name,name_ru,category,brand,models,years_from,years_to,price_usd,price_kgs,stock_qty,images,description'],
        ['is_available', 'eq.true'],
        ['order', 'brand.asc,name.asc'],
        ['limit', String(limit)],
        ['offset', String(page * limit)]
    ];

    if (brand)    p.push(['brand',      `eq.${brand}`]);
    if (category) p.push(['category',   `eq.${category}`]);
    if (oem)      p.push(['oem_number', `eq.${oem}`]);
    if (search)   p.push(['name',       `ilike.*${search}*`]);

    const params = new URLSearchParams(p);
    return _sbGet('parts', params);
}

// ── ANALYTICS ─────────────────────────────────────────────────────────────────

/**
 * Логирование поискового события (пожар-и-забудь).
 * @param {string} page
 * @param {object} filters
 * @param {number} resultsCnt
 */
function sbLogSearch(page, filters, resultsCnt) {
    const cleanFilters = {};
    for (const [k, v] of Object.entries(filters || {})) {
        if (v !== '' && v !== null && v !== undefined) cleanFilters[k] = v;
    }
    fetch(`${SUPABASE_URL}/rest/v1/search_events`, {
        method: 'POST',
        headers: { ..._sbHeaders, 'Prefer': 'return=minimal' },
        body: JSON.stringify({ page, filters: cleanFilters, results_cnt: resultsCnt })
    }).catch(() => {}); // молча игнорируем ошибки аналитики
}

// ── FALLBACK: загрузка из JSON если Supabase недоступен ───────────────────────

/**
 * Загрузка авто с автоматическим фолбеком на локальный JSON.
 * Пробует Supabase, при ошибке — читает JSON файл.
 *
 * @param {string} region     — 'georgia' | 'europe'
 * @param {string} jsonFile   — путь к JSON (напр. 'cars_georgia_stock.json')
 * @param {object} [filters]  — фильтры для sbQueryCars
 */
async function sbLoadCarsWithFallback(region, jsonFile, filters = {}) {
    try {
        const result = await sbQueryCars({ region, ...filters });
        if (result.data && result.data.length > 0) {
            return result;
        }
        // Если Supabase вернул 0 записей — возможно ещё не заполнен, пробуем JSON
        throw new Error('Supabase вернул 0 записей');
    } catch (err) {
        console.warn(`[Supabase] fallback → ${jsonFile}:`, err.message);
        const res = await fetch(jsonFile);
        if (!res.ok) throw new Error(`JSON fallback тоже недоступен: ${jsonFile}`);
        const data = await res.json();
        return { data, total: data.length, page: 0, limit: data.length, _source: 'json' };
    }
}
