#!/usr/bin/env python3
"""
Скрипт для назначения администратора
"""

import sqlite3
import sys

def setup_admin(user_id: int):
    """Назначение пользователя администратором"""
    try:
        conn = sqlite3.connect("cars.db")
        cursor = conn.cursor()
        
        # Проверяем, существует ли пользователь
        cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        if not cursor.fetchone():
            print(f"❌ Пользователь с ID {user_id} не найден в базе данных")
            print("💡 Сначала запустите бота и отправьте команду /start")
            return False
        
        # Назначаем администратором
        cursor.execute('UPDATE users SET is_admin = 1 WHERE user_id = ?', (user_id,))
        
        if cursor.rowcount > 0:
            conn.commit()
            print(f"✅ Пользователь {user_id} назначен администратором")
            return True
        else:
            print(f"❌ Не удалось назначить администратора")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    finally:
        conn.close()

def main():
    """Основная функция"""
    print("👨‍💼 Назначение администратора CarSalesBot")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        try:
            user_id = int(sys.argv[1])
            setup_admin(user_id)
        except ValueError:
            print("❌ Неверный формат ID пользователя")
            print("💡 Использование: python setup_admin.py <USER_ID>")
    else:
        print("💡 Для назначения администратора:")
        print("1. Запустите бота и отправьте /start")
        print("2. Получите ваш Telegram ID")
        print("3. Выполните: python setup_admin.py <YOUR_TELEGRAM_ID>")
        print("\n🔍 Как получить ваш Telegram ID:")
        print("1. Найдите бота @userinfobot в Telegram")
        print("2. Отправьте ему /start")
        print("3. Скопируйте ваш ID")

if __name__ == "__main__":
    main()




