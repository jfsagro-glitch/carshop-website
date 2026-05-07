# OEM import format

Каталог принимает только реальные OEM-номера из проверенных выгрузок поставщиков,
лицензируемых каталогов или API. Внутренние номера больше не генерируются.

## CSV

Минимальные колонки:

```csv
brand,prefix,part_code,oem_number,source
Toyota,TY,OF,04152-YZZA6,Toyota EPC export
Volkswagen,VW,BPF,5Q0-698-151-F,VAG catalog export
```

`brand` или `prefix` достаточно одного. `part_code` должен совпадать с кодом из
`data/parts_catalog.json` (`OF`, `BPF`, `RAD`, `EGR` и т.д.).

Импорт:

```powershell
python tools\import_oem_lookup.py --input supplier_oem.csv --source "Supplier / API name"
python tools\import_oem_lookup.py --input https://supplier.example/export/oem.csv --source "Supplier API export"
python generate_engines_catalog.py
python generate_parts_catalog.py --output generated_parts_catalog.csv
```

## JSON

```json
{
  "lookup": {
    "TY": {
      "OF": ["04152-YZZA6", "90915-YZZD4"]
    }
  }
}
```

## Контроль покрытия

```powershell
python tools\oem_coverage_report.py
python tools\audit_supabase_parts.py
```

Отчёт показывает покрытие по каждой марке и список полностью непокрытых типов
запчастей. Если для позиции нет реального OEM, сайт показывает `OEM по VIN`
вместо выдуманного номера.

Для админки используется JSON-отчёт:

```powershell
python tools\oem_coverage_report.py --json data\oem_coverage.json
```

`tools\import_oem_lookup.py` пересобирает этот отчёт автоматически после
успешного импорта, если не передан `--skip-report`.

## Источники для усиления базы

Для полного покрытия нужны легальные выгрузки/API. На практике подходят:

- TecDoc / TecAlliance Web Service: кроссы, OE/OEM и применяемость.
- PartsTech / поставщик с API: прайсы и OEM/aftermarket кроссы.
- MOTOR Parts Data as a Service: структурированные данные по запчастям.
- Официальные EPC/дилерские выгрузки производителей.

Аудит пользовательского списка онлайн-каталогов ведётся в `OEM_SOURCE_AUDIT.md`,
машинный результат проверки доступности — `data/oem_source_probe.json`.

## PartsTech Punchout

Ключи PartsTech не хранятся в репозитории. Для проверки доступа и создания
сессии подбора нужны все четыре значения из личного кабинета/API-договора:

```powershell
$env:PARTSTECH_PARTNER_ID="..."
$env:PARTSTECH_PARTNER_API_KEY="..."
$env:PARTSTECH_USER_ID="user@example.com"
$env:PARTSTECH_USER_API_KEY="..."
python tools\partstech_client.py --auth-test
```

Создание VIN-сессии подбора:

```powershell
python tools\partstech_client.py --vin "WVWZZZ..." --keyword "brake pad" --output data\partstech_session.json
```

Если поставщик отдаёт CSV/JSON-экспорт OEM-кроссов, его нужно импортировать
через `tools\import_oem_lookup.py`. Punchout-сессия сама по себе открывает
поиск/корзину поставщика, а не является полным скачиваемым EPC-справочником.

Нормализованную JSON-выгрузку провайдера можно конвертировать:

```powershell
python tools\tecdoc_oem_import_stub.py --input provider_export.json --output supplier_oem_import.csv
python tools\import_oem_lookup.py --input supplier_oem_import.csv --source "Licensed provider export"
python generate_engines_catalog.py
python generate_parts_catalog.py --output generated_parts_catalog.csv
```
