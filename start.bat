@echo off
echo ========================================
echo    Запуск Telegram бота автосалона
echo ========================================
echo.

echo Установка зависимостей...
pip install -r requirements.txt

echo.
echo Запуск бота...
python run_bot.py

pause

