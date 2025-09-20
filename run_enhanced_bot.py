#!/usr/bin/env python3
"""
Запуск улучшенного Telegram-бота для продажи автомобилей
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Добавляем текущую директорию в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_bot import CarSalesBot

def main():
    """Основная функция запуска бота"""
    
    # Настройка логирования
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    # Получаем токен бота
    bot_token = os.getenv('BOT_TOKEN')
    
    if not bot_token:
        logger.error("BOT_TOKEN не найден в переменных окружения!")
        logger.error("Создайте файл .env и добавьте BOT_TOKEN=your_token_here")
        sys.exit(1)
    
    try:
        # Создаем и запускаем бота
        bot = CarSalesBot(bot_token)
        logger.info("Запуск CarSalesBot...")
        bot.run()
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()



