(function () {
  'use strict';

  const DATA_URL = 'data/avtostok63_premium.json?v=20260621-expo-premium';
  const CONTACT_PHONE = '381631671218';
  const EUR = new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 0 });
  const KM = new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 0 });

  const $ = (id) => document.getElementById(id);

  function text(value) {
    return String(value ?? '').trim();
  }

  function safeUrl(value, fallback = '') {
    try {
      const url = new URL(String(value || ''), location.href);
      return ['http:', 'https:'].includes(url.protocol) ? url.href : fallback;
    } catch (_) {
      return fallback;
    }
  }

  function price(value, currency) {
    const amount = Number(value || 0);
    if (!amount) return 'Цена по запросу';
    const symbol = text(currency) || '€';
    return `${EUR.format(amount)} ${symbol}`;
  }

  function mileage(value) {
    const amount = Number(value || 0);
    return amount > 0 ? `${KM.format(amount)} км` : 'Новый';
  }

  function spec(label, value) {
    const wrap = document.createElement('div');
    const dt = document.createElement('dt');
    const dd = document.createElement('dd');
    dt.textContent = label;
    dd.textContent = value || '—';
    wrap.append(dt, dd);
    return wrap;
  }

  function normalize(payload) {
    return (payload?.cars || [])
      .filter((car) => car && text(car.brand) && Array.isArray(car.images))
      .map((car) => {
        const images = car.images.map((src) => safeUrl(src)).filter(Boolean);
        return {
          ...car,
          _images: images,
          _title: text(car.title) || [car.brand, car.model].filter(Boolean).join(' '),
          _source: safeUrl(car.url, 'https://carexpo.group/catalog?status=in_stock'),
          _sortPrice: Number(car.price_eur || car.otd_price_eur || 0),
        };
      })
      .filter((car) => car._images.length)
      .sort((a, b) => (b._sortPrice || 0) - (a._sortPrice || 0));
  }

  function renderCard(car) {
    const template = $('premiumCardTemplate');
    const node = template.content.firstElementChild.cloneNode(true);
    const media = node.querySelector('.premium-card__media');
    const image = node.querySelector('.premium-card__image');
    const badge = node.querySelector('.premium-card__badge');
    const brand = node.querySelector('.premium-card__brand');
    const title = node.querySelector('h3');
    const amount = node.querySelector('.premium-card__price');
    const subtitle = node.querySelector('.premium-card__subtitle');
    const specs = node.querySelector('.premium-card__specs');
    const source = node.querySelector('.premium-card__source');
    const whatsapp = node.querySelector('.premium-card__whatsapp');

    media.href = car._source;
    image.src = car._images[0];
    image.alt = `${car.brand || ''} ${car.model || ''}`.trim() || car._title;
    image.dataset.index = '0';
    image.addEventListener('error', () => {
      const next = Number(image.dataset.index || 0) + 1;
      if (car._images[next]) {
        image.dataset.index = String(next);
        image.src = car._images[next];
      } else {
        node.remove();
      }
    });

    badge.textContent = text(car.status) || 'Premium';
    brand.textContent = [car.brand, car.model].filter(Boolean).join(' ');
    title.textContent = car._title;
    amount.textContent = price(car.price_eur || car.otd_price_eur, car.currency);
    subtitle.textContent = car.otd_price_eur ? `${price(car.otd_price_eur, car.currency)} OTD` : 'Цена источника';
    specs.append(
      spec('Год', car.year || '—'),
      spec('Пробег', mileage(car.mileage)),
      spec('Топливо', car.fuel_type || '—'),
      spec('КПП', car.transmission || '—'),
      spec('Локация', car.location || '—'),
      spec('Состояние', car.condition || '—')
    );

    source.href = car._source;
    const message = [
      'Здравствуйте! Интересует Premium автомобиль EXPO MIR:',
      `${car.brand || ''} ${car.model || ''} ${car._title}`.trim(),
      `Цена: ${price(car.price_eur || car.otd_price_eur, car.currency)}`,
      `Источник: ${car._source}`,
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
      empty.className = 'premium-empty';
      empty.textContent = 'Premium предложения пока не загрузились';
      grid.append(empty);
      return;
    }
    const fragment = document.createDocumentFragment();
    cars.forEach((car) => fragment.append(renderCard(car)));
    grid.append(fragment);
  }

  async function init() {
    try {
      const response = await fetch(DATA_URL, { cache: 'no-store' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const payload = await response.json();
      const cars = normalize(payload);
      const label = `${KM.format(cars.length)} автомобилей`;
      if ($('premiumCount')) $('premiumCount').textContent = label;
      if ($('premiumHeroCount')) $('premiumHeroCount').textContent = `${label} в Premium-каталоге`;
      render(cars);
    } catch (error) {
      if ($('premiumCount')) $('premiumCount').textContent = 'Ошибка загрузки';
      if ($('premiumHeroCount')) $('premiumHeroCount').textContent = 'Каталог временно недоступен';
      const grid = $('premiumGrid');
      if (grid) {
        const empty = document.createElement('div');
        empty.className = 'premium-empty';
        empty.textContent = `Не удалось загрузить Premium-каталог: ${text(error.message)}`;
        grid.replaceChildren(empty);
      }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
