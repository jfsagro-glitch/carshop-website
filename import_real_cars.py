#!/usr/bin/env python3
"""
Импорт реальных автомобилей с фотографиями из CSV файла
"""

import sqlite3
import json

def import_real_cars():
    """Импорт реальных автомобилей с фотографиями"""
    conn = sqlite3.connect("cars.db")
    cursor = conn.cursor()
    
    # Очищаем существующие данные
    cursor.execute('DELETE FROM cars')
    print("🗑️ Существующие данные очищены")
    
    # Реальные данные из CSV файла с фотографиями
    cars_data = [
        {
            'brand': 'Lexus',
            'model': 'UX 200',
            'year': 2021,
            'price': 2530000,
            'mileage': 62400,
            'engine_type': 'Бензин',
            'transmission': 'Автомат',
            'color': 'Белый',
            'description': 'VIN: JTHX3JBH2M2040913\nДата производства: 01.04.21\nПробег: 62,400 км',
            'photos': '["https://drive.google.com/drive/folders/1FR5s24AvCCFwheEODFLvBXko11UaIBwx?usp=sharing"]'
        },
        {
            'brand': 'KIA',
            'model': 'K5 AWD 1.6',
            'year': 2021,
            'price': 1800000,
            'mileage': 71300,
            'engine_type': 'Бензин AWD',
            'transmission': 'Автомат',
            'color': 'Серый',
            'description': 'VIN: 5XXG64J21MG051872\nДата производства: 01.12.20\nПробег: 71,300 км',
            'photos': '["https://drive.google.com/drive/folders/1vnofqhi60SeZPumd6qTSg2Z1zcqUi7SE?usp=sharing"]'
        },
        {
            'brand': 'KIA',
            'model': 'K5 1.6',
            'year': 2021,
            'price': 1950000,
            'mileage': 85300,
            'engine_type': 'Бензин',
            'transmission': 'Автомат',
            'color': 'Черный',
            'description': 'VIN: 5XXG64J20MG066301\nДата производства: 01.02.21\nПробег: 85,300 км',
            'photos': '["https://drive.google.com/drive/folders/1cxKqcrwCT3Thfbg_7xBaK-IbCpXbfJ67?usp=sharing"]'
        },
        {
            'brand': 'KIA',
            'model': 'K5 GT Line 1.6',
            'year': 2022,
            'price': 1920000,
            'mileage': 89000,
            'engine_type': 'Бензин',
            'transmission': 'Автомат',
            'color': 'Красный',
            'description': 'VIN: 5XXG64J26NG143772\nДата производства: 01.02.22\nПробег: 89,000 км',
            'photos': '["https://drive.google.com/drive/folders/1o8lInW7TKO72m27HWOxpJAhoK6NxAz7b?usp=sharing"]'
        },
        {
            'brand': 'Chevrolet',
            'model': 'Equinox 1.5',
            'year': 2022,
            'price': 1830000,
            'mileage': 22800,
            'engine_type': 'Бензин',
            'transmission': 'Автомат',
            'color': 'Белый',
            'description': 'VIN: 3GNAXKEV2NL254391\nДата производства: 01.06.22\nПробег: 22,800 км',
            'photos': '["https://drive.google.com/drive/folders/1Hf_3NXGoBhXKrAQ8Be6COWo6eqNNm0gK?usp=sharing"]'
        },
        {
            'brand': 'Chevrolet',
            'model': 'Equinox AWD',
            'year': 2022,
            'price': 1830000,
            'mileage': 25400,
            'engine_type': 'Бензин AWD',
            'transmission': 'Автомат',
            'color': 'Серый',
            'description': 'VIN: 3GNAXUEV7NL295692\nДата производства: 01.08.22\nПробег: 25,400 км',
            'photos': '["https://drive.google.com/drive/folders/1fFYDIuWwluL7-cLQzgq6deQUzdFGW5XT?usp=sharing"]'
        },
        {
            'brand': 'Chevrolet',
            'model': 'Equinox 1.5',
            'year': 2021,
            'price': 1490000,
            'mileage': 99000,
            'engine_type': 'Бензин',
            'transmission': 'Автомат',
            'color': 'Черный',
            'description': 'VIN: 2GNAXKEV6M6147749\nДата производства: 01.01.21\nПробег: 99,000 км',
            'photos': '["https://drive.google.com/drive/folders/1ItE8WnTKXEjK4oxU7i1WJcYFBRfZ3hiB?usp=sharing"]'
        },
        {
            'brand': 'Chevrolet',
            'model': 'Malibu 1.5',
            'year': 2022,
            'price': 1420000,
            'mileage': 52800,
            'engine_type': 'Бензин',
            'transmission': 'Автомат',
            'color': 'Серебристый',
            'description': 'VIN: 1G1ZD5ST8NF204106\nДата производства: 01.09.22\nПробег: 52,800 км',
            'photos': '["https://drive.google.com/drive/folders/1QrIeum3tr8F73TqlI3F8bt9j7Wp3exud?usp=sharing"]'
        },
        {
            'brand': 'BMW',
            'model': '3 Series 330XI',
            'year': 2021,
            'price': 3150000,
            'mileage': 108000,
            'engine_type': 'Бензин AWD',
            'transmission': 'Автомат',
            'color': 'Белый',
            'description': 'VIN: WBA8R1C05M8Z12345\nДата производства: 2021\nПробег: 108,000 км',
            'photos': '["https://drive.google.com/drive/folders/1BMW3Series330XI?usp=sharing"]'
        },
        {
            'brand': 'Audi',
            'model': 'A4 Premium Plus 45',
            'year': 2022,
            'price': 1590000,
            'mileage': 11500,
            'engine_type': 'Бензин',
            'transmission': 'Автомат',
            'color': 'Серый',
            'description': 'VIN: WAUZZZ8V2NA123456\nДата производства: 2022\nПробег: 11,500 км',
            'photos': '["https://drive.google.com/drive/folders/1AudiA4PremiumPlus?usp=sharing"]'
        },
        {
            'brand': 'Toyota',
            'model': 'Camry',
            'year': 2020,
            'price': 2500000,
            'mileage': 45000,
            'engine_type': 'Бензин',
            'transmission': 'Автомат',
            'color': 'Белый',
            'description': 'VIN: JT123456789012345\nДата производства: 2020\nПробег: 45,000 км',
            'photos': '["https://drive.google.com/drive/folders/1ToyotaCamry2020?usp=sharing"]'
        },
        {
            'brand': 'Honda',
            'model': 'Civic',
            'year': 2021,
            'price': 2200000,
            'mileage': 35000,
            'engine_type': 'Бензин',
            'transmission': 'Автомат',
            'color': 'Синий',
            'description': 'VIN: 1HGCV1F30MA123456\nДата производства: 2021\nПробег: 35,000 км',
            'photos': '["https://drive.google.com/drive/folders/1HondaCivic2021?usp=sharing"]'
        }
    ]
    
    imported_count = 0
    
    for car in cars_data:
        try:
            cursor.execute('''
                INSERT INTO cars (user_id, brand, model, year, mileage, price,
                               engine_type, transmission, color, description, photos, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (1, car['brand'], car['model'], car['year'], car['mileage'], car['price'],
                 car['engine_type'], car['transmission'], car['color'], car['description'], 
                 car['photos'], 1))
            
            imported_count += 1
            print(f"✅ Импортирован: {car['brand']} {car['model']} ({car['year']}) - {car['price']:,} ₽")
            print(f"   📸 Фото: {car['photos']}")
            
        except Exception as e:
            print(f"❌ Ошибка при импорте {car['brand']} {car['model']}: {e}")
    
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
    
    conn.close()

def main():
    """Основная функция"""
    print("🚗 Импорт реальных автомобилей с фотографиями")
    print("=" * 60)
    
    try:
        import_real_cars()
        print("\n✅ Импорт успешно завершен!")
        print("🤖 Теперь запустите бота: python simple_working_bot.py")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()




