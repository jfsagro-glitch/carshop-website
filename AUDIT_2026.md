# EXPO MIR — Полный аудит проекта
**Дата:** 2026-05-21  
**Проект:** cmsauto.store — автомобильный маркетплейс  
**Стек:** Vanilla JS / CSS / HTML5, GitHub Pages, Supabase, PWA

---

## КРИТИЧЕСКИЕ ПРОБЛЕМЫ (SECURITY)

### SEC-01 — Утечка Supabase SERVICE ROLE KEY в коде
**Файл:** `supabase-client.js`, строки 7–8  
**Серьёзность:** КРИТИЧЕСКАЯ  
**Описание:** Supabase ANON_KEY захардкожен прямо в клиентском JS-файле, который индексируется поисковиками и виден в DevTools любого пользователя.  
```js
const SUPABASE_URL = 'https://jolyujjfxzhkswflqodz.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';
```
**Исправление:** Перенести ключи в переменные окружения (Netlify/Vercel env vars), или использовать серверный прокси. Минимум — ограничить ANON_KEY через Supabase RLS политики только разрешёнными операциями.

---

### SEC-02 — SERVICE ROLE KEY и хэш пароля в admin.html
**Файл:** `admin.html`, строки 158–165  
**Серьёзность:** КРИТИЧЕСКАЯ  
**Описание:** Инлайновый скрипт admin.html содержит Supabase SERVICE_ROLE key (полный доступ к БД, обход RLS) и хэш пароля администратора.  
**Исправление:** Немедленно сделать admin.html server-only (Basic Auth на уровне хостинга, или переместить в отдельный защищённый репозиторий). Ротировать SERVICE_ROLE key в Supabase Dashboard.

---

### SEC-03 — Credentials в git-репозитории
**Файлы:** `check_supabase.py`, `import_to_supabase.py`  
**Серьёзность:** КРИТИЧЕСКАЯ  
**Описание:** Python-скрипты содержат Supabase SERVICE_ROLE и ANON ключи хардкодом и НЕ добавлены в `.gitignore`. Ключи попали в git history и будут видны всем, кто клонирует репо.  
**Исправление:**
1. `echo "check_supabase.py\nimport_to_supabase.py\n*.env" >> .gitignore`
2. Ротировать оба ключа в Supabase Dashboard
3. Если репо публичное — удалить commits через `git filter-branch` или BFG Repo Cleaner

---

### SEC-04 — XSS через innerHTML
**Файл:** `script.js`, строки 2392–2439  
**Серьёзность:** ВЫСОКАЯ  
**Описание:** Telegram offer cards рендерятся через `element.innerHTML = \`...\`` с данными напрямую из внешнего источника без санитизации. Если данные из Supabase скомпрометированы или CORS-атака — XSS гарантирован.  
```js
container.innerHTML = offers.map(offer => `
    <div class="telegram-offer-card">
        <h3>${offer.title}</h3>  <!-- небезопасно -->
        <p>${offer.description}</p>  <!-- небезопасно -->
    </div>
`).join('');
```
**Исправление:** Заменить на `textContent` + DOM API, или использовать DOMPurify:
```js
element.textContent = offer.title; // безопасно
```

---

## ВЫСОКИЙ ПРИОРИТЕТ

### HIGH-01 — ETT таблица пустая (сломаны расчёты для юрлиц)
**Файл:** `src/features/customs-calculator/customsRates.js`, строки 161–165  
**Серьёзность:** ВЫСОКАЯ — функционал не работает  
**Описание:** `ETT_IMPORT_DUTY_RATES_PASSENGER_CAR` — массив пуст. TODO-комментарий: "fill confirmed ETT/TN VED rates for legal entities". Расчёт таможни по СТП (схема для юрлиц) полностью неработоспособен.  
**Исправление:** Заполнить таблицу актуальными ставками ЕАЭС 2026 (ТН ВЭД 87.03). Источник: ТК ЕАЭС и решения ЕЭК.

---

### HIGH-02 — Гонка условий при загрузке курсов валют
**Файл:** `script.js`, строки 26–45  
**Серьёзность:** ВЫСОКАЯ  
**Описание:** `updateAllDisplayedPrices()` вызывается до завершения async `loadUsdToRubRate()`. При медленном интернете цены отображаются в USD даже при выбранном RUB, пока не завершится fetch.  
**Исправление:** Await загрузки курса перед первым рендером цен. Показывать skeleton/spinner вместо неверных цен.

