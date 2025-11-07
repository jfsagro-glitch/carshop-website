#!/usr/bin/env python3
"""
Исправленная версия бота с фотографиями
"""

import logging
import json
import os
import sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SimpleCarBot:
    def __init__(self, bot_token):
        """Инициализация бота"""
        self.bot_token = bot_token
        self.application = Application.builder().token(bot_token).build()
        self.db_path = "cars.db"
        self.init_database()
        self.setup_handlers()
    
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Создаем таблицы если их нет
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                is_admin BOOLEAN DEFAULT FALSE,
                is_seller BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                brand TEXT,
                model TEXT,
                year INTEGER,
                mileage INTEGER,
                price INTEGER,
                engine_type TEXT,
                transmission TEXT,
                color TEXT,
                description TEXT,
                photos TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                car_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (car_id) REFERENCES cars (id),
                UNIQUE(user_id, car_id)
            )
        ''')
        
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
    
    def add_user(self, user_id, username=None, first_name=None, last_name=None):
        """Добавление пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name))
            conn.commit()
        except Exception as e:
            print(f"Ошибка при добавлении пользователя: {e}")
        finally:
            conn.close()
    
    def get_cars(self, limit=10, offset=0):
        """Получение списка автомобилей"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM cars WHERE is_active = 1 
            ORDER BY created_at DESC LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        columns = [description[0] for description in cursor.description]
        cars = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return cars
    
    def get_car_by_id(self, car_id):
        """Получение автомобиля по ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM cars WHERE id = ?', (car_id,))
        columns = [description[0] for description in cursor.description]
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return dict(zip(columns, row))
        return None
    
    def get_favorites(self, user_id):
        """Получение избранных автомобилей"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.* FROM cars c
            JOIN favorites f ON c.id = f.car_id
            WHERE f.user_id = ? AND c.is_active = 1
            ORDER BY f.created_at DESC
        ''', (user_id,))
        
        columns = [description[0] for description in cursor.description]
        cars = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return cars
    
    def add_to_favorites(self, user_id, car_id):
        """Добавление в избранное"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO favorites (user_id, car_id)
                VALUES (?, ?)
            ''', (user_id, car_id))
            conn.commit()
        except Exception as e:
            print(f"Ошибка при добавлении в избранное: {e}")
        finally:
            conn.close()
    
    def remove_from_favorites(self, user_id, car_id):
        """Удаление из избранного"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                DELETE FROM favorites WHERE user_id = ? AND car_id = ?
            ''', (user_id, car_id))
            conn.commit()
        except Exception as e:
            print(f"Ошибка при удалении из избранного: {e}")
        finally:
            conn.close()
    
    def is_favorite(self, user_id, car_id):
        """Проверка, есть ли в избранном"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM favorites WHERE user_id = ? AND car_id = ?
        ''', (user_id, car_id))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def is_admin(self, user_id):
        """Проверка прав администратора"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT is_admin FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        return result and result[0]
    
    def get_statistics(self):
        """Получение статистики"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Общее количество пользователей
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        # Общее количество автомобилей
        cursor.execute('SELECT COUNT(*) FROM cars WHERE is_active = 1')
        total_cars = cursor.fetchone()[0]
        
        # Количество избранных
        cursor.execute('SELECT COUNT(*) FROM favorites')
        total_favorites = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_users': total_users,
            'total_cars': total_cars,
            'total_favorites': total_favorites
        }
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        self.add_user(user.id, user.username, user.first_name, user.last_name)
        
        text = f"""
🚗 *Добро пожаловать в AutoSaleGE!*

Привет, {user.first_name}! 👋

Я помогу вам найти идеальный автомобиль или продать свой.

*Доступные команды:*
🚗 /catalog - Каталог автомобилей
💝 /favorites - Избранные автомобили
❓ /help - Помощь
👨‍💼 /admin - Панель администратора

*Нажмите на кнопки ниже для быстрого доступа:*
        """
        
        keyboard = [
            [InlineKeyboardButton("🚗 Каталог авто", callback_data="catalog")],
            [InlineKeyboardButton("💝 Избранное", callback_data="favorites")],
            [InlineKeyboardButton("❓ Помощь", callback_data="help")],
            [InlineKeyboardButton("👨‍💼 Админ", callback_data="admin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
🤖 *AutoSaleGE - Помощь*

*Основные команды:*
🚗 `/catalog` - Просмотр каталога автомобилей
💝 `/favorites` - Ваши избранные автомобили
❓ `/help` - Показать эту справку
👨‍💼 `/admin` - Панель администратора

*Как пользоваться:*
1. Выберите "🚗 Каталог авто" для просмотра автомобилей
2. Нажмите на автомобиль для просмотра деталей
3. Добавляйте понравившиеся авто в избранное
4. Связывайтесь с продавцами через кнопки

*Поддержка:*
Если у вас есть вопросы, обратитесь к администратору.
        """
        
        keyboard = [[InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                help_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                help_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )
    
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
            keyboard.append([InlineKeyboardButton(
                f"🚗 {car['brand']} {car['model']} - {car['price']:,} ₽",
                callback_data=f"car_{car['id']}"
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

*Доступные действия:*
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
            text = "🚗 *Каталог автомобилей*\n\nК сожалению, в данный момент нет доступных автомобилей."
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
        
        text = f"🚗 *Каталог автомобилей* (стр. {page + 1})\n\n"
        
        keyboard = []
        for car in cars:
            keyboard.append([InlineKeyboardButton(
                f"🚗 {car['brand']} {car['model']} ({car['year']}) - {car['price']:,} ₽",
                callback_data=f"car_{car['id']}"
            )])
        
        # Навигация
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"page_{page-1}"))
        if len(cars) == 5:  # Если показали 5, возможно есть еще
            nav_buttons.append(InlineKeyboardButton("➡️ Вперед", callback_data=f"page_{page+1}"))
        
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
                text, reply_markup=reply_markup
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
            text, reply_markup=reply_markup
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "main_menu":
            await self.start_command(update, context)
        elif data == "catalog":
            await self.show_cars(update, context, page=0)
        elif data == "favorites":
            await self.favorites_command(update, context)
        elif data == "help":
            await self.help_command(update, context)
        elif data == "admin":
            await self.admin_command(update, context)
        elif data.startswith("page_"):
            page = int(data.replace("page_", ""))
            await self.show_cars(update, context, page=page)
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
        
        if self.is_favorite(user_id, car_id):
            # Удаляем из избранного
            self.remove_from_favorites(user_id, car_id)
            await update.callback_query.answer("💔 Удалено из избранного")
        else:
            # Добавляем в избранное
            self.add_to_favorites(user_id, car_id)
            await update.callback_query.answer("❤️ Добавлено в избранное")
    
    async def show_contact_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE, car_id: int):
        """Показ контактной информации"""
        car = self.get_car_by_id(car_id)
        
        if not car:
            await update.callback_query.answer("❌ Автомобиль не найден")
            return
        
        text = f"""
📞 *Связь с продавцом*

🚗 *{car['brand']} {car['model']} ({car['year']})*
💰 *Цена:* {car['price']:,} ₽

*Для связи с продавцом:*
📱 Telegram: @autosalege_support
📧 Email: support@autosalege.com
☎️ Телефон: +7 (XXX) XXX-XX-XX

*Или напишите администратору:*
👨‍💼 @autosalege_admin
        """
        
        keyboard = [
            [InlineKeyboardButton("📱 Написать в Telegram", url="https://t.me/autosalege_support")],
            [InlineKeyboardButton("📧 Отправить email", url="mailto:support@autosalege.com")],
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

*Последние обновления:*
🕐 {datetime.now().strftime('%d.%m.%Y %H:%M')}
        """
        
        keyboard = [
            [InlineKeyboardButton("👥 Пользователи", callback_data="admin_users")],
            [InlineKeyboardButton("🔙 Админ панель", callback_data="admin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
        )
    
    async def show_admin_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ списка пользователей"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, username, first_name, last_name, is_admin, created_at
            FROM users ORDER BY created_at DESC LIMIT 10
        ''')
        
        users = cursor.fetchall()
        conn.close()
        
        text = "👥 *Последние пользователи*\n\n"
        
        for user in users:
            user_id, username, first_name, last_name, is_admin, created_at = user
            admin_text = "👑" if is_admin else "👤"
            name = f"{first_name} {last_name}" if first_name and last_name else (username or f"ID: {user_id}")
            text += f"{admin_text} {name}\n"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Админ панель", callback_data="admin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
        )
    
    def run(self):
        """Запуск бота"""
        logger.info("Запуск SimpleCarBot...")
        self.application.run_polling()

def main():
    """Основная функция"""
    try:
        from config import BOT_TOKEN
    except ImportError:
        BOT_TOKEN = "8431697857:AAFBcnKw3BCX_jL5QwfUN7aCj71nNiSRBh4"
        print("⚠️ Файл config.py не найден, используется токен по умолчанию")
    
    bot = SimpleCarBot(BOT_TOKEN)
    bot.run()

if __name__ == "__main__":
    main()





