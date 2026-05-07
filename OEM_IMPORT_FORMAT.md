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

## Источники для усиления базы

Для полного покрытия нужны легальные выгрузки/API. На практике подходят:

- TecDoc / TecAlliance Web Service: кроссы, OE/OEM и применяемость.
- PartsTech / поставщик с API: прайсы и OEM/aftermarket кроссы.
- MOTOR Parts Data as a Service: структурированные данные по запчастям.
- Официальные EPC/дилерские выгрузки производителей.

Нормализованную JSON-выгрузку провайдера можно конвертировать:

```powershell
python tools\tecdoc_oem_import_stub.py --input provider_export.json --output supplier_oem_import.csv
python tools\import_oem_lookup.py --input supplier_oem_import.csv --source "Licensed provider export"
python generate_engines_catalog.py
python generate_parts_catalog.py --output generated_parts_catalog.csv
```