---

### HIGH-03 — Глобальный `state` без инкапсуляции
**Файл:** `script.js`, строки 3–15  
**Серьёзность:** ВЫСОКАЯ  
**Описание:** Весь стейт приложения — глобальные переменные в window scope. Любой скрипт (включая инжектированный) может изменить `state.currency`, `state.cart`, `state.filters` и т.д.  
**Исправление:** Обернуть в IIFE или ES6 Module с экспортом только публичного API.

---

### HIGH-04 — 437 КБ JSON без пагинации
**Файл:** `data/parts-catalog.json` (загружается в `parts-orders.js`)  
**Серьёзность:** ВЫСОКАЯ  
**Описание:** Весь каталог запчастей загружается одним запросом без lazy loading или пагинации. На мобильном 3G это 4–8 секунд блокировки.  
**Исправление:** Реализовать серверную пагинацию через Supabase (`.range(0, 49)`), или виртуальный скроллинг на клиенте.

---

### HIGH-05 — Поиск запчастей без debounce
**Файл:** `parts-orders.js` (поисковый обработчик)  
**Серьёзность:** ВЫСОКАЯ  
**Описание:** Каждый keydown при поиске по запчастям запускает синхронный фильтр по всему 437КБ массиву. На медленных устройствах — UI freeze.  
**Исправление:**
```js
const debouncedSearch = debounce(searchParts, 300);
searchInput.addEventListener('input', debouncedSearch);
```

---

### HIGH-06 — europe-orders.html: 637 строк inline CSS + 318 строк inline JS
**Файл:** `europe-orders.html`  
**Серьёзность:** ВЫСОКАЯ — нарушение DRY, CSP, кэширования  
**Описание:** Страница европейских заказов содержит сотни строк стилей и скриптов прямо в HTML. Это дублирует логику из общих файлов, блокирует кэширование браузером и не позволяет применить Content-Security-Policy.  
**Исправление:** Вынести в `europe-orders.css` и `europe-orders.js`.

---

## СРЕДНИЙ ПРИОРИТЕТ

### MED-01 — 519 деклараций `!important` в CSS
**Файлы:** `premium-enhancements.css` (~487), `styles.css` (~32)  
**Серьёзность:** СРЕДНЯЯ  
**Описание:** Два CSS-файла находятся в "войне специфичности". `premium-enhancements.css` переопределяет практически всё через `!important`, делая любой новый стиль практически невозможным без ещё одного `!important`.  
**Исправление:** Рефакторинг: объединить файлы, правильно использовать CSS-каскад и специфичность селекторов.

---

### MED-02 — Z-index хаос (диапазон 0–100,000)
**Файлы:** `styles.css`, `premium-enhancements.css`  
**Серьёзность:** СРЕДНЯЯ  
**Описание:** Z-index значения: 0, 1, 10, 100, 999, 1000, 9999, 10000, 100000. Нет стекинг-системы. Добавление нового оверлея — угадайка.  
**Исправление:** Завести CSS-переменные:
```css
:root {
    --z-base: 0;
    --z-dropdown: 100;
    --z-sticky: 200;
    --z-modal: 300;
    --z-toast: 400;
}
```

---

### MED-03 — `will-change` на 14+ элементах
**Файлы:** `premium-enhancements.css`  
**Серьёзность:** СРЕДНЯЯ  
**Описание:** `will-change: transform` и `will-change: opacity` применены к 14+ элементам одновременно. Браузер держит все в GPU-памяти — memory leak на мобильных.  
**Исправление:** Применять `will-change` только динамически через JS на время анимации, снимать после завершения.

---

### MED-04 — 4 дублирующихся `@keyframes`
**Файлы:** `styles.css`, `premium-enhancements.css`  
**Серьёзность:** СРЕДНЯЯ  
**Описание:** `@keyframes fadeInUp`, `@keyframes slideIn`, `@keyframes pulse`, `@keyframes glow` определены дважды. Второе определение молча перезаписывает первое.  
**Исправление:** Убрать дубли, оставить в одном файле.

---

