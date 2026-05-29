(function () {
    'use strict';

    const DATA_URL = 'data/avtostok63_premium.json?v=20260529';
    const CONTACT_PHONE = '79178177711';
    const EUR = new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 0 });
    const RUB = new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 0 });

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

    function formatPrice(value) {
        const number = Number(value || 0);
        return number > 0 ? `${EUR.format(number)} €` : 'Цена по запросу';
    }

    function formatMileage(value) {
        const number = Number(value || 0);
        return number > 0 ? `${RUB.format(number)} км` : 'Новый';
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

    function normalize(rows) {
        return (rows || [])
            .filter(car => car && safeText(car.brand) && Array.isArray(car.images) && car.images.length)
            .map(car => ({
                ...car,
                _images: car.images.map(src => safeHttpUrl(src)).filter(Boolean),
                _title: safeText(car.title) || [car.brand, car.model].filter(Boolean).join(' '),
                _price: Number(car.price_eur || car.otd_price_eur || 0),
            }))
            .filter(car => car._images.length);
    }

    function renderCard(car) {
        const template = $('premiumCardTemplate');
        const node = template.content.firstElementChild.cloneNode(true);
        const image = node.querySelector('.as63-card__image');
        const badge = node.querySelector('.as63-card__badge');
        const brand = node.querySelector('.as63-card__brand');
        const title = node.querySelector('h3');
        const price = node.querySelector('.as63-card__turnkey');
        const subtitle = node.querySelector('.as63-card__eur');
        const specs = node.querySelector('.as63-card__specs');
        const source = node.querySelector('.as63-card__source');
        const whatsapp = node.querySelector('.as63-card__whatsapp');

        image.src = car._images[0];
        image.alt = `${car.brand || ''} ${car.model || ''}`.trim() || car._title;
        image.dataset.imageIndex = '0';
        image.addEventListener('error', () => {
            const nextIndex = Number(image.dataset.imageIndex || 0) + 1;
            if (car._images[nextIndex]) {
                image.dataset.imageIndex = String(nextIndex);
                image.src = car._images[nextIndex];
                return;
            }
            node.remove();
        });

        badge.textContent = safeText(car.status) || 'Premium';
        brand.textContent = [car.brand, car.model].filter(Boolean).join(' ');
        title.textContent = car._title;
        price.textContent = formatPrice(car.price_eur);
        subtitle.textContent = car.otd_price_eur ? `${formatPrice(car.otd_price_eur)} OTD` : 'Стоимость на источнике';

        specs.append(
            createSpec('Год', car.year || '—'),
            createSpec('Пробег', formatMileage(car.mileage)),
            createSpec('Топливо', car.fuel_type || '—'),
            createSpec('КПП', car.transmission || '—'),
            createSpec('Локация', car.location || '—'),
            createSpec('Состояние', car.condition || 'New')
        );

        const sourceUrl = safeHttpUrl(car.url, 'https://carexpo.group/catalog?status=in_stock&page=5');
        source.href = sourceUrl;

        const message = [
            'Здравствуйте! Интересует Premium автомобиль Avtostok63:',
            `${car.brand || ''} ${car.model || ''} ${car._title}`.trim(),
            `Цена: ${formatPrice(car.price_eur)}`,
            `Источник: ${sourceUrl}`,
        ].join('\n');
        whatsapp.href = `https://wa.me/${CONTACT_PHONE}?text=${encodeURIComponent(message)}`;
        return node;
    }

    function render(cars) {
        const grid = $('premiumGrid');
        if (!grid) return;
        grid.replaceChildren();

        if (!cars.length) {
            const empty = document.createElement('div');
            empty.className = 'as63-empty';
            empty.textContent = 'Premium предложения пока не загрузились';
            grid.appendChild(empty);
            return;
        }

        const fragment = document.createDocumentFragment();
        cars.forEach(car => fragment.appendChild(renderCard(car)));
        grid.appendChild(fragment);
    }

    async function init() {
        try {
            const response = await fetch(DATA_URL, { cache: 'no-store' });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const payload = await response.json();
            const cars = normalize(payload.cars);
            if ($('premiumCount')) $('premiumCount').textContent = `${RUB.format(cars.length)} premium`;
            render(cars);
        } catch (error) {
            const grid = $('premiumGrid');
            if ($('premiumCount')) $('premiumCount').textContent = 'Ошибка загрузки';
            if (grid) {
                const message = document.createElement('div');
                message.className = 'as63-empty';
                message.textContent = `Не удалось загрузить premium предложения: ${safeText(error.message)}`;
                grid.replaceChildren(message);
            }
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
