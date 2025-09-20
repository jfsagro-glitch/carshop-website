#!/usr/bin/env python3
"""
Обновление фотографий автомобилей с реальными ссылками из Google Drive
"""

import sqlite3
import json

def update_real_car_photos():
    """Обновление фотографий автомобилей с реальными ссылками"""
    conn = sqlite3.connect("cars.db")
    cursor = conn.cursor()
    
    # Получаем все ID автомобилей
    cursor.execute('SELECT car_id FROM cars ORDER BY car_id')
    car_ids = [row[0] for row in cursor.fetchall()]
    
    print(f"Найдено {len(car_ids)} автомобилей: {car_ids}")
    
    # Реальные ссылки на фотографии из Google Drive
    real_photo_urls = [
        "https://drive.google.com/drive/folders/1FR5s24AvCCFwheEODFLvBXko11UaIBwx?usp=sharing",
        "https://drive.google.com/drive/folders/1vnofqhi60SeZPumd6qTSg2Z1zcqUi7SE?usp=sharing",
        "https://drive.google.com/drive/folders/1cxKqcrwCT3Thfbg_7xBaK-IbCpXbfJ67?usp=sharing",
        "https://drive.google.com/drive/folders/1o8lInW7TKO72m27HWOxpJAhoK6NxAz7b?usp=sharing",
        "https://drive.google.com/drive/folders/1Hf_3NXGoBhXKrAQ8Be6COWo6eqNNm0gK?usp=sharing",
        "https://drive.google.com/drive/folders/1fFYDIuWwluL7-cLQzgq6deQUzdFGW5XT?usp=sharing",
        "https://drive.google.com/drive/folders/1ItE8WnTKXEjK4oxU7i1WJcYFBRfZ3hiB?usp=sharing",
        "https://drive.google.com/drive/folders/1QrIeum3tr8F73TqlI3F8bt9j7Wp3exud?usp=sharing",
        "https://drive.google.com/drive/folders/1SLPy7kA6U3GHvmaWMCv1aLV1hgJp78ht?usp=sharing",
        "https://drive.google.com/drive/folders/1AneTIy_JInzve71jMfyHRAaMmdmv0p9e?usp=sharing",
        "https://drive.google.com/drive/folders/1fndY8K0rjlF0JbqnNSl7KRF-kvpyfElP?usp=sharing",
        "https://drive.google.com/drive/folders/1vI6ngtd-7pS-Q6GZyx3cT1TAbLP02cJ2?usp=sharing",
        "https://drive.google.com/drive/folders/1ktbbcV03TNaxOo85hcxdRI12cf48PDlA?usp=sharing",
        "https://drive.google.com/drive/folders/1T_WJeiasoMStwqfsrrKCQMrqhauDO2HV?usp=sharing",
        "https://drive.google.com/drive/folders/11m3ri2m9na7jmqV-Zf2gRwhoXTga4Ruo?usp=sharing",
        "https://drive.google.com/drive/folders/1wbbCZ90K5ph9vunmCnuQJTxSx2sqxQ8n?usp=sharing",
        "https://drive.google.com/drive/folders/1lts5r3t6ftPayg55mjSHdMbwRBGMoz78?usp=sharing",
        "https://drive.google.com/drive/folders/18gkgVMN3UWPXSSVtB73M1SUxj7Sd6BpG?usp=sharing",
        "https://drive.google.com/drive/folders/1PMVX5wAq0amBEmIotp7DN0Xfvpb1bPHU?usp=sharing",
        "https://drive.google.com/drive/folders/1PV5UOJxvCIn52_qrxFJdcvcWuiyE3yM4?usp=sharing",
        "https://drive.google.com/drive/folders/1lkew_BKZI_6xKdInzK4JKEpzgRNsHl3H?usp=sharing",
        "https://drive.google.com/drive/folders/1PpnoOBW5SxQvATGHODbNrDco5SBFXgAc?usp=sharing",
        "https://drive.google.com/drive/folders/1bv6Te0NZyRaskQVJ1bYJItgprQMYlbAZ?usp=sharing",
        "https://drive.google.com/drive/folders/1P4HH2NfEva269zYtUZsFSfzeQxQfpzYG?usp=sharing",
        "https://drive.google.com/drive/folders/1u9kNrW8mwUnRMku1O4hjx3bdVHcyCpKI?usp=sharing",
        "https://drive.google.com/drive/folders/1m4mktjJLI0feWy8EtHAuEBZB5OetMWqg?usp=sharing",
        "https://drive.google.com/drive/folders/1cZ0NU_NfNc8VKCBdRklkQBETifuKhMLe?usp=sharing",
        "https://drive.google.com/drive/folders/1G3wdYypzFOTNVuuUFiXwKnXZtu5y5VXl?usp=sharing",
        "https://drive.google.com/drive/folders/1dAJ-gcvjwwYCN8kO7wAIFIdCJcjEnRqG?usp=sharing",
        "https://drive.google.com/drive/folders/1os_egVR07QtwJMgWaN6SHWNz5ntSiwaO?usp=sharing",
        "https://drive.google.com/drive/folders/17TPAkN76U8TCT_l81FJbnpHJLyQGcwo2?usp=sharing",
        "https://drive.google.com/drive/folders/12IE_Wr0f6VJ3h5wiFnyCQnzYhu8Fxgyu?usp=sharing",
        "https://drive.google.com/drive/folders/1hmGbI2RO3F72KXOX8EkYXoMq6uHxISgl?usp=sharing"
    ]
    
    updated_count = 0
    
    for i, car_id in enumerate(car_ids):
        try:
            # Используем реальные ссылки на фотографии
            if i < len(real_photo_urls):
                photos = [real_photo_urls[i]]
            else:
                # Если автомобилей больше чем ссылок, используем последнюю ссылку
                photos = [real_photo_urls[-1]]
            
            # Обновляем фотографии в базе данных
            cursor.execute('''
                UPDATE cars SET photos = ? WHERE car_id = ?
            ''', (json.dumps(photos), car_id))
            
            updated_count += 1
            print(f"✅ Обновлены фотографии для автомобиля ID {car_id}")
            print(f"   📸 Фото: {photos[0]}")
            
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
    cursor.execute('SELECT car_id, brand, model, photos FROM cars WHERE photos != "[]" AND photos IS NOT NULL LIMIT 5')
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
    print("📸 Обновление фотографий автомобилей с реальными ссылками")
    print("=" * 70)
    
    try:
        update_real_car_photos()
        print("\n✅ Фотографии успешно обновлены!")
        print("🤖 Теперь запустите бота: python final_photos_bot.py")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()