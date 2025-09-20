#!/usr/bin/env python3
"""
Обновление фотографий автомобилей с правильными ID
"""

import sqlite3
import json

def update_car_photos():
    """Обновление фотографий автомобилей"""
    conn = sqlite3.connect("cars.db")
    cursor = conn.cursor()
    
    # Получаем все ID автомобилей
    cursor.execute('SELECT car_id FROM cars ORDER BY car_id')
    car_ids = [row[0] for row in cursor.fetchall()]
    
    print(f"Найдено {len(car_ids)} автомобилей: {car_ids}")
    
    # Фотографии для автомобилей
    photo_urls = [
        "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800",
        "https://images.unsplash.com/photo-1549317336-206569e8475c?w=800", 
        "https://images.unsplash.com/photo-1549924231-f129b911e442?w=800",
        "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=800",
        "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800",
        "https://images.unsplash.com/photo-1549317336-206569e8475c?w=800",
        "https://images.unsplash.com/photo-1549924231-f129b911e442?w=800",
        "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=800",
        "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800",
        "https://images.unsplash.com/photo-1549317336-206569e8475c?w=800",
        "https://images.unsplash.com/photo-1549924231-f129b911e442?w=800",
        "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=800"
    ]
    
    updated_count = 0
    
    for i, car_id in enumerate(car_ids):
        try:
            # Создаем массив фотографий для каждого автомобиля
            photos = [photo_urls[i % len(photo_urls)]]
            
            # Обновляем фотографии в базе данных
            cursor.execute('''
                UPDATE cars SET photos = ? WHERE car_id = ?
            ''', (json.dumps(photos), car_id))
            
            updated_count += 1
            print(f"✅ Обновлены фотографии для автомобиля ID {car_id}")
            
        except Exception as e:
            print(f"❌ Ошибка при обновлении автомобиля ID {car_id}: {e}")
    
    conn.commit()
    print(f"\n🎉 Обновление завершено! Обновлено {updated_count} автомобилей")
    
    # Показываем статистику
    cursor.execute('SELECT COUNT(*) FROM cars WHERE photos != "[]" AND photos IS NOT NULL')
    cars_with_photos = cursor.fetchone()[0]
    
    print(f"\n📊 Статистика:")
    print(f"Автомобилей с фотографиями: {cars_with_photos}")
    
    # Показываем примеры фотографий
    cursor.execute('SELECT car_id, brand, model, photos FROM cars WHERE photos != "[]" AND photos IS NOT NULL LIMIT 3')
    examples = cursor.fetchall()
    
    print(f"\n📸 Примеры фотографий:")
    for car_id, brand, model, photos_json in examples:
        photos = json.loads(photos_json)
        print(f"  {brand} {model}: {len(photos)} фото")
        for i, photo in enumerate(photos[:1]):  # Показываем первое фото
            print(f"    {i+1}. {photo}")
    
    conn.close()

def main():
    """Основная функция"""
    print("📸 Обновление фотографий автомобилей")
    print("=" * 50)
    
    try:
        update_car_photos()
        print("\n✅ Фотографии успешно обновлены!")
        print("🤖 Теперь запустите бота: python fix_photos_bot.py")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()



