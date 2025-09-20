#!/usr/bin/env python3
"""
Скрипт для запуска Telegram бота автосалона
"""

import sys
import logging
import traceback
from bot import CarShopBot

def setup_logging():
    """Настройка логирования"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Главная функция запуска бота"""
    try:
        print("🚗 Запуск бота автосалона...")
        print("=" * 50)
        
        # Настройка логирования
        setup_logging()
        logger = logging.getLogger(__name__)
        
        # Проверяем наличие CSV файла и импортируем данные
        if os.path.exists("cars_data.csv"):
            print("📥 Обнаружен CSV файл с данными об автомобилях")
            print("🔄 Импорт данных...")
            
            try:
                from csv_importer import CarsCSVImporter
                importer = CarsCSVImporter()
                success = importer.import_to_database(clear_existing=True)
                
                if success:
                    print("✅ Данные успешно импортированы")
                else:
                    print("⚠️ Ошибка при импорте данных, продолжаем с существующими данными")
            except Exception as e:
                print(f"⚠️ Ошибка импорта: {e}, продолжаем с существующими данными")
        else:
            print("ℹ️ CSV файл не найден, используются тестовые данные")
        
        # Создание и запуск бота
        bot = CarShopBot()
        logger.info("Бот успешно инициализирован")
        
        print("✅ Бот запущен и готов к работе!")
        print("📱 Найдите бота в Telegram и отправьте /start")
        print("🛑 Для остановки нажмите Ctrl+C")
        print("=" * 50)
        
        # Запуск бота
        bot.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал остановки...")
        print("👋 Бот остановлен")
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        print("📋 Детали ошибки:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
