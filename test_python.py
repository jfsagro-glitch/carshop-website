#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("🐍 Python работает корректно!")
print("🚗 Тестируем бота...")

try:
    import sqlite3
    print("✅ SQLite модуль найден")
except ImportError:
    print("❌ SQLite модуль не найден")

try:
    import telegram
    print("✅ Telegram модуль найден")
except ImportError:
    print("❌ Telegram модуль не найден")
    print("💡 Установите: pip install python-telegram-bot")

print("🎯 Тест завершен")

