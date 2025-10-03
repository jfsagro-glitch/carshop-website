#!/usr/bin/env python3
"""
Тест подключения к Telegram API
"""

import asyncio
from telegram import Bot
from config import BOT_TOKEN

async def test_connection():
    """Тест подключения к Telegram API"""
    try:
        bot = Bot(token=BOT_TOKEN)
        
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        
        print("✅ Подключение к Telegram API успешно!")
        print(f"🤖 Имя бота: {bot_info.first_name}")
        print(f"🆔 Username: @{bot_info.username}")
        print(f"🆔 ID бота: {bot_info.id}")
        print(f"🔗 Ссылка на бота: https://t.me/{bot_info.username}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения к Telegram API: {e}")
        return False

def main():
    """Основная функция"""
    print("🔍 Тестирование подключения к Telegram API...")
    print("=" * 50)
    
    # Запускаем асинхронный тест
    result = asyncio.run(test_connection())
    
    if result:
        print("\n🎉 Бот готов к работе!")
        print("📱 Найдите бота в Telegram и отправьте /start")
    else:
        print("\n❌ Проблема с подключением к Telegram API")
        print("🔧 Проверьте токен бота в config.py")

if __name__ == "__main__":
    main()




