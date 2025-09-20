#!/usr/bin/env python3
"""
Скрипт для импорта данных об автомобилях из CSV файла
"""

import os
import sys
import logging
from csv_importer import CarsCSVImporter

def setup_logging():
    """Настройка логирования"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('import.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Основная функция импорта"""
    print("🚗 Импорт данных об автомобилях")
    print("=" * 50)
    
    # Настройка логирования
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Проверяем наличие CSV файла
    csv_file = "cars_data.csv"
    if not os.path.exists(csv_file):
        print(f"❌ CSV файл {csv_file} не найден!")
        print("Создайте файл cars_data.csv с данными об автомобилях")
        return False
    
    # Создаем импортер
    importer = CarsCSVImporter(csv_file)
    
    # Валидация данных
    print("🔍 Проверка данных...")
    errors = importer.validate_csv_data()
    if errors:
        print("❌ Найдены ошибки в данных:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("✅ Данные валидны")
    
    # Статистика
    stats = importer.get_import_statistics()
    print(f"\n📊 Статистика:")
    print(f"  Всего автомобилей: {stats['total']}")
    print(f"  Бренды: {', '.join(stats['brands'])}")
    print(f"  Цены: {stats['price_range']['min']:,} - {stats['price_range']['max']:,} ₽")
    print(f"  Годы: {stats['years']['min']} - {stats['years']['max']}")
    
    # Импорт
    print(f"\n📥 Импорт данных...")
    success = importer.import_to_database(clear_existing=True)
    
    if success:
        print("✅ Импорт завершен успешно!")
        print(f"📁 Файл: {csv_file}")
        print(f"🗄️ База данных: cars.db")
        return True
    else:
        print("❌ Ошибка при импорте данных")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

