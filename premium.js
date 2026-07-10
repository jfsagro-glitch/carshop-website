(function () {
  'use strict';

  const DATA_URL = 'data/avtostok63_premium.json?v=20260621-expo-premium';
  const CONTACT_PHONE = '381631671218';
  const EUR = new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 0 });
  const KM = new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 0 });
  let premiumCars = [];

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
      .filter((car) => car._images.length);
  }

  function uniqueValues(cars, field) {
    return [...new Set(cars.map((car) => text(car[field])).filter(Boolean))]
      .sort((a, b) => a.localeCompare(b, 'ru'));
  }

  function fillSelect(id, values, placeholder) {
    const select = $(id);
    if (!select) return;
    select.replaceChildren(new Option(placeholder, ''));
    values.forEach((value) => select.add(new Option(value, value)));
  }

  function populateModels() {
    const brand = $('premiumBrand')?.value || '';
    const cars = brand ? premiumCars.filter((car) => car.brand === brand) : premiumCars;
    fillSelect('premiumModel', uniqueValues(cars, 'model'), 'Все модели');
  }

  function populateFilters() {
    fillSelect('premiumBrand', uniqueValues(premiumCars, 'brand'), 'Все марки');
    populateModels();
    fillSelect('premiumTransmission', uniqueValues(premiumCars, 'transmission'), 'Любая');
    fillSelect('premiumFuel', uniqueValues(premiumCars, 'fuel_type'), 'Любой');
  }

  function filteredCars() {
    const brand = $('premiumBrand')?.value || '';
    const model = $('premiumModel')?.value || '';
    const search = text($('premiumSearch')?.value).toLowerCase();
    const priceFrom = Number($('premiumPriceFrom')?.value || 0);
    const priceTo = Number($('premiumPriceTo')?.value || 0);
    const transmission = $('premiumTransmission')?.value || '';
    const fuel = $('premiumFuel')?.value || '';
    const sort = $('premiumSort')?.value || 'price-desc';
    const result = premiumCars.filter((car) => {
      if (brand && car.brand !== brand) return false;
      if (model && car.model !== model) return false;
      if (transmission && car.transmission !== transmission) return false;
      if (fuel && car.fuel_type !== fuel) return false;
      if (priceFrom && car._sortPrice < priceFrom) return false;
      if (priceTo && car._sortPrice > priceTo) return false;
      if (search && !`${car.brand} ${car.model} ${car._title}`.toLowerCase().includes(search)) return false;
      return true;
    });
    return result.sort((a, b) => {
      if (sort === 'price-desc') return (b._sortPrice || 0) - (a._sortPrice || 0);
      if (sort === 'year-desc') return Number(b.year || 0) - Number(a.year || 0);
      return (a._sortPrice || Number.MAX_SAFE_INTEGER) - (b._sortPrice || Number.MAX_SAFE_INTEGER);
    });
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

    image.src = car._images[0];
    image.alt = `${car.brand || ''} ${car.model || ''}`.trim() || car._title;
    image.dataset.index = '0';
    const previous = node.querySelector('.premium-card__gallery-nav--prev');
    const next = node.querySelector('.premium-card__gallery-nav--next');
    const count = node.querySelector('.premium-card__photo-count');
    const dots = node.querySelector('.premium-card__gallery-dots');
    let imageIndex = 0;
    const updateGallery = (index) => {
      imageIndex = (index + car._images.length) % car._images.length;
      image.dataset.index = String(imageIndex);
      image.src = car._images[imageIndex];
      count.textContent = `${imageIndex + 1}/${car._images.length}`;
      dots.querySelectorAll('i').forEach((dot, dotIndex) => dot.classList.toggle('is-active', dotIndex === imageIndex));
    };
    if (car._images.length > 1) {
      count.textContent = `1/${car._images.length}`;
      dots.replaceChildren(...car._images.slice(0, 8).map((_, index) => {
        const dot = document.createElement('i');
        dot.className = index === 0 ? 'is-active' : '';
        return dot;
      }));
      previous.addEventListener('click', () => updateGallery(imageIndex - 1));
      next.addEventListener('click', () => updateGallery(imageIndex + 1));
      let startX = null;
      media.addEventListener('pointerdown', (event) => { startX = event.clientX; });
      media.addEventListener('pointerup', (event) => {
        if (startX === null) return;
        const distance = event.clientX - startX;
        if (Math.abs(distance) > 36) updateGallery(imageIndex + (distance < 0 ? 1 : -1));
        startX = null;
      });
      media.addEventListener('pointercancel', () => { startX = null; });
      media.addEventListener('touchstart', (event) => {
        startX = event.touches[0]?.clientX ?? null;
      }, { passive: true });
      media.addEventListener('touchend', (event) => {
        if (startX === null) return;
        const distance = (event.changedTouches[0]?.clientX ?? startX) - startX;
        if (Math.abs(distance) > 36) updateGallery(imageIndex + (distance < 0 ? 1 : -1));
        startX = null;
      }, { passive: true });
    } else {
      previous.hidden = true;
      next.hidden = true;
      count.hidden = true;
    }
    image.addEventListener('error', () => {
      const next = Number(image.dataset.index || 0) + 1;
      if (car._images[next]) {
        updateGallery(next);
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

  function updateCount(cars) {
    const label = `${KM.format(cars.length)} автомобилей`;
    if ($('premiumCount')) $('premiumCount').textContent = label;
  }

  function applyFilters() {
    const cars = filteredCars();
    updateCount(cars);
    render(cars);
  }

  function resetFilters() {
    ['premiumSearch', 'premiumPriceFrom', 'premiumPriceTo'].forEach((id) => { if ($(id)) $(id).value = ''; });
    ['premiumBrand', 'premiumModel', 'premiumTransmission', 'premiumFuel'].forEach((id) => { if ($(id)) $(id).value = ''; });
    if ($('premiumSort')) $('premiumSort').value = 'price-desc';
    populateModels();
    applyFilters();
  }

  function setupFilters() {
    $('premiumBrand')?.addEventListener('change', () => { populateModels(); applyFilters(); });
    $('premiumModel')?.addEventListener('change', applyFilters);
    $('premiumTransmission')?.addEventListener('change', applyFilters);
    $('premiumFuel')?.addEventListener('change', applyFilters);
    $('premiumSort')?.addEventListener('change', applyFilters);
    $('premiumApply')?.addEventListener('click', applyFilters);
    $('premiumReset')?.addEventListener('click', resetFilters);
    $('premiumSearch')?.addEventListener('input', applyFilters);
  }

  async function init() {
    try {
      const response = await fetch(DATA_URL, { cache: 'no-store' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const payload = await response.json();
      premiumCars = normalize(payload);
      const label = `${KM.format(premiumCars.length)} автомобилей`;
      if ($('premiumHeroCount')) $('premiumHeroCount').textContent = `${label} в Premium-каталоге`;
      populateFilters();
      setupFilters();
      applyFilters();
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
