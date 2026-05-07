# OEM source audit

Проверка выполнена 07 мая 2026 инструментом:

```powershell
python tools\probe_oem_sources.py --workers 6
```

Результаты сохранены в `data/oem_source_probe.json`. Это технический аудит
доступности и robots.txt, а не разрешение на массовое копирование данных.
Оригинальные OEM-номера можно импортировать только из легального API, экспорта
поставщика, лицензированного EPC/TecDoc-источника или ручной VIN-проверки для
конкретной заявки.

## Итог по списку

- Всего проверено источников: 79.
- Предпочтительно API/экспорт: 9.
- Нужен аккаунт и проверка условий: 3.
- Доступен ручной lookup, массовый импорт не подтверждён: 35.
- Блокировка/авторизация: 5.
- Недоступно или нужна ручная проверка: 26.
- robots.txt запрещает массовый обход корня: 1.

## Лучшие кандидаты для API/экспорта

- `emex.ru` — поставщик/каталог, лучше брать партнёрский API или выгрузку.
- `rmsauto.ru` — отвечает 401, нужен партнёрский доступ/API.
- `fae.es` — датчики; полезно для пробелов `O2F/O2R/KNS/CTS/IAT`.
- `frenkit.es` — ремкомплекты суппортов; полезно для `CRK/CSG`.
- `seinsa.es` — ремкомплекты суппортов и цилиндров.
- `valeoservice.com` — Valeo; климат, электрика, сцепление.
- `webcat.zf.com` — ZF/Sachs/Boge/Lemforder; подвеска/трансмиссия.
- `fmecat.eu` — Federal-Mogul; моторные/тормозные позиции.
- `lpr.it` — тормоза/гидравлика.

## Аккаунт/условия перед импортом

- `public.servicebox.peugeot.com` — Peugeot Servicebox.
- `service.citroen.com` — Citroen Service.
- `b2b.shate-m.com` — B2B-каталоги производителей.

## Ручной VIN/EPC lookup, без подтверждённого bulk-импорта

Эти источники полезны менеджеру для проверки конкретной заявки по VIN/FRAME,
но их нельзя считать безопасным источником массовой выгрузки без отдельного
разрешения или API:

- `autodoc.ru`, `japancats.ru`, `elcats.ru`, `jedip.ru`, `parts66.ru`,
  `parts77.ru`, `auto2.ru`.
- `fordparts.com`, `realoem.com`, `bmwcats.com`, `new.lrcat.com`,
  `partsale.eu`, `trshop.audi.de`.
- `toyotacarmine.ru`, `kia.a-inside.ru`, `hyundai.a-inside.ru`,
  `hondaworld.ru`, `acurapartswarehouse.com`, `mitsubishi-autoparts.com.ua`.
- `findpart.org`, `rockauto.com`, `infodozer.com`, `avtobukvar.ru`,
  `motorzona.ru`, `podshipnik.in.ua`, `woodauto.com`.

## Нельзя использовать для автоматического bulk сейчас

- `epcdata.ru` — robots.txt не разрешил корневой обход для нашего audit-agent.
- `baxterautoparts.com`, `gmpartsdepartment.com`, `hondapartsdeals.com`,
  `oemfordpart.com`, `size.name` — 403/блокировка или авторизация.

## Практический план усиления OEM

1. Получить партнёрский API/CSV от Emex/RMSAuto/PartsTech или TecDoc.
2. Для датчиков, тормозов, подвески и трансмиссии запросить экспорт у FAE,
   Frenkit, Seinsa, ZF WebCat, Valeo, Federal-Mogul, LPR.
3. Загружать только структурированные CSV/JSON через:

```powershell
python tools\import_oem_lookup.py --input supplier_oem.csv --source "Supplier export"
python generate_engines_catalog.py
python generate_parts_catalog.py --output generated_parts_catalog.csv
python tools\audit_supabase_parts.py
```

4. После каждого импорта проверять вкладку `OEM база` в админке.
