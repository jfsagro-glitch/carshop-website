"""
Модуль для импорта данных об автомобилях из CSV файла
"""

import csv
import json
import os
import sqlite3
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class CarsCSVImporter:
    """Класс для импорта автомобилей из CSV файла"""
    
    def __init__(self, csv_file: str = "cars_data.csv", db_path: str = "cars.db"):
        self.csv_file = csv_file
        self.db_path = db_path
    
    def read_csv_file(self) -> List[Dict]:
        """Чтение данных из CSV файла"""
        cars_data = []
        
        if not os.path.exists(self.csv_file):
            logger.error(f"CSV файл {self.csv_file} не найден")
            return cars_data
        
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Обработка фотографий
                    photos_str = row.get('photos', '')
                    if photos_str:
                        photos = [photo.strip() for photo in photos_str.split(',')]
                    else:
                        photos = []
                    
                    car_data = {
                        'id': int(row.get('id', 0)),
                        'brand': row.get('brand', '').strip(),
                        'model': row.get('model', '').strip(),
                        'year': int(row.get('year', 0)),
                        'price': int(row.get('price', 0)),
                        'mileage': int(row.get('mileage', 0)),
                        'fuel_type': row.get('fuel_type', '').strip(),
                        'transmission': row.get('transmission', '').strip(),
                        'color': row.get('color', '').strip(),
                        'description': row.get('description', '').strip(),
                        'photos': photos,
                        'is_available': True
                    }
                    cars_data.append(car_data)
            
            logger.info(f"Прочитано {len(cars_data)} автомобилей из CSV файла")
            return cars_data
            
        except Exception as e:
            logger.error(f"Ошибка чтения CSV файла: {e}")
            return []
    
    def import_to_database(self, clear_existing: bool = False) -> bool:
        """Импорт данных в базу данных"""
        try:
            # Читаем данные из CSV
            cars_data = self.read_csv_file()
            if not cars_data:
                logger.error("Нет данных для импорта")
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Очищаем существующие данные если нужно
            if clear_existing:
                cursor.execute('DELETE FROM cars')
                logger.info("Существующие данные очищены")
            
            # Импортируем данные
            imported_count = 0
            for car in cars_data:
                try:
                    # Проверяем, существует ли уже автомобиль с таким ID
                    cursor.execute('SELECT id FROM cars WHERE id = ?', (car['id'],))
                    if cursor.fetchone():
                        logger.warning(f"Автомобиль с ID {car['id']} уже существует, пропускаем")
                        continue
                    
                    # Преобразуем список фотографий в JSON
                    photos_json = json.dumps(car['photos'])
                    
                    cursor.execute('''
                        INSERT INTO cars (id, brand, model, year, price, mileage, fuel_type, 
                                       transmission, color, description, photos, is_available)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        car['id'], car['brand'], car['model'], car['year'], 
                        car['price'], car['mileage'], car['fuel_type'], 
                        car['transmission'], car['color'], car['description'], 
                        photos_json, car['is_available']
                    ))
                    imported_count += 1
                    
                except Exception as e:
                    logger.error(f"Ошибка импорта автомобиля {car['id']}: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
            logger.info(f"Успешно импортировано {imported_count} автомобилей")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка импорта в базу данных: {e}")
            return False
    
    def validate_csv_data(self) -> List[str]:
        """Валидация данных CSV файла"""
        errors = []
        cars_data = self.read_csv_file()
        
        for i, car in enumerate(cars_data, 1):
            # Проверка обязательных полей
            required_fields = ['brand', 'model', 'year', 'price']
            for field in required_fields:
                if not car.get(field):
                    errors.append(f"Строка {i}: отсутствует обязательное поле '{field}'")
            
            # Проверка числовых полей
            if car.get('year', 0) < 1990 or car.get('year', 0) > 2024:
                errors.append(f"Строка {i}: некорректный год выпуска {car.get('year')}")
            
            if car.get('price', 0) <= 0:
                errors.append(f"Строка {i}: некорректная цена {car.get('price')}")
            
            if car.get('mileage', 0) < 0:
                errors.append(f"Строка {i}: некорректный пробег {car.get('mileage')}")
        
        return errors
    
    def get_import_statistics(self) -> Dict:
        """Получение статистики импорта"""
        cars_data = self.read_csv_file()
        
        if not cars_data:
            return {"total": 0, "brands": [], "price_range": {"min": 0, "max": 0}}
        
        brands = list(set(car['brand'] for car in cars_data))
        prices = [car['price'] for car in cars_data]
        
        return {
            "total": len(cars_data),
            "brands": sorted(brands),
            "price_range": {
                "min": min(prices),
                "max": max(prices)
            },
            "years": {
                "min": min(car['year'] for car in cars_data),
                "max": max(car['year'] for car in cars_data)
            }
        }

def main():
    """Основная функция для импорта данных"""
    print("🚗 Импорт данных об автомобилях из CSV файла")
    print("=" * 50)
    
    # Настройка логирования
    logging.basicConfig(level=logging.INFO)
    
    importer = CarsCSVImporter()
    
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
        return True
    else:
        print("❌ Ошибка при импорте данных")
        return False

if __name__ == "__main__":
    main()

