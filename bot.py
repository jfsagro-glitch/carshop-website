import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from csv_importer import CarsCSVImporter

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = "7826759414:AAGaLHFPhbdoXYABMdx9E9EIERLWoU_uWwg"

@dataclass
class Car:
    id: int
    brand: str
    model: str
    year: int
    price: int
    mileage: int
    fuel_type: str
    transmission: str
    color: str
    description: str
    photos: List[str]
    is_available: bool = True

class CarDatabase:
    def __init__(self, db_path: str = "cars.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT NOT NULL,
                model TEXT NOT NULL,
                year INTEGER NOT NULL,
                price INTEGER NOT NULL,
                mileage INTEGER NOT NULL,
                fuel_type TEXT NOT NULL,
                transmission TEXT NOT NULL,
                color TEXT NOT NULL,
                description TEXT,
                photos TEXT,
                is_available BOOLEAN DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                car_id INTEGER NOT NULL,
                order_date TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (car_id) REFERENCES cars (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Добавляем тестовые данные если база пустая
        self.add_sample_cars()
    
    def add_sample_cars(self):
        """Добавление тестовых автомобилей"""
        sample_cars = [
            {
                'brand': 'Toyota',
                'model': 'Camry',
                'year': 2020,
                'price': 2500000,
                'mileage': 45000,
                'fuel_type': 'Бензин',
                'transmission': 'Автомат',
                'color': 'Белый',
                'description': 'Отличное состояние, один владелец, полная комплектация',
                'photos': '["https://example.com/camry1.jpg", "https://example.com/camry2.jpg"]'
            },
            {
                'brand': 'BMW',
                'model': 'X5',
                'year': 2019,
                'price': 4200000,
                'mileage': 62000,
                'fuel_type': 'Бензин',
                'transmission': 'Автомат',
                'color': 'Черный',
                'description': 'Премиум комплектация, кожаный салон, навигация',
                'photos': '["https://example.com/x5_1.jpg", "https://example.com/x5_2.jpg"]'
            },
            {
                'brand': 'Audi',
                'model': 'A4',
                'year': 2021,
                'price': 3200000,
                'mileage': 28000,
                'fuel_type': 'Бензин',
                'transmission': 'Автомат',
                'color': 'Серый',
                'description': 'Новый автомобиль, гарантия, полный пакет опций',
                'photos': '["https://example.com/a4_1.jpg", "https://example.com/a4_2.jpg"]'
            }
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Проверяем, есть ли уже данные
        cursor.execute("SELECT COUNT(*) FROM cars")
        if cursor.fetchone()[0] == 0:
            for car in sample_cars:
                cursor.execute('''
                    INSERT INTO cars (brand, model, year, price, mileage, fuel_type, 
                                   transmission, color, description, photos)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (car['brand'], car['model'], car['year'], car['price'], 
                     car['mileage'], car['fuel_type'], car['transmission'], 
                     car['color'], car['description'], car['photos']))
        
        conn.commit()
        conn.close()
    
    def get_cars(self, limit: int = 10, offset: int = 0, brand: str = None) -> List[Dict]:
        """Получение списка автомобилей"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if brand:
            cursor.execute('''
                SELECT * FROM cars WHERE brand = ? AND is_available = 1 
                ORDER BY id DESC LIMIT ? OFFSET ?
            ''', (brand, limit, offset))
        else:
            cursor.execute('''
                SELECT * FROM cars WHERE is_available = 1 
                ORDER BY id DESC LIMIT ? OFFSET ?
            ''', (limit, offset))
        
        columns = [description[0] for description in cursor.description]
        cars = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return cars
    
    def get_car_by_id(self, car_id: int) -> Optional[Dict]:
        """Получение автомобиля по ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM cars WHERE id = ?', (car_id,))
        row = cursor.fetchone()
        
        if row:
            columns = [description[0] for description in cursor.description]
            car = dict(zip(columns, row))
            conn.close()
            return car
        
        conn.close()
        return None
    
    def get_brands(self) -> List[str]:
        """Получение списка брендов"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT brand FROM cars WHERE is_available = 1 ORDER BY brand')
        brands = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return brands
    
    def create_order(self, user_id: int, car_id: int) -> bool:
        """Создание заказа"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO orders (user_id, car_id, order_date)
                VALUES (?, ?, ?)
            ''', (user_id, car_id, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Ошибка создания заказа: {e}")
            conn.close()
            return False
    
    def import_from_csv(self, csv_file: str = "cars_data.csv", clear_existing: bool = False) -> bool:
        """Импорт данных из CSV файла"""
        try:
            importer = CarsCSVImporter(csv_file, self.db_path)
            return importer.import_to_database(clear_existing)
        except Exception as e:
            logger.error(f"Ошибка импорта из CSV: {e}")
            return False

# Инициализация базы данных
db = CarDatabase()

class CarShopBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("cars", self.cars_command))
        self.application.add_handler(CommandHandler("brands", self.brands_command))
        self.application.add_handler(CommandHandler("import", self.import_command))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        keyboard = [
            [InlineKeyboardButton("🚗 Посмотреть автомобили", callback_data="view_cars")],
            [InlineKeyboardButton("🔍 Поиск по бренду", callback_data="search_brand")],
            [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = """
🚗 *Добро пожаловать в автосалон!*

Здесь вы можете:
• Просматривать доступные автомобили
• Искать по брендам
• Получать подробную информацию
• Оформлять заказы

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
/cars - Показать все автомобили
/brands - Список брендов
/help - Эта справка

*🔍 Как пользоваться:*
1. Нажмите "Посмотреть автомобили" для просмотра каталога
2. Используйте кнопки навигации для перехода между страницами
3. Нажмите на автомобиль для подробной информации
4. Используйте "Поиск по бренду" для фильтрации

*📞 Контакты:*
Телефон: +7 (XXX) XXX-XX-XX
Email: info@autoshop.ru
        """
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def cars_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /cars"""
        await self.show_cars(update, context, page=0)
    
    async def brands_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /brands"""
        brands = db.get_brands()
        
        if not brands:
            await update.message.reply_text("❌ Автомобили не найдены")
            return
        
        keyboard = []
        for brand in brands:
            keyboard.append([InlineKeyboardButton(f"🚗 {brand}", callback_data=f"brand_{brand}")])
        
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="main_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        brands_text = "*🏭 Доступные бренды:*\n\n"
        for brand in brands:
            brands_text += f"• {brand}\n"
        
        await update.message.reply_text(
            brands_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def import_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /import для импорта данных из CSV"""
        # Проверяем, что команда выполняется администратором
        user_id = update.effective_user.id
        
        # Простая проверка на администратора (можно расширить)
        admin_ids = [123456789]  # Замените на реальные ID администраторов
        
        if user_id not in admin_ids:
            await update.message.reply_text("❌ У вас нет прав для выполнения этой команды")
            return
        
        await update.message.reply_text("📥 Начинаю импорт данных из CSV файла...")
        
        try:
            success = db.import_from_csv("cars_data.csv", clear_existing=True)
            
            if success:
                cars_count = len(db.get_cars())
                await update.message.reply_text(
                    f"✅ Импорт завершен успешно!\n"
                    f"📊 Загружено автомобилей: {cars_count}\n"
                    f"📁 Файл: cars_data.csv"
                )
            else:
                await update.message.reply_text("❌ Ошибка при импорте данных из CSV файла")
                
        except Exception as e:
            logger.error(f"Ошибка импорта: {e}")
            await update.message.reply_text(f"❌ Ошибка импорта: {str(e)}")
    
    async def show_cars(self, update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0, brand: str = None):
        """Показать список автомобилей"""
        cars = db.get_cars(limit=5, offset=page*5, brand=brand)
        
        if not cars:
            text = "❌ Автомобили не найдены"
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]]
        else:
            text = f"🚗 *Автомобили* (страница {page + 1})\n\n"
            
            keyboard = []
            for car in cars:
                text += f"*{car['brand']} {car['model']} ({car['year']})*\n"
                text += f"💰 Цена: {car['price']:,} ₽\n"
                text += f"🛣️ Пробег: {car['mileage']:,} км\n"
                text += f"⛽ Топливо: {car['fuel_type']}\n"
                text += f"🎨 Цвет: {car['color']}\n\n"
                
                keyboard.append([InlineKeyboardButton(
                    f"🚗 {car['brand']} {car['model']} - {car['price']:,} ₽",
                    callback_data=f"car_{car['id']}"
                )])
            
            # Кнопки навигации
            nav_buttons = []
            if page > 0:
                nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"page_{page-1}_{brand or ''}"))
            
            if len(cars) == 5:  # Если показали 5 машин, возможно есть еще
                nav_buttons.append(InlineKeyboardButton("➡️ Далее", callback_data=f"page_{page+1}_{brand or ''}"))
            
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
        """Показать подробную информацию об автомобиле"""
        car = db.get_car_by_id(car_id)
        
        if not car:
            await update.callback_query.answer("❌ Автомобиль не найден")
            return
        
        text = f"""
🚗 *{car['brand']} {car['model']} ({car['year']})*

💰 *Цена:* {car['price']:,} ₽
🛣️ *Пробег:* {car['mileage']:,} км
⛽ *Топливо:* {car['fuel_type']}
🔧 *КПП:* {car['transmission']}
🎨 *Цвет:* {car['color']}

📝 *Описание:*
{car['description']}

✅ *В наличии*
        """
        
        keyboard = [
            [InlineKeyboardButton("🛒 Заказать", callback_data=f"order_{car_id}")],
            [InlineKeyboardButton("🔙 К списку", callback_data="view_cars")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Проверяем наличие фотографий
        photos = []
        if car.get('photos'):
            try:
                photos = json.loads(car['photos']) if isinstance(car['photos'], str) else car['photos']
            except:
                photos = []
        
        if photos:
            # Отправляем фотографии с подписью
            try:
                media = []
                for i, photo_url in enumerate(photos[:5]):  # Максимум 5 фотографий
                    if i == 0:
                        media.append(InputMediaPhoto(media=photo_url, caption=text, parse_mode=ParseMode.MARKDOWN))
                    else:
                        media.append(InputMediaPhoto(media=photo_url))
                
                await update.callback_query.delete_message()
                await context.bot.send_media_group(
                    chat_id=update.effective_chat.id,
                    media=media
                )
                
                # Отправляем кнопки отдельным сообщением
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Выберите действие:",
                    reply_markup=reply_markup
                )
                return
                
            except Exception as e:
                logger.error(f"Ошибка отправки фотографий: {e}")
                # Если не удалось отправить фотографии, отправляем обычное сообщение
        
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
        elif data == "view_cars":
            await self.show_cars(update, context)
        elif data == "search_brand":
            await self.brands_command(update, context)
        elif data == "help":
            await self.help_command(update, context)
        elif data.startswith("page_"):
            parts = data.split("_")
            page = int(parts[1])
            brand = parts[2] if len(parts) > 2 and parts[2] else None
            await self.show_cars(update, context, page, brand)
        elif data.startswith("brand_"):
            brand = data.replace("brand_", "")
            await self.show_cars(update, context, brand=brand)
        elif data.startswith("car_"):
            car_id = int(data.replace("car_", ""))
            await self.show_car_details(update, context, car_id)
        elif data.startswith("order_"):
            car_id = int(data.replace("order_", ""))
            await self.create_order(update, context, car_id)
    
    async def create_order(self, update: Update, context: ContextTypes.DEFAULT_TYPE, car_id: int):
        """Создание заказа"""
        user_id = update.effective_user.id
        car = db.get_car_by_id(car_id)
        
        if not car:
            await update.callback_query.answer("❌ Автомобиль не найден")
            return
        
        success = db.create_order(user_id, car_id)
        
        if success:
            text = f"""
✅ *Заказ оформлен!*

🚗 *Автомобиль:* {car['brand']} {car['model']} ({car['year']})
💰 *Цена:* {car['price']:,} ₽

📞 *Наш менеджер свяжется с вами в ближайшее время для уточнения деталей.*

*Контакты:*
📱 Телефон: +7 (XXX) XXX-XX-XX
📧 Email: info@autoshop.ru
            """
            
            keyboard = [[InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.edit_message_text(
                text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )
        else:
            await update.callback_query.answer("❌ Ошибка при создании заказа")
    
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
    
    def run(self):
        """Запуск бота"""
        logger.info("Запуск бота...")
        self.application.run_polling()

if __name__ == "__main__":
    bot = CarShopBot()
    bot.run()