### MED-05 — Нет hreflang тегов
**Затронуты:** Все 11 HTML-страниц  
**Серьёзность:** СРЕДНЯЯ — потери SEO  
**Описание:** Сайт поддерживает 5 языков (RU, EN, KY, DE, KA) через JS, но `<link rel="alternate" hreflang="...">` отсутствует. Google не знает о языковых версиях.  
**Исправление:** Добавить hreflang в `<head>` каждой страницы для всех 5 языков.

---

### MED-06 — sitemap.xml: дубль и устаревшие даты
**Файл:** `sitemap.xml`  
**Серьёзность:** СРЕДНЯЯ  
**Описание:**
- `georgia-stock.html` встречается дважды (строки 5 и 6)
- Все `<lastmod>` датированы 2026-05-04 — не обновляются автоматически  
**Исправление:** Удалить дубль. Настроить скрипт обновления lastmod при деплое.

---

### MED-07 — robots.txt: дублирующийся Allow
**Файл:** `robots.txt`  
**Серьёзность:** НИЗКАЯ/СРЕДНЯЯ  
**Описание:** `Allow: /georgia-stock` встречается дважды (строки 5 и 6).  
**Исправление:** Удалить одну строку.

---

### MED-08 — supabase-client.js отсутствует в SW precache
**Файл:** `sw.js`  
**Серьёзность:** СРЕДНЯЯ  
**Описание:** Service Worker кэширует 26 assets, но `supabase-client.js` в списке нет. При офлайн-режиме Supabase-запросы упадут даже с кэшированным контентом.  
**Исправление:** Добавить `'supabase-client.js'` в `PRECACHE_URLS` массив в `sw.js`.

---

### MED-09 — Нет honeypot полей в формах (защита от ботов)
**Затронуты:** Все 10 форм на 8 страницах  
**Серьёзность:** СРЕДНЯЯ  
**Описание:** Ни одна форма не имеет honeypot полей или rate limiting. Формы заказов уязвимы к spam-ботам.  
**Исправление:** Добавить скрытое поле `<input name="website" style="display:none">` и проверять его на стороне обработчика.

---

### MED-10 — Отсутствие обработки ошибок в fetch
**Файл:** `script.js`, строки 858–891 (`decodeVin`)  
**Серьёзность:** СРЕДНЯЯ  
**Описание:** VIN-декодер не обрабатывает сетевые ошибки. При недоступном API пользователь видит пустой контейнер без объяснений.  
**Исправление:** Добавить `try/catch` с информативным сообщением об ошибке.

---

## НИЗКИЙ ПРИОРИТЕТ

### LOW-01 — Service Worker: hardcoded cache version
**Файл:** `sw.js`  
**Серьёзность:** НИЗКАЯ  
**Описание:** `const CACHE_NAME = 'expo-mir-pwa-v6-home-georgia-stock'` — захардкожено. При обновлении файлов нужно вручную менять версию, иначе пользователи получат старый кэш.  
**Исправление:** Автоматически генерировать версию из git hash или timestamp при сборке/деплое.

---

### LOW-02 — `<title>` не локализован
**Затронуты:** Все страницы  
**Серьёзность:** НИЗКАЯ  
**Описание:** Заголовок вкладки всегда на русском. При переключении языка через JS `<title>` не меняется.  
**Исправление:** Обновлять `document.title` в `applyTranslations()`.

---

### LOW-03 — Отсутствует `lang` атрибут на `<html>`
**Затронуты:** Некоторые страницы  
**Серьёзность:** НИЗКАЯ — доступность, SEO  
**Описание:** `<html lang="ru">` должен обновляться при смене языка пользователем.  
**Исправление:** `document.documentElement.lang = newLanguage;` в обработчике смены языка.

---

### LOW-04 — Нет `<meta name="robots">` на admin.html
**Файл:** `admin.html`  
**Серьёзность:** НИЗКАЯ/ВЫСОКАЯ (безопасность)  
**Описание:** Страница администратора может быть проиндексирована Google.  
**Исправление:** Добавить `<meta name="robots" content="noindex, nofollow">` и добавить в robots.txt: `Disallow: /admin.html`.

---

### LOW-05 — Нет `loading="lazy"` на изображениях
**Затронуты:** Страницы с галереями (georgia-catalog, korea-orders и др.)  
**Серьёзность:** НИЗКАЯ  
**Описание:** Все `<img>` без `loading="lazy"`. LCP (Largest Contentful Paint) деградирует на страницах с большим количеством изображений.  
**Исправление:** `<img src="..." loading="lazy" alt="...">` для всех изображений ниже fold.

