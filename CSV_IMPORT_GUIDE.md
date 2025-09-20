# 📥 Руководство по импорту данных из CSV

## 🎯 Обзор

Система поддерживает импорт данных об автомобилях из CSV файлов с автоматической обработкой фотографий.

## 📋 Формат CSV файла

### Обязательные поля

| Поле | Тип | Описание | Пример |
|------|-----|----------|---------|
| `id` | Integer | Уникальный ID автомобиля | `1` |
| `brand` | String | Бренд автомобиля | `Toyota` |
| `model` | String | Модель автомобиля | `Camry` |
| `year` | Integer | Год выпуска | `2020` |
| `price` | Integer | Цена в рублях | `2500000` |
| `mileage` | Integer | Пробег в км | `45000` |
| `fuel_type` | String | Тип топлива | `Бензин` |
| `transmission` | String | Тип КПП | `Автомат` |
| `color` | String | Цвет автомобиля | `Белый` |
| `description` | String | Описание | `Отличное состояние` |
| `photos` | String | URL фотографий через запятую | `url1,url2,url3` |

### Пример CSV файла

```csv
id,brand,model,year,price,mileage,fuel_type,transmission,color,description,photos
1,Toyota,Camry,2020,2500000,45000,Бензин,Автомат,Белый,"Отличное состояние, один владелец","https://example.com/camry1.jpg,https://example.com/camry2.jpg"
2,BMW,X5,2019,4200000,62000,Бензин,Автомат,Черный,"Премиум комплектация","https://example.com/x5_1.jpg,https://example.com/x5_2.jpg"
```

## 🚀 Способы импорта

### 1. Автоматический импорт при запуске

Бот автоматически проверяет наличие файла `cars_data.csv` при запуске и импортирует данные.

```bash
python run_bot.py
```

### 2. Ручной импорт через скрипт

```bash
python import_data.py
```

### 3. Импорт через команду бота

Администраторы могут использовать команду `/import` в Telegram боте.

### 4. Программный импорт

```python
from csv_importer import CarsCSVImporter

importer = CarsCSVImporter("cars_data.csv")
success = importer.import_to_database(clear_existing=True)
```

## 📸 Работа с фотографиями

### Поддерживаемые форматы URL

- HTTP/HTTPS ссылки на изображения
- Прямые ссылки на файлы изображений
- Ссылки на облачные хранилища

### Примеры URL фотографий

```
https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?w=800
https://example.com/car_photo.jpg
https://drive.google.com/file/d/123/view
```

### Ограничения

- Максимум 5 фотографий на автомобиль
- Поддерживаются форматы: JPG, PNG, GIF, WebP
- Рекомендуемый размер: 800x600 пикселей

## 🔧 Настройка импорта

### Параметры импорта

```python
importer = CarsCSVImporter(
    csv_file="cars_data.csv",  # Путь к CSV файлу
    db_path="cars.db"          # Путь к базе данных
)

# Очистить существующие данные
success = importer.import_to_database(clear_existing=True)

# Добавить к существующим данным
success = importer.import_to_database(clear_existing=False)
```

### Валидация данных

```python
# Проверка данных перед импортом
errors = importer.validate_csv_data()
if errors:
    print("Найдены ошибки:", errors)
```

### Статистика импорта

```python
stats = importer.get_import_statistics()
print(f"Всего автомобилей: {stats['total']}")
print(f"Бренды: {stats['brands']}")
print(f"Цены: {stats['price_range']['min']} - {stats['price_range']['max']}")
```

## ⚠️ Обработка ошибок

### Типичные ошибки

1. **Некорректный формат CSV**
   - Проверьте разделители (запятые)
   - Убедитесь в правильности кодировки (UTF-8)

2. **Некорректные данные**
   - Проверьте типы данных (числа, строки)
   - Убедитесь в корректности URL фотографий

3. **Проблемы с базой данных**
   - Проверьте права доступа к файлу базы данных
   - Убедитесь в отсутствии блокировок

### Логирование

Все операции импорта записываются в лог:

```bash
tail -f import.log
```

## 📊 Мониторинг импорта

### Проверка статуса

```python
from csv_importer import CarsCSVImporter

importer = CarsCSVImporter()
stats = importer.get_import_statistics()

print(f"Статус импорта:")
print(f"  Всего записей: {stats['total']}")
print(f"  Бренды: {', '.join(stats['brands'])}")
print(f"  Диапазон цен: {stats['price_range']['min']:,} - {stats['price_range']['max']:,} ₽")
```

### Проверка в базе данных

```sql
-- Количество автомобилей
SELECT COUNT(*) FROM cars;

-- Автомобили с фотографиями
SELECT brand, model, photos FROM cars WHERE photos != '[]';

-- Статистика по брендам
SELECT brand, COUNT(*) as count FROM cars GROUP BY brand;
```

## 🎯 Лучшие практики

### Подготовка данных

1. **Проверьте данные перед импортом**
2. **Используйте качественные фотографии**
3. **Убедитесь в уникальности ID**
4. **Проверьте корректность URL фотографий**

### Оптимизация

1. **Импортируйте данные пакетами**
2. **Используйте сжатие изображений**
3. **Регулярно очищайте неиспользуемые данные**

### Безопасность

1. **Проверяйте URL фотографий на безопасность**
2. **Используйте HTTPS для всех ссылок**
3. **Регулярно обновляйте данные**

## 🆘 Поддержка

При возникновении проблем:

1. Проверьте логи в файле `import.log`
2. Убедитесь в корректности формата CSV
3. Проверьте доступность URL фотографий
4. Обратитесь к документации по API

