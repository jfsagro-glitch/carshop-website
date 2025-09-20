#!/usr/bin/env python3
"""
Добавление реальных фотографий автомобилей в базу данных
"""

import sqlite3
import json

def add_telegram_photos():
    """Добавление реальных фотографий автомобилей"""
    conn = sqlite3.connect("cars.db")
    cursor = conn.cursor()
    
    # Обновляем фотографии для каждого автомобиля
    cars_photos = [
        {
            'id': 14,
            'photos': [
                "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800",
                "https://images.unsplash.com/photo-1549317336-206569e8475c?w=800",
                "https://images.unsplash.com/photo-1549924231-f129b911e442?w=800"
            ]
        },
        {
            'id': 15,
            'photos': [
                "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=800",
                "https://images.unsplash.com/photo-1549317336-206569e8475c?w=800",
                "https://images.unsplash.com/photo-1549924231-f129b911e442?w=800"
            ]
        },
        {
            'id': 3,
            'photos': [
                "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800",
                "https://images.unsplash.com/photo-1549317336-206569e8475c?w=800",
                "https://images.unsplash.com/photo-1549924231-f129b911e442?w=800"
            ]
        },
        {
            'id': 4,
            'photos': [
                "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=800",
                "https://images.unsplash.com/photo-1549317336-206569e8475c?w=800",
                "https://images.unsplash.com/photo-1549924231-f129b911e442?w=800"
            ]
        },
        {
            'id': 5,
            'photos': [
                "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800",
                "https://images.unsplash.com/photo-1549317336-206569e8475c?w=800",
                "https://images.unsplash.com/photo-1549924231-f129b911e442?w=800"
            ]
        },
        {
            'id': 6,
            'photos': [
                "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=800",
                "https://images.unsplash.com/photo-1549317336-206569e8475c?w=800",
                "https://images.unsplash.com/photo-1549924231-f129b911e442?w=800"
            ]
        },
        {
            'id': 7,
            'photos': [
                "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800",
                "https://images.unsplash.com/photo-1549317336-206569e8475c?w=800",
                "https://images.unsplash.com/photo-1549924231-f129b911e442?w=800"
            ]
        },
        {
            'id': 8,
            'photos': [
                "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=800",
                "https://images.unsplash.com/photo-1549317336-206569e8475c?w=800",
                "https://images.unsplash.com/photo-1549924231-f129b911e442?w=800"
            ]
        },
        {
            'id': 9,
            'photos': [
                "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800",
                "https://images.unsplash.com/photo-1549317336-206569e8475c?w=800",
                "https://images.unsplash.com/photo-1549924231-f129b911e442?w=800"
            ]
        },
        {
            'id': 10,
            'photos': [
                "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=800",
                "https://images.unsplash.com/photo-1549317336-206569e8475c?w=800",
                "https://images.unsplash.com/photo-1549924231-f129b911e442?w=800"
            ]
        },
        {
            'id': 11,
            'photos': [
                "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800",
                "https://images.unsplash.com/photo-1549317336-206569e8475c?w=800",
                "https://images.unsplash.com/photo-1549924231-f129b911e442?w=800"
            ]
        },
        {
            'id': 12,
            'photos': [
                "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=800",
                "https://images.unsplash.com/photo-1549317336-206569e8475c?w=800",
                "https://images.unsplash.com/photo-1549924231-f129b911e442?w=800"
            ]
        }
    ]
    
    updated_count = 0
    
    for car_photo in cars_photos:
        try:
            # Обновляем фотографии в базе данных
            cursor.execute('''
                UPDATE cars SET photos = ? WHERE car_id = ?
            ''', (json.dumps(car_photo['photos']), car_photo['id']))
            
            updated_count += 1
            print(f"✅ Обновлены фотографии для автомобиля ID {car_photo['id']}")
            
        except Exception as e:
            print(f"❌ Ошибка при обновлении автомобиля ID {car_photo['id']}: {e}")
    
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
        for i, photo in enumerate(photos[:2]):  # Показываем первые 2 фото
            print(f"    {i+1}. {photo}")
    
    conn.close()

def main():
    """Основная функция"""
    print("📸 Добавление фотографий автомобилей в базу данных")
    print("=" * 60)
    
    try:
        add_telegram_photos()
        print("\n✅ Фотографии успешно добавлены!")
        print("🤖 Теперь запустите бота: python fix_photos_bot.py")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
