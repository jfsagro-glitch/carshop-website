#!/usr/bin/env python3
"""
Импорт автомобилей с реальными фотографиями из CSV файла
"""

import sqlite3
import json
import re

def parse_car_name(name):
    """Парсинг названия автомобиля для извлечения марки, модели и года"""
    # Убираем лишние пробелы
    name = name.strip()
    
    # Ищем год в начале строки
    year_match = re.match(r'(\d{4})', name)
    if year_match:
        year = int(year_match.group(1))
        # Убираем год из названия
        name = name[4:].strip()
    else:
        year = 2020  # По умолчанию
    
    # Разделяем на марку и модель
    parts = name.split(',')
    if len(parts) >= 1:
        brand_model = parts[0].strip()
        # Разделяем марку и модель
        brand_model_parts = brand_model.split()
        if len(brand_model_parts) >= 2:
            brand = brand_model_parts[0]
            model = ' '.join(brand_model_parts[1:])
        else:
            brand = brand_model
            model = "Unknown"
    else:
        brand = name
        model = "Unknown"
    
    return brand, model, year

def parse_price(price_str):
    """Парсинг цены"""
    if not price_str:
        return 0
    
    # Убираем все кроме цифр
    price_clean = re.sub(r'[^\d]', '', price_str)
    try:
        return int(price_clean)
    except:
        return 0

def parse_mileage(mileage_str):
    """Парсинг пробега"""
    if not mileage_str:
        return 0
    
    # Убираем все кроме цифр
    mileage_clean = re.sub(r'[^\d]', '', mileage_str)
    try:
        return int(mileage_clean)
    except:
        return 0

def import_cars_with_photos():
    """Импорт автомобилей с фотографиями из CSV файла"""
    conn = sqlite3.connect("cars.db")
    cursor = conn.cursor()
    
    # Очищаем существующие данные
    cursor.execute('DELETE FROM cars')
    print("🗑️ Существующие данные очищены")
    
    imported_count = 0
    
    try:
        with open("cars_extended.csv", 'r', encoding='utf-8') as file:
            # Пропускаем заголовки
            next(file)  # Первая строка - описание
            next(file)  # Вторая строка - заголовки
            
            for line_num, line in enumerate(file, start=3):
                if not line.strip():
                    continue
                
                # Разделяем по точкам с запятой
                parts = line.strip().split(';')
                if len(parts) < 7:
                    continue
                
                try:
                    # Парсим данные
                    no = parts[0].strip()
                    name = parts[1].strip()
                    vin = parts[2].strip()
                    cost = parts[3].strip()
                    photos_url = parts[4].strip()
                    mileage = parts[5].strip()
                    production_date = parts[6].strip()
                    
                    # Парсим название автомобиля
                    brand, model, year = parse_car_name(name)
                    
                    # Парсим цену
                    price = parse_price(cost)
                    
                    # Парсим пробег
                    mileage_km = parse_mileage(mileage)
                    
                    # Обрабатываем фотографии
                    photos_list = []
                    if photos_url and 'drive.google.com' in photos_url:
                        photos_list = [photos_url]
                    
                    # Определяем тип двигателя по названию
                    engine_type = "Бензин"
                    if "AWD" in name:
                        engine_type = "Бензин AWD"
                    
                    # Определяем КПП
                    transmission = "Автомат"
                    if "1,6" in name or "1,5" in name:
                        transmission = "Автомат"
                    
                    # Определяем цвет (по умолчанию)
                    color = "Не указан"
                    
                    # Создаем описание
                    description = f"VIN: {vin}\nДата производства: {production_date}\nПробег: {mileage:,} км\nФотографии: {photos_url}"
                    
                    # Добавляем в базу данных
                    cursor.execute('''
                        INSERT INTO cars (user_id, brand, model, year, mileage, price,
                                       engine_type, transmission, color, description, photos, is_active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (1, brand, model, year, mileage_km, price, engine_type, 
                         transmission, color, description, json.dumps(photos_list), 1))
                    
                    imported_count += 1
                    print(f"✅ Импортирован: {brand} {model} ({year}) - {price:,} ₽")
                    print(f"   📸 Фото: {photos_url}")
                    
                except Exception as e:
                    print(f"❌ Ошибка в строке {line_num}: {e}")
                    continue
        
        conn.commit()
        print(f"\n🎉 Импорт завершен! Загружено {imported_count} автомобилей")
        
        # Показываем статистику
        cursor.execute('SELECT COUNT(*) FROM cars')
        total_cars = cursor.fetchone()[0]
        
        cursor.execute('SELECT brand, COUNT(*) FROM cars GROUP BY brand ORDER BY COUNT(*) DESC')
        brands = cursor.fetchall()
        
        print(f"\n📊 Статистика:")
        print(f"Всего автомобилей: {total_cars}")
        print(f"Марки:")
        for brand, count in brands:
            print(f"  {brand}: {count} шт.")
        
        # Показываем автомобили с фотографиями
        cursor.execute('SELECT brand, model, photos FROM cars WHERE photos != "[]"')
        cars_with_photos = cursor.fetchall()
        
        print(f"\n📸 Автомобили с фотографиями: {len(cars_with_photos)}")
        for brand, model, photos in cars_with_photos:
            photos_data = json.loads(photos)
            if photos_data:
                print(f"  {brand} {model}: {photos_data[0]}")
        
    except Exception as e:
        print(f"❌ Ошибка при импорте: {e}")
    finally:
        conn.close()

def main():
    """Основная функция"""
    print("🚗 Импорт автомобилей с фотографиями из CSV файла")
    print("=" * 60)
    
    try:
        import_cars_with_photos()
        print("\n✅ Импорт успешно завершен!")
        print("🤖 Теперь запустите бота: python simple_working_bot.py")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()





