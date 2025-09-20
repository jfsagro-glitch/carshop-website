#!/usr/bin/env python3
"""
Проверка фотографий в базе данных
"""

import sqlite3
import json

def check_photos_in_database():
    """Проверка фотографий в базе данных"""
    conn = sqlite3.connect("cars.db")
    cursor = conn.cursor()
    
    # Получаем все автомобили с фотографиями
    cursor.execute('SELECT car_id, brand, model, photos FROM cars WHERE photos IS NOT NULL AND photos != "[]"')
    cars_with_photos = cursor.fetchall()
    
    print(f"📊 Найдено {len(cars_with_photos)} автомобилей с фотографиями:")
    print("=" * 70)
    
    for car_id, brand, model, photos_json in cars_with_photos:
        try:
            photos = json.loads(photos_json) if isinstance(photos_json, str) else photos_json
            print(f"🚗 {brand} {model} (ID: {car_id})")
            print(f"   📸 Фотографий: {len(photos)}")
            for i, photo in enumerate(photos):
                print(f"   {i+1}. {photo}")
            print()
        except Exception as e:
            print(f"❌ Ошибка при обработке автомобиля {car_id}: {e}")
    
    # Проверяем общую статистику
    cursor.execute('SELECT COUNT(*) FROM cars')
    total_cars = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM cars WHERE photos IS NOT NULL AND photos != "[]"')
    cars_with_photos_count = cursor.fetchone()[0]
    
    print(f"📈 Статистика:")
    print(f"   Всего автомобилей: {total_cars}")
    print(f"   С фотографиями: {cars_with_photos_count}")
    print(f"   Процент с фото: {(cars_with_photos_count/total_cars*100):.1f}%")
    
    conn.close()

def main():
    """Основная функция"""
    print("🔍 Проверка фотографий в базе данных")
    print("=" * 50)
    
    try:
        check_photos_in_database()
        print("\n✅ Проверка завершена!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()