---

### LOW-06 — CSS: конфликт fixed height vs aspect-ratio (ИСПРАВЛЕНО)
**Файлы:** `styles.css`, `premium-enhancements.css`  
**Статус:** ✅ ИСПРАВЛЕНО в текущей сессии  
**Описание:** `.car-image` имел одновременно `height: 480px` и `aspect-ratio: 4/3` — противоречие. Исправлено: убраны все фиксированные высоты, оставлен только `aspect-ratio: 4/3`.

---

### LOW-07 — Modal close кнопки как `<span>` (ИСПРАВЛЕНО)
**Файлы:** Все 9 HTML-страниц  
**Статус:** ✅ ИСПРАВЛЕНО в текущей сессии  
**Описание:** `<span class="close">` не фокусируем с клавиатуры, не является кнопкой для screen readers. Исправлено: заменены на `<button class="close" aria-label="Закрыть">`.

---

### LOW-08 — Orphaned CSS блок без селектора (ИСПРАВЛЕНО)
**Файл:** `premium-enhancements.css`, ~строка 3104  
**Статус:** ✅ ИСПРАВЛЕНО в текущей сессии  
**Описание:** 5 CSS-деклараций без открывающего селектора. Исправлено: добавлен `.korea-card__img-wrap {`.

---

### LOW-09 — Неудобочитаемый текст на тёмном фоне (ИСПРАВЛЕНО)
**Файл:** `premium-enhancements.css`  
**Статус:** ✅ ИСПРАВЛЕНО в текущей сессии  
**Описание:** 6 селекторов использовали `#64748b` на тёмном фоне `#0a0e1a` (contrast ratio < 3:1). Исправлено: изменено на `#94a3b8`.

---

### LOW-10 — LED-баннер не отключается при prefers-reduced-motion (ИСПРАВЛЕНО)
**Файл:** `premium-enhancements.css`  
**Статус:** ✅ ИСПРАВЛЕНО в текущей сессии  
**Описание:** `ledGlow` 3s infinite и `ledScan` 2s infinite не были включены в `@media (prefers-reduced-motion: reduce)`. Исправлено.

---

## ПРОИЗВОДИТЕЛЬНОСТЬ

### PERF-01 — Нет code splitting / bundling
**Описание:** 7 больших JS-файлов загружаются последовательно. `script.js` (4,766 строк) — 120+ КБ не минифицированного JS.  
**Рекомендация:** Даже без сборщика можно разбить на модули с `type="module"` и использовать dynamic `import()` для некритических фич (VIN, калькулятор).

---

### PERF-02 — Нет минификации CSS/JS
**Описание:** Суммарный CSS: ~6,500 строк (styles.css + premium-enhancements.css). Не минифицирован.  
**Рекомендация:** Добавить шаг сборки (даже простой npm скрипт с `cssnano` + `terser`) или использовать Cloudflare Pages с автоминификацией.

---

### PERF-03 — Нет Resource Hints
**Описание:** Отсутствуют `<link rel="preconnect">` для Supabase домена, `<link rel="preload">` для критических шрифтов.  
**Исправление:**
```html
<link rel="preconnect" href="https://jolyujjfxzhkswflqodz.supabase.co">
<link rel="preload" href="styles.css" as="style">
```

---

## СВОДНАЯ ТАБЛИЦА ПРИОРИТЕТОВ

