(function () {
    'use strict';

    const DATA_URL = 'cars_europe_new.json?v=20260529-avtostok63-passenger';
    const PAGE_SIZE = 18;
    const FINAL_PRICE_MARKUP_RUB = 200000;
    const CONTACT_PHONE = '79178177711';
    const RUB = new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 0 });
    const EUR = new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 0 });

    const state = {
        cars: [],
        filtered: [],
        visible: PAGE_SIZE,
        renderedKeys: new Set(),
    };

    const $ = (id) => document.getElementById(id);

    function safeText(value) {
        return String(value ?? '').trim();
    }

    function safeHttpUrl(value, fallback = '') {
        try {
            const url = new URL(String(value || ''), location.href);
            return ['http:', 'https:'].includes(url.protocol) ? url.href : fallback;
        } catch (_) {
            return fallback;
        }
    }

    function getImages(car) {
        const images = Array.isArray(car.images) ? car.images : [];
        return images
            .map(item => typeof item === 'string' ? item : item?.url)
            .map(src => safeHttpUrl(src, ''))
            .filter(Boolean);
    }

    function getImage(car) {
        return getImages(car)[0] || '';
    }

    function formatRub(value) {
        const number = Number(value || 0);
        return number > 0 ? `${RUB.format(number)} ₽` : 'Расчёт по запросу';
    }

    function formatEur(value) {
        const number = Number(value || 0);
        return number > 0 ? `${EUR.format(number)} € в Европе` : 'Цена в Европе по запросу';
    }

    function formatMileage(value) {
        const number = Number(value || 0);
        return number > 0 ? `${RUB.format(number)} км` : '—';
    }

    function withFinalMarkup(value) {
        const number = Number(value || 0);
        return number > 0 ? number + FINAL_PRICE_MARKUP_RUB : 0;
    }

    function parseBudgetRange(value) {
        const [minRaw, maxRaw] = String(value || '').split('-');
        return {
            min: Number(minRaw || 0),
            max: Number(maxRaw || 0),
        };
    }

    function carTitle(car) {
        return safeText(car.full_title) || [car.brand, car.model].filter(Boolean).join(' ') || 'Автомобиль из Европы';
    }

    function carSearchText(car) {
        return [
            car.brand,
            car.model,
            car.full_title,
            car.fuel_type,
            car.transmission,
            car.power_hp,
            car.first_registration,
        ].map(safeText).join(' ').toLowerCase();
    }

    function commercialText(car) {
        return [car.brand, car.model, car.full_title, car.equipment?.join(' ')]
            .map(safeText)
            .join(' ')
            .toLowerCase();
    }

    function hasPassengerVanSignal(text) {
        return /\b(tourer|tourneo|multivan|california|caravelle|shuttle|kombi|combi|life|9\s*-?\s*sitzer|8\s*-?\s*sitze|8\s*-?\s*sitzer|7\s*-?\s*sitzer|пассажир|passenger)\b/i.test(text);
    }

    function isCommercialVehicle(car) {
        const brand = safeText(car.brand).toLowerCase();
        const model = safeText(car.model).toLowerCase();
        const text = commercialText(car);
        const passengerVan = hasPassengerVanSignal(text);

        if (brand === 'iveco') return true;

        const commercialModels = [
            'daily',
            'ducato',
            'sprinter',
            'crafter',
            'transit',
            'transit custom',
            'transit connect',
            'vito',
            'vivaro',
            'trafic',
            'proace',
            'proace city',
            'doblo',
            'combo',
            'caddy',
            'transporter',
        ];

        const commercialModel = commercialModels.some(item => model.includes(item));
        const hardCargoSignal = /\b(kasten|cargo|kastenwagen|panel\s*van|trenngitter|regale|nur\s+handel|heckflügeltür|ka\s|ka$)\b/i.test(text);

        if (hardCargoSignal) return true;
        if (!commercialModel) return false;
        return !passengerVan;
    }

    function normalizedCars(rows) {
        return (rows || [])
            .filter(car => car && (car.brand || car.model) && getImage(car))
            .filter(car => !isCommercialVehicle(car))
            .map(car => ({
                ...car,
                _images: getImages(car),
                _image: getImage(car),
                _title: carTitle(car),
                _search: carSearchText(car),
                _turnkey: withFinalMarkup(car.turnkey_price_rub),
                _price: Number(car.price || 0),
                _year: Number(car.first_registration_year || 0),
                _mileage: Number(car.mileage || 0),
                _power: Number(car.power_hp || 0),
                _key: safeText(car.id || car.external_id || car.url || `${car.brand}-${car.model}-${car.full_title}`),
                _imageFailed: false,
            }));
    }

    function setHeroImage() {
        const hero = $('heroMedia');
        const image = state.cars.find(car => car._image)?._image;
        if (hero && image) hero.style.backgroundImage = `url("${image.replace(/"/g, '%22')}")`;
    }

    function updateMetrics() {
        const brands = new Set(state.cars.map(car => car.brand).filter(Boolean));
        const dates = state.cars
            .map(car => safeText(car.turnkey_calculation_date))
            .filter(Boolean)
            .sort();
        if ($('metricTotal')) $('metricTotal').textContent = RUB.format(state.cars.length);
        if ($('metricBrands')) $('metricBrands').textContent = RUB.format(brands.size);
        if ($('metricUpdated')) $('metricUpdated').textContent = dates.at(-1) || 'сегодня';
    }

    function fillBrandFilter() {
        const select = $('brandFilter');
        if (!select) return;
        const brands = [...new Set(state.cars.map(car => car.brand).filter(Boolean))]
            .sort((a, b) => a.localeCompare(b, 'ru'));
        select.replaceChildren(new Option('Все марки', ''));
        brands.forEach(brand => {
            select.appendChild(new Option(brand, brand));
        });
    }

    function fillModelFilter(brand = $('brandFilter')?.value || '') {
        const select = $('modelFilter');
        if (!select) return;

        const current = select.value;
        const models = [...new Set(
            state.cars
                .filter(car => !brand || car.brand === brand)
                .map(car => car.model)
                .filter(Boolean)
        )].sort((a, b) => a.localeCompare(b, 'ru'));

        select.replaceChildren(new Option('Все модели', ''));
        models.forEach(model => {
            select.appendChild(new Option(model, model));
        });
        select.value = models.includes(current) ? current : '';
    }

    function applyFilters() {
        const query = safeText($('searchInput')?.value).toLowerCase();
        const brand = $('brandFilter')?.value || '';
        const model = $('modelFilter')?.value || '';
        const budget = parseBudgetRange($('budgetFilter')?.value);
        const power = Number($('powerFilter')?.value || 0);
        const sort = $('sortFilter')?.value || 'turnkey_asc';

        let list = state.cars.filter(car => {
            if (query && !car._search.includes(query)) return false;
            if (brand && car.brand !== brand) return false;
            if (model && car.model !== model) return false;
            if (budget.min && (!car._turnkey || car._turnkey < budget.min)) return false;
            if (budget.max && (!car._turnkey || car._turnkey > budget.max)) return false;
            if (power && (!car._power || car._power > power)) return false;
            return true;
        });

        list.sort((a, b) => {
            if (sort === 'year_desc') return (b._year || 0) - (a._year || 0);
            if (sort === 'mileage_asc') return (a._mileage || Infinity) - (b._mileage || Infinity);
            return (a._turnkey || Infinity) - (b._turnkey || Infinity);
        });

        state.filtered = list;
        state.visible = PAGE_SIZE;
        render();
    }

    function createSpec(label, value) {
        const wrap = document.createElement('div');
        const dt = document.createElement('dt');
        const dd = document.createElement('dd');
        dt.textContent = label;
        dd.textContent = value || '—';
        wrap.append(dt, dd);
        return wrap;
    }

    function renderCard(car) {
        const template = $('offerCardTemplate');
        const node = template.content.firstElementChild.cloneNode(true);
        node.dataset.carKey = car._key;
        const image = node.querySelector('.as63-card__image');
        const badge = node.querySelector('.as63-card__badge');
        const brand = node.querySelector('.as63-card__brand');
        const title = node.querySelector('h3');
        const turnkey = node.querySelector('.as63-card__turnkey');
        const eur = node.querySelector('.as63-card__eur');
        const specs = node.querySelector('.as63-card__specs');
        const source = node.querySelector('.as63-card__source');
        const whatsapp = node.querySelector('.as63-card__whatsapp');

        image.src = car._image;
        image.alt = `${car.brand || ''} ${car.model || ''}`.trim() || car._title;
        image.dataset.imageIndex = '0';
        image.addEventListener('error', () => {
            const nextIndex = Number(image.dataset.imageIndex || 0) + 1;
            if (car._images[nextIndex]) {
                image.dataset.imageIndex = String(nextIndex);
                image.src = car._images[nextIndex];
                return;
            }
            car._imageFailed = true;
            state.renderedKeys.delete(car._key);
            node.remove();
            fillVisibleCards();
        });

        badge.textContent = car._power ? `${car._power} л.с.` : 'Europe';
        brand.textContent = [car.brand, car.model].filter(Boolean).join(' ');
        title.textContent = car._title;
        turnkey.textContent = formatRub(car._turnkey);
        eur.textContent = formatEur(car._price);

        specs.append(
            createSpec('Год', car.first_registration || car.first_registration_year || '—'),
            createSpec('Пробег', formatMileage(car._mileage)),
            createSpec('Топливо', car.fuel_type || '—'),
            createSpec('КПП', car.transmission || '—')
        );

        const sourceUrl = safeHttpUrl(car.url, '#');
        source.href = sourceUrl;
        source.textContent = 'Источник';

        const message = [
            'Здравствуйте! Интересует автомобиль Avtostok63 из Европы:',
            `${car.brand || ''} ${car.model || ''} ${car._title}`.trim(),
            `Цена под ключ: ${formatRub(car._turnkey)}`,
            `Источник: ${sourceUrl}`,
        ].join('\n');
        whatsapp.href = `https://wa.me/${CONTACT_PHONE}?text=${encodeURIComponent(message)}`;
        whatsapp.textContent = 'Заявка';
        return node;
    }

    function availableFilteredCars() {
        return state.filtered.filter(car => !car._imageFailed);
    }

    function updateOffersCount() {
        const count = $('offersCount');
        if (!count) return;
        count.textContent = `${RUB.format(availableFilteredCars().length)} предложений`;
    }

    function fillVisibleCards() {
        const grid = $('offersGrid');
        const more = $('showMoreBtn');
        if (!grid) return;

        const available = availableFilteredCars();
        updateOffersCount();

        const currentCount = grid.querySelectorAll('.as63-card').length;
        const target = Math.min(state.visible, available.length);
        if (!available.length) {
            grid.replaceChildren();
            const empty = document.createElement('div');
            empty.className = 'as63-empty';
            empty.textContent = 'По выбранным фильтрам предложений с фото не найдено';
            grid.appendChild(empty);
            if (more) more.hidden = true;
            return;
        }

        if (currentCount >= target) {
            if (more) more.hidden = state.visible >= available.length;
            return;
        }

        for (const car of available) {
            if (grid.querySelectorAll('.as63-card').length >= target) break;
            if (state.renderedKeys.has(car._key)) continue;
            state.renderedKeys.add(car._key);
            grid.appendChild(renderCard(car));
        }

        if (more) more.hidden = state.visible >= available.length;
    }

    function render() {
        const grid = $('offersGrid');
        const more = $('showMoreBtn');
        if (!grid) return;

        state.renderedKeys = new Set();
        updateOffersCount();
        grid.replaceChildren();

        if (!availableFilteredCars().length) {
            const empty = document.createElement('div');
            empty.className = 'as63-empty';
            empty.textContent = 'По выбранным фильтрам предложений с фото не найдено';
            grid.appendChild(empty);
            if (more) more.hidden = true;
            return;
        }

        fillVisibleCards();
    }

    function bindFilters() {
        const form = $('filtersForm');
        const inputs = ['searchInput', 'modelFilter', 'budgetFilter', 'powerFilter', 'sortFilter'];
        let timer = 0;
        const debounced = () => {
            clearTimeout(timer);
            timer = window.setTimeout(applyFilters, 160);
        };
        inputs.forEach(id => {
            const el = $(id);
            if (!el) return;
            el.addEventListener(id === 'searchInput' ? 'input' : 'change', debounced);
        });
        $('brandFilter')?.addEventListener('change', () => {
            fillModelFilter();
            debounced();
        });
        form?.addEventListener('reset', () => {
            window.setTimeout(() => {
                fillModelFilter('');
                applyFilters();
            }, 0);
        });
        $('showMoreBtn')?.addEventListener('click', () => {
            state.visible += PAGE_SIZE;
            render();
        });
    }

    async function init() {
        bindFilters();
        try {
            const response = await fetch(DATA_URL, { cache: 'no-store' });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            state.cars = normalizedCars(await response.json());
            state.filtered = [...state.cars].sort((a, b) => (a._turnkey || Infinity) - (b._turnkey || Infinity));
            fillBrandFilter();
            fillModelFilter();
            setHeroImage();
            updateMetrics();
            render();
        } catch (error) {
            const grid = $('offersGrid');
            const more = $('showMoreBtn');
            if (grid) {
                grid.replaceChildren();
                const message = document.createElement('div');
                message.className = 'as63-empty';
                message.textContent = location.protocol === 'file:'
                    ? 'Предложения загружаются через сайт. Откройте страницу по адресу http://localhost:8029/avtostok63-europe.html или на домене cmsauto.store.'
                    : `Не удалось загрузить предложения: ${safeText(error.message)}`;
                grid.appendChild(message);
            }
            if (more) more.hidden = true;
            if ($('offersCount')) $('offersCount').textContent = 'Ошибка загрузки';
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
