#!/usr/bin/env python3
"""
Упрощенная рабочая версия CarSalesBot
"""

import logging
import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = "8431697857:AAFBcnKw3BCX_jL5QwfUN7aCj71nNiSRBh4"

class SimpleCarBot:
    """Упрощенная версия бота для продажи автомобилей"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.application = Application.builder().token(bot_token).build()
        self.setup_handlers()
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect("cars.db")
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                is_admin BOOLEAN DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица автомобилей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cars (
                car_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                brand TEXT NOT NULL,
                model TEXT NOT NULL,
                year INTEGER NOT NULL,
                mileage INTEGER NOT NULL,
                price INTEGER NOT NULL,
                engine_type TEXT,
                transmission TEXT,
                color TEXT,
                description TEXT,
                photos TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица избранного
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                car_id INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (car_id) REFERENCES cars (car_id),
                UNIQUE(user_id, car_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Добавляем тестовые данные
        self.add_sample_data()
    
    def add_sample_data(self):
        """Добавление тестовых данных"""
        conn = sqlite3.connect("cars.db")
        cursor = conn.cursor()
        
        # Проверяем, есть ли уже данные
        cursor.execute("SELECT COUNT(*) FROM cars")
        if cursor.fetchone()[0] == 0:
            sample_cars = [
                {
                    'brand': 'Toyota',
                    'model': 'Camry',
                    'year': 2020,
                    'price': 2500000,
                    'mileage': 45000,
                    'engine_type': 'Бензин',
                    'transmission': 'Автомат',
                    'color': 'Белый',
                    'description': 'Отличное состояние, один владелец, полная комплектация',
                    'photos': '["https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?w=800"]'
                },
                {
                    'brand': 'BMW',
                    'model': 'X5',
                    'year': 2019,
                    'price': 4200000,
                    'mileage': 62000,
                    'engine_type': 'Бензин',
                    'transmission': 'Автомат',
                    'color': 'Черный',
                    'description': 'Премиум комплектация, кожаный салон, навигация',
                    'photos': '["https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800"]'
                },
                {
                    'brand': 'Audi',
                    'model': 'A4',
                    'year': 2021,
                    'price': 3200000,
                    'mileage': 28000,
                    'engine_type': 'Бензин',
                    'transmission': 'Автомат',
                    'color': 'Серый',
                    'description': 'Новый автомобиль, гарантия, полный пакет опций',
                    'photos': '["https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=800"]'
                }
            ]
            
            for car in sample_cars:
                cursor.execute('''
                    INSERT INTO cars (user_id, brand, model, year, price, mileage, 
                                   engine_type, transmission, color, description, photos)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (1, car['brand'], car['model'], car['year'], car['price'], 
                     car['mileage'], car['engine_type'], car['transmission'], 
                     car['color'], car['description'], car['photos']))
        
        conn.commit()
        conn.close()
    
    def setup_handlers(self):
        """Настройка обработчиков"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("catalog", self.catalog_command))
        self.application.add_handler(CommandHandler("favorites", self.favorites_command))
        self.application.add_handler(CommandHandler("admin", self.admin_command))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        user_id = user.id
        
        # Регистрируем пользователя
        self.add_user(user_id, user.username, user.first_name, user.last_name)
        
        keyboard = [
            [InlineKeyboardButton("🚗 Каталог авто", callback_data="catalog")],
            [InlineKeyboardButton("💝 Избранное", callback_data="favorites")],
            [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")],
            [InlineKeyboardButton("👨‍💼 Админ", callback_data="admin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = """
🚗 *Добро пожаловать в CarSalesBot!*

Здесь вы можете:
• 🚗 Просматривать каталог автомобилей
• 💝 Сохранять понравившиеся авто в избранное
• 📞 Связываться с продавцами

Выберите действие:
        """
        
        await update.message.reply_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
*📋 Доступные команды:*

/start - Главное меню
/catalog - Просмотр каталога автомобилей
/favorites - Ваши избранные автомобили
/admin - Панель администратора
/help - Эта справка

*🔍 Как пользоваться:*
1. Используйте "Каталог авто" для просмотра всех автомобилей
2. Добавляйте понравившиеся авто в избранное
3. Используйте "Админ" для управления (только для администраторов)
        """
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def catalog_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /catalog"""
        await self.show_cars(update, context, page=0)
    
    async def favorites_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /favorites"""
        user_id = update.effective_user.id
        favorites = self.get_favorites(user_id)
        
        if not favorites:
            text = "💝 У вас пока нет избранных автомобилей.\n\nДобавляйте понравившиеся авто в избранное, нажимая ❤️ в каталоге."
            keyboard = [[InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(
                    text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
                )
            return
        
        text = f"💝 *Ваши избранные автомобили* ({len(favorites)} шт.)\n\n"
        
        keyboard = []
        for car in favorites[:10]:
            text += f"🚗 *{car['brand']} {car['model']} ({car['year']})*\n"
            text += f"💰 {car['price']:,} ₽ | 🛣️ {car['mileage']:,} км\n\n"
            
            keyboard.append([InlineKeyboardButton(
                f"🚗 {car['brand']} {car['model']} - {car['price']:,} ₽",
                callback_data=f"car_{car['car_id']}"
            )])
        
        keyboard.append([InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /admin"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            text = "❌ У вас нет прав администратора"
            keyboard = [[InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(
                    text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
                )
            return
        
        stats = self.get_statistics()
        
        text = f"""
👨‍💼 *Панель администратора*

📊 *Статистика:*
👥 Пользователей: {stats['total_users']}
🚗 Автомобилей: {stats['total_cars']}
💝 В избранном: {stats['total_favorites']}
        """
        
        keyboard = [
            [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton("👥 Пользователи", callback_data="admin_users")],
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )
    
    async def show_cars(self, update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0):
        """Показ списка автомобилей"""
        cars = self.get_cars(limit=5, offset=page*5)
        
        if not cars:
            text = "❌ Автомобили не найдены"
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]]
        else:
            text = f"🚗 *Каталог автомобилей* (страница {page + 1})\n\n"
            
            keyboard = []
            for car in cars:
                text += f"🚗 *{car['brand']} {car['model']} ({car['year']})*\n"
                text += f"💰 {car['price']:,} ₽ | 🛣️ {car['mileage']:,} км\n\n"
                
                keyboard.append([InlineKeyboardButton(
                    f"🚗 {car['brand']} {car['model']} - {car['price']:,} ₽",
                    callback_data=f"car_{car['car_id']}"
                )])
            
            # Кнопки навигации
            nav_buttons = []
            if page > 0:
                nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"page_{page-1}"))
            
            if len(cars) == 5:
                nav_buttons.append(InlineKeyboardButton("➡️ Далее", callback_data=f"page_{page+1}"))
            
            if nav_buttons:
                keyboard.append(nav_buttons)
            
            keyboard.append([InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )
    
    async def show_car_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE, car_id: int):
        """Показ подробной информации об автомобиле"""
        car = self.get_car_by_id(car_id)
        
        if not car:
            await update.callback_query.answer("❌ Автомобиль не найден")
            return
        
        user_id = update.effective_user.id
        
        text = f"""
🚗 *{car['brand']} {car['model']} ({car['year']})*

💰 *Цена:* {car['price']:,} ₽
🛣️ *Пробег:* {car['mileage']:,} км
⛽ *Двигатель:* {car.get('engine_type', 'Не указан')}
🔧 *КПП:* {car.get('transmission', 'Не указана')}
🎨 *Цвет:* {car.get('color', 'Не указан')}

📝 *Описание:*
{car.get('description', 'Описание отсутствует')}
        """
        
        keyboard = [
            [InlineKeyboardButton("❤️ В избранное", callback_data=f"favorite_{car_id}")],
            [InlineKeyboardButton("📞 Связаться с продавцом", callback_data=f"contact_{car_id}")],
            [InlineKeyboardButton("🔙 К каталогу", callback_data="catalog")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Проверяем наличие фотографий
        photos = []
        if car.get('photos'):
            try:
                photos = json.loads(car['photos']) if isinstance(car['photos'], str) else car['photos']
            except:
                photos = []
        
        if photos and photos[0]:
            # Добавляем кнопку для просмотра фотографий
            keyboard.insert(0, [InlineKeyboardButton("📸 Посмотреть фотографии", callback_data=f"photos_{car_id}")])
            reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "main_menu":
            await self.start_command(update, context)
        elif data == "catalog":
            await self.show_cars(update, context)
        elif data == "favorites":
            await self.favorites_command(update, context)
        elif data == "help":
            await self.help_command(update, context)
        elif data == "admin":
            await self.admin_command(update, context)
        elif data.startswith("page_"):
            page = int(data.split("_")[1])
            await self.show_cars(update, context, page)
        elif data.startswith("car_"):
            car_id = int(data.replace("car_", ""))
            await self.show_car_details(update, context, car_id)
        elif data.startswith("favorite_"):
            car_id = int(data.replace("favorite_", ""))
            await self.toggle_favorite(update, context, car_id)
        elif data.startswith("contact_"):
            car_id = int(data.replace("contact_", ""))
            await self.show_contact_info(update, context, car_id)
        elif data.startswith("photos_"):
            car_id = int(data.replace("photos_", ""))
            await self.show_car_photos(update, context, car_id)
        elif data == "admin_stats":
            await self.show_admin_stats(update, context)
        elif data == "admin_users":
            await self.show_admin_users(update, context)
    
    async def toggle_favorite(self, update: Update, context: ContextTypes.DEFAULT_TYPE, car_id: int):
        """Добавление/удаление из избранного"""
        user_id = update.effective_user.id
        
        # Проверяем, есть ли уже в избранном
        favorites = self.get_favorites(user_id)
        car_ids = [fav['car_id'] for fav in favorites]
        
        if car_id in car_ids:
            # Удаляем из избранного
            self.remove_from_favorites(user_id, car_id)
            await update.callback_query.answer("💔 Удалено из избранного")
        else:
            # Добавляем в избранное
            self.add_to_favorites(user_id, car_id)
            await update.callback_query.answer("❤️ Добавлено в избранное")
    
    async def show_car_photos(self, update: Update, context: ContextTypes.DEFAULT_TYPE, car_id: int):
        """Показ фотографий автомобиля"""
        car = self.get_car_by_id(car_id)
        
        if not car:
            await update.callback_query.answer("❌ Автомобиль не найден")
            return
        
        # Получаем фотографии
        photos = []
        if car.get('photos'):
            try:
                photos = json.loads(car['photos']) if isinstance(car['photos'], str) else car['photos']
            except:
                photos = []
        
        if not photos or not photos[0]:
            text = "📸 Фотографии для этого автомобиля не найдены"
            keyboard = [[InlineKeyboardButton("🔙 К автомобилю", callback_data=f"car_{car_id}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.edit_message_text(
                text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )
            return
        
        # Показываем ссылку на фотографии
        text = f"""📸 Фотографии {car['brand']} {car['model']} ({car['year']})

🔗 Ссылка на альбом:
{photos[0]}

Нажмите на ссылку выше, чтобы посмотреть фотографии автомобиля."""
        
        keyboard = [
            [InlineKeyboardButton("🔗 Открыть фотографии", url=photos[0])],
            [InlineKeyboardButton("🔙 К автомобилю", callback_data=f"car_{car_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
        )
    
    async def show_contact_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE, car_id: int):
        """Показ контактной информации"""
        car = self.get_car_by_id(car_id)
        
        if not car:
            await update.callback_query.answer("❌ Автомобиль не найден")
            return
        
        text = f"""
📞 *Контактная информация*

🚗 *Автомобиль:* {car['brand']} {car['model']} ({car['year']})
💰 *Цена:* {car['price']:,} ₽

*Для связи с продавцом используйте кнопку "Связаться" ниже.*
        """
        
        keyboard = [
            [InlineKeyboardButton("📞 Связаться", url="https://t.me/autosalege_bot")],
            [InlineKeyboardButton("🔙 К автомобилю", callback_data=f"car_{car_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
        )
    
    async def show_admin_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ статистики администратора"""
        stats = self.get_statistics()
        
        text = f"""
📊 *Статистика системы*

👥 *Пользователи:* {stats['total_users']}
🚗 *Автомобили:* {stats['total_cars']}
💝 *В избранном:* {stats['total_favorites']}
📅 *Последнее обновление:* {datetime.now().strftime('%d.%m.%Y %H:%M')}
        """
        
        keyboard = [[InlineKeyboardButton("🔙 Админ-панель", callback_data="admin")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
        )
    
    async def show_admin_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ пользователей"""
        users = self.get_users()
        
        text = f"👥 *Пользователи системы* ({len(users)} чел.)\n\n"
        
        for user in users[:10]:  # Показываем первых 10
            text += f"👤 {user.get('first_name', 'Не указано')} (@{user.get('username', 'нет username')})\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Админ-панель", callback_data="admin")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        text = update.message.text.lower()
        
        if any(word in text for word in ['привет', 'hello', 'hi', 'здравствуй']):
            await update.message.reply_text("👋 Привет! Используйте /start для начала работы с ботом.")
        elif any(word in text for word in ['помощь', 'help', 'справка']):
            await self.help_command(update, context)
        else:
            await update.message.reply_text(
                "Не понимаю ваше сообщение. Используйте /start для начала работы."
            )
    
    # Методы работы с базой данных
    def add_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        """Добавление пользователя"""
        conn = sqlite3.connect("cars.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name))
        
        conn.commit()
        conn.close()
    
    def is_admin(self, user_id: int) -> bool:
        """Проверка прав администратора"""
        conn = sqlite3.connect("cars.db")
        cursor = conn.cursor()
        
        cursor.execute('SELECT is_admin FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result and result[0] == 1
    
    def get_cars(self, limit: int = 10, offset: int = 0) -> List[Dict]:
        """Получение списка автомобилей"""
        conn = sqlite3.connect("cars.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM cars WHERE is_active = 1 
            ORDER BY created_at DESC LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        columns = [description[0] for description in cursor.description]
        cars = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return cars
    
    def get_car_by_id(self, car_id: int) -> Optional[Dict]:
        """Получение автомобиля по ID"""
        conn = sqlite3.connect("cars.db")
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM cars WHERE car_id = ?', (car_id,))
        row = cursor.fetchone()
        
        if row:
            columns = [description[0] for description in cursor.description]
            car = dict(zip(columns, row))
            conn.close()
            return car
        
        conn.close()
        return None
    
    def add_to_favorites(self, user_id: int, car_id: int) -> bool:
        """Добавление в избранное"""
        try:
            conn = sqlite3.connect("cars.db")
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO favorites (user_id, car_id)
                VALUES (?, ?)
            ''', (user_id, car_id))
            
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def remove_from_favorites(self, user_id: int, car_id: int) -> bool:
        """Удаление из избранного"""
        try:
            conn = sqlite3.connect("cars.db")
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM favorites WHERE user_id = ? AND car_id = ?
            ''', (user_id, car_id))
            
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def get_favorites(self, user_id: int) -> List[Dict]:
        """Получение избранных автомобилей"""
        conn = sqlite3.connect("cars.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.* FROM cars c 
            JOIN favorites f ON c.car_id = f.car_id
            WHERE f.user_id = ? AND c.is_active = 1
            ORDER BY f.created_at DESC
        ''', (user_id,))
        
        columns = [description[0] for description in cursor.description]
        cars = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return cars
    
    def get_statistics(self) -> Dict:
        """Получение статистики"""
        conn = sqlite3.connect("cars.db")
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM cars WHERE is_active = 1')
        total_cars = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM favorites')
        total_favorites = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_users': total_users,
            'total_cars': total_cars,
            'total_favorites': total_favorites
        }
    
    def get_users(self) -> List[Dict]:
        """Получение списка пользователей"""
        conn = sqlite3.connect("cars.db")
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
        columns = [description[0] for description in cursor.description]
        users = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return users
    
    def run(self):
        """Запуск бота"""
        logger.info("Запуск SimpleCarBot...")
        self.application.run_polling()

def main():
    """Основная функция"""
    bot = SimpleCarBot(BOT_TOKEN)
    bot.run()

if __name__ == "__main__":
    main()
