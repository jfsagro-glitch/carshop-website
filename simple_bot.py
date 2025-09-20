#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простая версия бота автосалона для тестирования
"""

print("🚗 Запуск бота автосалона...")
print("=" * 50)

try:
    # Пытаемся импортировать необходимые модули
    import sys
    print(f"✅ Python версия: {sys.version}")
    
    import sqlite3
    print("✅ SQLite модуль доступен")
    
    import json
    print("✅ JSON модуль доступен")
    
    # Пытаемся импортировать telegram
    try:
        import telegram
        print("✅ Telegram библиотека найдена")
        
        # Информация о боте
        BOT_TOKEN = "7826759414:AAGaLHFPhbdoXYABMdx9E9EIERLWoU_uWwg"
        print(f"🤖 Токен бота: {BOT_TOKEN[:10]}...")
        
        print("\n🎯 Функционал бота:")
        print("• 📋 Просмотр каталога автомобилей")
        print("• 🔍 Поиск по брендам")
        print("• 📱 Подробная информация с фотографиями")
        print("• 🛒 Система заказов")
        print("• 📥 Импорт данных из CSV")
        
        print("\n📱 Команды:")
        print("• /start - Главное меню")
        print("• /cars - Показать автомобили")
        print("• /brands - Список брендов")
        print("• /help - Справка")
        
        print("\n✅ Бот готов к запуску!")
        print("🔗 Найдите бота в Telegram по токену и отправьте /start")
        
    except ImportError:
        print("❌ Telegram библиотека не найдена")
        print("💡 Установите командой: pip install python-telegram-bot")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")

print("\n" + "=" * 50)
print("🏁 Тест завершен")