| ID | Приоритет | Файл | Строки | Описание |
|----|-----------|------|--------|----------|
| SEC-01 | 🔴 КРИТИК | supabase-client.js | 7–8 | ANON_KEY в публичном коде |
| SEC-02 | 🔴 КРИТИК | admin.html | 158–165 | SERVICE_ROLE KEY + password hash |
| SEC-03 | 🔴 КРИТИК | *.py | — | Credentials в git history |
| SEC-04 | 🟠 ВЫСОК | script.js | 2392–2439 | XSS через innerHTML |
| HIGH-01 | 🟠 ВЫСОК | customsRates.js | 161–165 | ETT таблица пуста |
| HIGH-02 | 🟠 ВЫСОК | script.js | 26–45 | Race condition при курсах |
| HIGH-03 | 🟠 ВЫСОК | script.js | 3–15 | Глобальный state |
| HIGH-04 | 🟠 ВЫСОК | parts-orders.js | — | 437КБ JSON без пагинации |
| HIGH-05 | 🟠 ВЫСОК | parts-orders.js | — | Поиск без debounce |
| HIGH-06 | 🟠 ВЫСОК | europe-orders.html | — | 637 строк inline CSS |
| MED-01 | 🟡 СРЕД | *.css | — | 519 !important |
| MED-02 | 🟡 СРЕД | *.css | — | Z-index 0–100000 |
| MED-03 | 🟡 СРЕД | premium-*.css | — | will-change на 14+ элем |
| MED-04 | 🟡 СРЕД | *.css | — | 4 дубля @keyframes |
| MED-05 | 🟡 СРЕД | все страницы | — | Нет hreflang |
| MED-06 | 🟡 СРЕД | sitemap.xml | — | Дубль + устаревшие даты |
| MED-07 | 🟡 СРЕД | robots.txt | 5–6 | Дублирующийся Allow |
| MED-08 | 🟡 СРЕД | sw.js | — | supabase-client.js не кэширован |
| MED-09 | 🟡 СРЕД | все формы | — | Нет honeypot |
| MED-10 | 🟡 СРЕД | script.js | 858–891 | Нет обработки ошибок VIN |
| LOW-01 | 🟢 НИЗ | sw.js | 1 | Хардкод версии кэша |
| LOW-02 | 🟢 НИЗ | все страницы | — | title не локализован |
| LOW-03 | 🟢 НИЗ | все страницы | — | lang атрибут не обновляется |
| LOW-04 | 🟢 НИЗ | admin.html | head | Нет noindex |
| LOW-05 | 🟢 НИЗ | галереи | — | Нет loading="lazy" |
| PERF-01 | 🟢 НИЗ | script.js | — | Нет code splitting |
| PERF-02 | 🟢 НИЗ | *.css, *.js | — | Нет минификации |
| PERF-03 | 🟢 НИЗ | все страницы | — | Нет resource hints |

---

## ИСПРАВЛЕНО В ТЕКУЩЕЙ СЕССИИ

| # | Проблема | Файлы |
|---|----------|-------|
| 1 | Пропорциональные изображения авто (aspect-ratio vs fixed height) | styles.css, premium-enhancements.css |
| 2 | Modal close: `<span>` → `<button aria-label="Закрыть">` | 9 HTML файлов |
| 3 | Orphaned CSS блок без селектора | premium-enhancements.css ~3104 |
| 4 | Тёмный текст на тёмном фоне (6 селекторов) | premium-enhancements.css |
| 5 | LED-баннер в prefers-reduced-motion | premium-enhancements.css |
| 6 | Mobile 480px: 1-column grid | styles.css |
| 7 | :focus-visible стили | premium-enhancements.css |
| 8 | footer-bottom__note читаемость | premium-enhancements.css |
| 9 | Убран публичный service-role key и password hash из admin.html; админка отключена на static-хостинге | admin.html |
| 10 | Убраны hardcoded Supabase service/anon keys из диагностических Python-скриптов | check_supabase.py, import_to_supabase.py, check_supabase_import.py |
| 11 | Защита Telegram offer ссылок/картинок от небезопасных URL-схем | script.js |
| 12 | Удалён дубль Allow в robots.txt | robots.txt |

> Важно: правки кода не ротируют уже скомпрометированные ключи. Ротацию `anon` и `service_role` нужно выполнить в Supabase Dashboard, затем проверить RLS.

---

## РЕКОМЕНДУЕМЫЙ ПОРЯДОК ДЕЙСТВИЙ

1. **Немедленно:** Ротировать ВСЕ Supabase ключи (SEC-01, SEC-02, SEC-03)
2. **Сегодня:** Добавить `*.py` в `.gitignore`, защитить `admin.html` (noindex + auth)
3. **На этой неделе:** Исправить XSS в innerHTML (SEC-04), заполнить ETT таблицу (HIGH-01)
4. **В следующей итерации:** Debounce поиска, пагинация запчастей, исправить race condition курсов
5. **Технический долг:** Рефакторинг CSS (убрать !important войны), z-index система
