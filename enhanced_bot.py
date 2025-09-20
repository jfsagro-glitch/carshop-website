"""
Улучшенный Telegram-бот для продажи автомобилей
Полная реализация согласно техническому заданию
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from database_schema import DatabaseManager

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
(WAITING_PHOTOS, WAITING_BRAND, WAITING_MODEL, WAITING_YEAR, WAITING_MILEAGE,
 WAITING_ENGINE_TYPE, WAITING_TRANSMISSION, WAITING_DRIVE_TYPE, WAITING_COLOR,
 WAITING_REGION, WAITING_PRICE, WAITING_DESCRIPTION, WAITING_CONTACT) = range(13)

# Инициализация базы данных
db = DatabaseManager()

class CarSalesBot:
    """Основной класс бота для продажи автомобилей"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.application = Application.builder().token(bot_token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка всех обработчиков"""
        # Основные команды
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("catalog", self.catalog_command))
        self.application.add_handler(CommandHandler("filters", self.filters_command))
        self.application.add_handler(CommandHandler("reset", self.reset_command))
        self.application.add_handler(CommandHandler("favorites", self.favorites_command))
        self.application.add_handler(CommandHandler("sell", self.sell_command))
        self.application.add_handler(CommandHandler("admin", self.admin_command))
        
        # ConversationHandler для процесса продажи
        sell_conversation = ConversationHandler(
            entry_points=[CommandHandler("sell", self.sell_command)],
            states={
                WAITING_PHOTOS: [MessageHandler(filters.PHOTO, self.handle_photos)],
                WAITING_BRAND: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_brand)],
                WAITING_MODEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_model)],
                WAITING_YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_year)],
                WAITING_MILEAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_mileage)],
                WAITING_ENGINE_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_engine_type)],
                WAITING_TRANSMISSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_transmission)],
                WAITING_DRIVE_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_drive_type)],
                WAITING_COLOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_color)],
                WAITING_REGION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_region)],
                WAITING_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_price)],
                WAITING_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_description)],
                WAITING_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_contact)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel_sell)]
        )
        self.application.add_handler(sell_conversation)
        
        # Обработчики кнопок
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Обработчик текстовых сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        user_id = user.id
        
        # Регистрируем пользователя
        db.add_user(
            user_id=user_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        keyboard = [
            [InlineKeyboardButton("🚗 Каталог авто", callback_data="catalog")],
            [InlineKeyboardButton("🔍 Поиск по фильтрам", callback_data="filters")],
            [InlineKeyboardButton("💝 Избранное", callback_data="favorites")],
            [InlineKeyboardButton("💰 Продать авто", callback_data="sell")],
            [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")],
            [InlineKeyboardButton("📞 Обратная связь", callback_data="feedback")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = """
🚗 *Добро пожаловать в CarSalesBot!*

Здесь вы можете:
• 🚗 Просматривать каталог автомобилей
• 🔍 Искать по фильтрам (марка, год, цена, пробег)
• 💝 Сохранять понравившиеся авто в избранное
• 💰 Размещать свои объявления
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
/filters - Настройка фильтров поиска
/favorites - Ваши избранные автомобили
/sell - Разместить объявление о продаже
/reset - Сбросить текущую сессию
/help - Эта справка

*🔍 Как пользоваться:*
1. Используйте "Каталог авто" для просмотра всех автомобилей
2. Настройте фильтры для поиска по параметрам
3. Добавляйте понравившиеся авто в избранное
4. Используйте "Продать авто" для размещения объявления

*📞 Поддержка:*
Если у вас есть вопросы, используйте "Обратная связь"
        """
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def catalog_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /catalog"""
        await self.show_cars(update, context, page=0)
    
    async def filters_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /filters"""
        await self.show_filters_menu(update, context)
    
    async def reset_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /reset"""
        # Очищаем контекст пользователя
        context.user_data.clear()
        
        await update.message.reply_text(
            "🔄 Сессия сброшена. Используйте /start для начала работы.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def favorites_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /favorites"""
        user_id = update.effective_user.id
        favorites = db.get_favorites(user_id)
        
        if not favorites:
            await update.message.reply_text(
                "💝 У вас пока нет избранных автомобилей.\n\n"
                "Добавляйте понравившиеся авто в избранное, нажимая ❤️ в каталоге.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        text = f"💝 *Ваши избранные автомобили* ({len(favorites)} шт.)\n\n"
        
        keyboard = []
        for car in favorites[:10]:  # Показываем первые 10
            text += f"🚗 *{car['brand']} {car['model']} ({car['year']})*\n"
            text += f"💰 {car['price']:,} ₽ | 🛣️ {car['mileage']:,} км\n\n"
            
            keyboard.append([InlineKeyboardButton(
                f"🚗 {car['brand']} {car['model']} - {car['price']:,} ₽",
                callback_data=f"car_{car['car_id']}"
            )])
        
        keyboard.append([InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
        )
    
    async def sell_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /sell"""
        user_id = update.effective_user.id
        
        # Проверяем, не начат ли уже процесс продажи
        if 'sell_data' in context.user_data:
            await update.message.reply_text(
                "⚠️ У вас уже есть незавершенное объявление.\n"
                "Используйте /reset для отмены или продолжите заполнение.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Инициализируем данные продажи
        context.user_data['sell_data'] = {
            'photos': [],
            'current_step': 'photos'
        }
        
        await update.message.reply_text(
            "💰 *Размещение объявления о продаже*\n\n"
            "📸 *Шаг 1 из 13: Загрузите фотографии автомобиля*\n\n"
            "Отправьте фотографии автомобиля (можно несколько).\n"
            "После загрузки всех фото отправьте команду /done",
            parse_mode=ParseMode.MARKDOWN
        )
        
        return WAITING_PHOTOS
    
    async def handle_photos(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка загруженных фотографий"""
        if 'sell_data' not in context.user_data:
            return ConversationHandler.END
        
        photo = update.message.photo[-1]  # Берем фото наивысшего качества
        file_id = photo.file_id
        
        context.user_data['sell_data']['photos'].append(file_id)
        
        await update.message.reply_text(
            f"✅ Фото добавлено! Загружено: {len(context.user_data['sell_data']['photos'])}\n\n"
            "Отправьте еще фото или команду /done для продолжения."
        )
        
        return WAITING_PHOTOS
    
    async def handle_brand(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода марки"""
        brand = update.message.text.strip()
        context.user_data['sell_data']['brand'] = brand
        
        await update.message.reply_text(
            f"✅ Марка: {brand}\n\n"
            "🚗 *Шаг 3 из 13: Введите модель автомобиля*",
            parse_mode=ParseMode.MARKDOWN
        )
        
        return WAITING_MODEL
    
    async def handle_model(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода модели"""
        model = update.message.text.strip()
        context.user_data['sell_data']['model'] = model
        
        await update.message.reply_text(
            f"✅ Модель: {model}\n\n"
            "📅 *Шаг 4 из 13: Введите год выпуска*",
            parse_mode=ParseMode.MARKDOWN
        )
        
        return WAITING_YEAR
    
    async def handle_year(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода года"""
        try:
            year = int(update.message.text.strip())
            if year < 1990 or year > 2024:
                await update.message.reply_text(
                    "❌ Некорректный год. Введите год от 1990 до 2024:"
                )
                return WAITING_YEAR
            
            context.user_data['sell_data']['year'] = year
            
            await update.message.reply_text(
                f"✅ Год выпуска: {year}\n\n"
                "🛣️ *Шаг 5 из 13: Введите пробег в км*",
                parse_mode=ParseMode.MARKDOWN
            )
            
            return WAITING_MILEAGE
        except ValueError:
            await update.message.reply_text("❌ Введите корректный год (число):")
            return WAITING_YEAR
    
    async def handle_mileage(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода пробега"""
        try:
            mileage = int(update.message.text.strip())
            if mileage < 0:
                await update.message.reply_text("❌ Пробег не может быть отрицательным:")
                return WAITING_MILEAGE
            
            context.user_data['sell_data']['mileage'] = mileage
            
            keyboard = [
                [InlineKeyboardButton("⛽ Бензин", callback_data="engine_Бензин")],
                [InlineKeyboardButton("⛽ Дизель", callback_data="engine_Дизель")],
                [InlineKeyboardButton("🔋 Электро", callback_data="engine_Электро")],
                [InlineKeyboardButton("🔋 Гибрид", callback_data="engine_Гибрид")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✅ Пробег: {mileage:,} км\n\n"
                "⛽ *Шаг 6 из 13: Выберите тип двигателя*",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
            return WAITING_ENGINE_TYPE
        except ValueError:
            await update.message.reply_text("❌ Введите корректный пробег (число):")
            return WAITING_MILEAGE
    
    async def handle_engine_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка выбора типа двигателя"""
        engine_type = update.callback_query.data.replace("engine_", "")
        context.user_data['sell_data']['engine_type'] = engine_type
        
        keyboard = [
            [InlineKeyboardButton("🔄 Автомат", callback_data="transmission_Автомат")],
            [InlineKeyboardButton("⚙️ Механика", callback_data="transmission_Механика")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            f"✅ Тип двигателя: {engine_type}\n\n"
            "🔧 *Шаг 7 из 13: Выберите коробку передач*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        
        return WAITING_TRANSMISSION
    
    async def handle_transmission(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка выбора КПП"""
        transmission = update.callback_query.data.replace("transmission_", "")
        context.user_data['sell_data']['transmission'] = transmission
        
        keyboard = [
            [InlineKeyboardButton("🚗 Передний", callback_data="drive_Передний")],
            [InlineKeyboardButton("🚗 Задний", callback_data="drive_Задний")],
            [InlineKeyboardButton("🚗 Полный", callback_data="drive_Полный")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            f"✅ КПП: {transmission}\n\n"
            "🚗 *Шаг 8 из 13: Выберите тип привода*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        
        return WAITING_DRIVE_TYPE
    
    async def handle_drive_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка выбора привода"""
        drive_type = update.callback_query.data.replace("drive_", "")
        context.user_data['sell_data']['drive_type'] = drive_type
        
        await update.callback_query.edit_message_text(
            f"✅ Привод: {drive_type}\n\n"
            "🎨 *Шаг 9 из 13: Введите цвет автомобиля*",
            parse_mode=ParseMode.MARKDOWN
        )
        
        return WAITING_COLOR
    
    async def handle_color(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода цвета"""
        color = update.message.text.strip()
        context.user_data['sell_data']['color'] = color
        
        await update.message.reply_text(
            f"✅ Цвет: {color}\n\n"
            "📍 *Шаг 10 из 13: Введите регион расположения авто*",
            parse_mode=ParseMode.MARKDOWN
        )
        
        return WAITING_REGION
    
    async def handle_region(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода региона"""
        region = update.message.text.strip()
        context.user_data['sell_data']['region'] = region
        
        await update.message.reply_text(
            f"✅ Регион: {region}\n\n"
            "💰 *Шаг 11 из 13: Введите цену в рублях*",
            parse_mode=ParseMode.MARKDOWN
        )
        
        return WAITING_PRICE
    
    async def handle_price(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода цены"""
        try:
            price = int(update.message.text.strip().replace(' ', '').replace(',', ''))
            if price <= 0:
                await update.message.reply_text("❌ Цена должна быть больше 0:")
                return WAITING_PRICE
            
            context.user_data['sell_data']['price'] = price
            
            await update.message.reply_text(
                f"✅ Цена: {price:,} ₽\n\n"
                "📝 *Шаг 12 из 13: Введите описание автомобиля*\n"
                "(состояние, комплектация, особенности и т.д.)",
                parse_mode=ParseMode.MARKDOWN
            )
            
            return WAITING_DESCRIPTION
        except ValueError:
            await update.message.reply_text("❌ Введите корректную цену (число):")
            return WAITING_PRICE
    
    async def handle_description(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода описания"""
        description = update.message.text.strip()
        context.user_data['sell_data']['description'] = description
        
        await update.message.reply_text(
            f"✅ Описание: {description}\n\n"
            "📞 *Шаг 13 из 13: Введите контактные данные*\n"
            "(телефон, email или другие способы связи)",
            parse_mode=ParseMode.MARKDOWN
        )
        
        return WAITING_CONTACT
    
    async def handle_contact(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода контактов"""
        contact = update.message.text.strip()
        context.user_data['sell_data']['contact'] = contact
        
        # Показываем превью объявления
        await self.show_sell_preview(update, context)
        
        return ConversationHandler.END
    
    async def show_sell_preview(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ превью объявления для подтверждения"""
        data = context.user_data['sell_data']
        
        text = f"""
📋 *Превью объявления:*

🚗 *{data['brand']} {data['model']} ({data['year']})*
💰 Цена: {data['price']:,} ₽
🛣️ Пробег: {data['mileage']:,} км
⛽ Двигатель: {data['engine_type']}
🔧 КПП: {data['transmission']}
🚗 Привод: {data['drive_type']}
🎨 Цвет: {data['color']}
📍 Регион: {data['region']}

📝 *Описание:*
{data['description']}

📞 *Контакты:*
{data['contact']}

📸 Фотографий: {len(data['photos'])}
        """
        
        keyboard = [
            [InlineKeyboardButton("✅ Опубликовать", callback_data="publish_ad")],
            [InlineKeyboardButton("❌ Отменить", callback_data="cancel_ad")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
        )
    
    async def cancel_sell(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отмена процесса продажи"""
        if 'sell_data' in context.user_data:
            del context.user_data['sell_data']
        
        await update.message.reply_text(
            "❌ Размещение объявления отменено.\n"
            "Используйте /start для возврата в главное меню."
        )
        
        return ConversationHandler.END
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /admin"""
        user_id = update.effective_user.id
        
        if not db.is_admin(user_id):
            await update.message.reply_text("❌ У вас нет прав администратора")
            return
        
        await self.show_admin_panel(update, context)
    
    async def show_admin_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ панели администратора"""
        stats = db.get_statistics()
        
        text = f"""
👨‍💼 *Панель администратора*

📊 *Статистика:*
👥 Пользователей: {stats['total_users']}
🚗 Активных объявлений: {stats['active_cars']}
⏳ На модерации: {stats['pending_moderation']}
📦 Заказов: {stats['total_orders']}
        """
        
        keyboard = [
            [InlineKeyboardButton("📋 Модерация объявлений", callback_data="admin_moderation")],
            [InlineKeyboardButton("👥 Управление пользователями", callback_data="admin_users")],
            [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast")],
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
        )
    
    async def show_cars(self, update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0, filters: Dict = None):
        """Показ списка автомобилей"""
        cars = db.get_cars(limit=5, offset=page*5, filters=filters)
        
        if not cars:
            text = "❌ Автомобили не найдены"
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]]
        else:
            text = f"🚗 *Каталог автомобилей* (страница {page + 1})\n\n"
            
            keyboard = []
            for car in cars:
                text += f"🚗 *{car['brand']} {car['model']} ({car['year']})*\n"
                text += f"💰 {car['price']:,} ₽ | 🛣️ {car['mileage']:,} км\n"
                text += f"📍 {car.get('region', 'Не указан')}\n\n"
                
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
        car = db.get_car_by_id(car_id)
        
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
🚗 *Привод:* {car.get('drive_type', 'Не указан')}
🎨 *Цвет:* {car.get('color', 'Не указан')}
📍 *Регион:* {car.get('region', 'Не указан')}

📝 *Описание:*
{car.get('description', 'Описание отсутствует')}

👤 *Продавец:* {car.get('first_name', 'Не указано')}
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
        
        if photos:
            try:
                media = []
                for i, photo_url in enumerate(photos[:5]):
                    if i == 0:
                        media.append(InputMediaPhoto(media=photo_url, caption=text, parse_mode=ParseMode.MARKDOWN))
                    else:
                        media.append(InputMediaPhoto(media=photo_url))
                
                await update.callback_query.delete_message()
                await context.bot.send_media_group(
                    chat_id=update.effective_chat.id,
                    media=media
                )
                
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Выберите действие:",
                    reply_markup=reply_markup
                )
                return
            except Exception as e:
                logger.error(f"Ошибка отправки фотографий: {e}")
        
        await update.callback_query.edit_message_text(
            text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
        )
    
    async def show_filters_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ меню фильтров"""
        text = """
🔍 *Настройка фильтров поиска*

Выберите параметры для фильтрации автомобилей:
        """
        
        keyboard = [
            [InlineKeyboardButton("🏭 Марка", callback_data="filter_brand")],
            [InlineKeyboardButton("📅 Год выпуска", callback_data="filter_year")],
            [InlineKeyboardButton("💰 Цена", callback_data="filter_price")],
            [InlineKeyboardButton("🛣️ Пробег", callback_data="filter_mileage")],
            [InlineKeyboardButton("⛽ Тип двигателя", callback_data="filter_engine")],
            [InlineKeyboardButton("🔧 КПП", callback_data="filter_transmission")],
            [InlineKeyboardButton("📍 Регион", callback_data="filter_region")],
            [InlineKeyboardButton("🔍 Применить фильтры", callback_data="apply_filters")],
            [InlineKeyboardButton("🗑️ Сбросить фильтры", callback_data="clear_filters")],
            [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
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
        elif data == "filters":
            await self.show_filters_menu(update, context)
        elif data == "favorites":
            await self.favorites_command(update, context)
        elif data == "sell":
            await self.sell_command(update, context)
        elif data == "help":
            await self.help_command(update, context)
        elif data == "feedback":
            await self.show_feedback_form(update, context)
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
        elif data == "publish_ad":
            await self.publish_advertisement(update, context)
        elif data == "cancel_ad":
            await self.cancel_advertisement(update, context)
        elif data == "admin_moderation":
            await self.show_moderation_queue(update, context)
        elif data.startswith("moderate_"):
            parts = data.split("_")
            car_id = int(parts[1])
            action = parts[2]
            await self.moderate_car(update, context, car_id, action)
    
    async def toggle_favorite(self, update: Update, context: ContextTypes.DEFAULT_TYPE, car_id: int):
        """Добавление/удаление из избранного"""
        user_id = update.effective_user.id
        
        # Проверяем, есть ли уже в избранном
        favorites = db.get_favorites(user_id)
        car_ids = [fav['car_id'] for fav in favorites]
        
        if car_id in car_ids:
            # Удаляем из избранного
            db.remove_from_favorites(user_id, car_id)
            await query.answer("💔 Удалено из избранного")
        else:
            # Добавляем в избранное
            db.add_to_favorites(user_id, car_id)
            await query.answer("❤️ Добавлено в избранное")
    
    async def show_contact_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE, car_id: int):
        """Показ контактной информации продавца"""
        car = db.get_car_by_id(car_id)
        
        if not car:
            await update.callback_query.answer("❌ Автомобиль не найден")
            return
        
        text = f"""
📞 *Контактная информация*

🚗 *Автомобиль:* {car['brand']} {car['model']} ({car['year']})
💰 *Цена:* {car['price']:,} ₽

👤 *Продавец:* {car.get('first_name', 'Не указано')}
📱 *Телефон:* {car.get('phone_number', 'Не указан')}

*Для связи с продавцом используйте указанные контакты.*
        """
        
        keyboard = [[InlineKeyboardButton("🔙 К автомобилю", callback_data=f"car_{car_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
        )
    
    async def publish_advertisement(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Публикация объявления"""
        if 'sell_data' not in context.user_data:
            await update.callback_query.answer("❌ Нет данных для публикации")
            return
        
        data = context.user_data['sell_data']
        user_id = update.effective_user.id
        
        # Добавляем автомобиль в базу данных
        car_id = db.add_car(
            user_id=user_id,
            brand=data['brand'],
            model=data['model'],
            year=data['year'],
            mileage=data['mileage'],
            price=data['price'],
            engine_type=data.get('engine_type'),
            transmission=data.get('transmission'),
            drive_type=data.get('drive_type'),
            color=data.get('color'),
            region=data.get('region'),
            description=data.get('description'),
            photos=data['photos']
        )
        
        if car_id:
            # Очищаем данные продажи
            del context.user_data['sell_data']
            
            await update.callback_query.edit_message_text(
                "✅ *Объявление отправлено на модерацию!*\n\n"
                "Ваше объявление будет проверено администратором и опубликовано в течение 24 часов.\n\n"
                "Используйте /start для возврата в главное меню.",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.callback_query.edit_message_text(
                "❌ *Ошибка при публикации объявления*\n\n"
                "Попробуйте еще раз или обратитесь в поддержку.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def cancel_advertisement(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отмена публикации объявления"""
        if 'sell_data' in context.user_data:
            del context.user_data['sell_data']
        
        await update.callback_query.edit_message_text(
            "❌ *Публикация объявления отменена*\n\n"
            "Используйте /start для возврата в главное меню.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def show_moderation_queue(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ очереди модерации"""
        queue = db.get_moderation_queue()
        
        if not queue:
            await update.callback_query.edit_message_text(
                "✅ *Нет объявлений на модерации*\n\n"
                "Все объявления обработаны.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        text = f"📋 *Очередь модерации* ({len(queue)} объявлений)\n\n"
        
        keyboard = []
        for item in queue[:5]:  # Показываем первые 5
            text += f"🚗 *{item['brand']} {item['model']} ({item['year']})*\n"
            text += f"💰 {item['price']:,} ₽ | 👤 {item['first_name']}\n\n"
            
            keyboard.append([
                InlineKeyboardButton("✅ Одобрить", callback_data=f"moderate_{item['car_id']}_approve"),
                InlineKeyboardButton("❌ Отклонить", callback_data=f"moderate_{item['car_id']}_reject")
            ])
        
        keyboard.append([InlineKeyboardButton("🔙 Админ-панель", callback_data="admin_panel")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
        )
    
    async def moderate_car(self, update: Update, context: ContextTypes.DEFAULT_TYPE, car_id: int, action: str):
        """Модерация автомобиля"""
        moderator_id = update.effective_user.id
        
        if action == "approve":
            success = db.moderate_car(car_id, moderator_id, True)
            if success:
                await update.callback_query.answer("✅ Объявление одобрено")
            else:
                await update.callback_query.answer("❌ Ошибка при одобрении")
        elif action == "reject":
            # Здесь можно добавить запрос причины отклонения
            success = db.moderate_car(car_id, moderator_id, False, "Не соответствует требованиям")
            if success:
                await update.callback_query.answer("❌ Объявление отклонено")
            else:
                await update.callback_query.answer("❌ Ошибка при отклонении")
        
        # Обновляем очередь модерации
        await self.show_moderation_queue(update, context)
    
    async def show_feedback_form(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ формы обратной связи"""
        text = """
📞 *Обратная связь*

Если у вас есть вопросы, предложения или жалобы, напишите нам сообщение.

Просто отправьте текстовое сообщение, и мы получим его.
        """
        
        keyboard = [[InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        text = update.message.text.lower()
        user_id = update.effective_user.id
        
        # Проверяем, не является ли это обратной связью
        if any(word in text for word in ['вопрос', 'проблема', 'жалоба', 'предложение']):
            # Сохраняем обратную связь
            db.add_feedback(user_id, update.message.text)
            await update.message.reply_text(
                "✅ Ваше сообщение получено! Мы свяжемся с вами в ближайшее время."
            )
        elif any(word in text for word in ['привет', 'hello', 'hi', 'здравствуй']):
            await update.message.reply_text("👋 Привет! Используйте /start для начала работы с ботом.")
        elif any(word in text for word in ['помощь', 'help', 'справка']):
            await self.help_command(update, context)
        else:
            await update.message.reply_text(
                "Не понимаю ваше сообщение. Используйте /start для начала работы."
            )
    
    def run(self):
        """Запуск бота"""
        logger.info("Запуск CarSalesBot...")
        self.application.run_polling()

def main():
    """Основная функция"""
    try:
        # Пытаемся импортировать конфигурацию
        from config import BOT_TOKEN
    except ImportError:
        # Если config.py не найден, используем токен по умолчанию
        BOT_TOKEN = "8431697857:AAFBcnKw3BCX_jL5QwfUN7aCj71nNiSRBh4"
        print("⚠️ Файл config.py не найден, используется токен по умолчанию")
    
    bot = CarSalesBot(BOT_TOKEN)
    bot.run()

if __name__ == "__main__":
    main()
