"""
Примеры использования API бота для разработчиков
"""

import requests
import json
from typing import Dict, List

class TelegramBotAPI:
    """Класс для работы с Telegram Bot API"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
    
    def send_message(self, chat_id: int, text: str, parse_mode: str = "Markdown") -> Dict:
        """Отправка сообщения"""
        url = f"{self.base_url}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        response = requests.post(url, json=data)
        return response.json()
    
    def send_photo(self, chat_id: int, photo: str, caption: str = "") -> Dict:
        """Отправка фотографии"""
        url = f"{self.base_url}/sendPhoto"
        data = {
            "chat_id": chat_id,
            "photo": photo,
            "caption": caption
        }
        response = requests.post(url, json=data)
        return response.json()
    
    def send_inline_keyboard(self, chat_id: int, text: str, keyboard: List[List[Dict]]) -> Dict:
        """Отправка сообщения с inline клавиатурой"""
        url = f"{self.base_url}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "reply_markup": {
                "inline_keyboard": keyboard
            }
        }
        response = requests.post(url, json=data)
        return response.json()
    
    def edit_message_text(self, chat_id: int, message_id: int, text: str, keyboard: List[List[Dict]] = None) -> Dict:
        """Редактирование сообщения"""
        url = f"{self.base_url}/editMessageText"
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text
        }
        if keyboard:
            data["reply_markup"] = {"inline_keyboard": keyboard}
        
        response = requests.post(url, json=data)
        return response.json()
    
    def answer_callback_query(self, callback_query_id: str, text: str = "") -> Dict:
        """Ответ на callback query"""
        url = f"{self.base_url}/answerCallbackQuery"
        data = {
            "callback_query_id": callback_query_id,
            "text": text
        }
        response = requests.post(url, json=data)
        return response.json()

def example_usage():
    """Пример использования API"""
    # Замените на ваш токен
    token = "7826759414:AAGaLHFPhbdoXYABMdx9E9EIERLWoU_uWwg"
    bot = TelegramBotAPI(token)
    
    # Пример отправки простого сообщения
    chat_id = 123456789  # Замените на реальный chat_id
    message = "🚗 Добро пожаловать в автосалон!"
    result = bot.send_message(chat_id, message)
    print("Результат отправки сообщения:", result)
    
    # Пример отправки сообщения с кнопками
    keyboard = [
        [{"text": "🚗 Посмотреть автомобили", "callback_data": "view_cars"}],
        [{"text": "🔍 Поиск по бренду", "callback_data": "search_brand"}]
    ]
    
    result = bot.send_inline_keyboard(chat_id, "Выберите действие:", keyboard)
    print("Результат отправки клавиатуры:", result)

def webhook_example():
    """Пример настройки webhook"""
    import flask
    from flask import request, jsonify
    
    app = flask.Flask(__name__)
    
    @app.route('/webhook', methods=['POST'])
    def webhook():
        """Обработка webhook от Telegram"""
        update = request.get_json()
        
        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            
            # Обработка команды /start
            if text == '/start':
                bot = TelegramBotAPI("7826759414:AAGaLHFPhbdoXYABMdx9E9EIERLWoU_uWwg")
                keyboard = [
                    [{"text": "🚗 Посмотреть автомобили", "callback_data": "view_cars"}],
                    [{"text": "🔍 Поиск по бренду", "callback_data": "search_brand"}]
                ]
                bot.send_inline_keyboard(chat_id, "Добро пожаловать в автосалон!", keyboard)
        
        return jsonify({'status': 'ok'})
    
    # Запуск Flask сервера
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    print("Примеры использования Telegram Bot API")
    print("=" * 50)
    
    # Раскомментируйте нужный пример
    # example_usage()
    # webhook_example()
    
    print("Для запуска примеров раскомментируйте нужную функцию")

