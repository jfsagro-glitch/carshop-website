"""
Обновленная схема базы данных для Telegram-бота продажи автомобилей
Соответствует техническому заданию
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class DatabaseManager:
    """Менеджер базы данных с полной схемой согласно ТЗ"""
    
    def __init__(self, db_path: str = "cars.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных с полной схемой"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                phone_number TEXT,
                is_admin BOOLEAN DEFAULT 0,
                is_seller BOOLEAN DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_activity TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица автомобилей (обновленная)
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
                drive_type TEXT,
                color TEXT,
                region TEXT,
                description TEXT,
                photos TEXT,
                is_active BOOLEAN DEFAULT 0,
                is_moderated BOOLEAN DEFAULT 0,
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
        
        # Таблица фильтров пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_filters (
                user_id INTEGER PRIMARY KEY,
                filter_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица заказов (обновленная)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                car_id INTEGER NOT NULL,
                order_date TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                contact_info TEXT,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (car_id) REFERENCES cars (car_id)
            )
        ''')
        
        # Таблица модерации объявлений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS moderation_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                car_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                moderator_id INTEGER,
                moderation_date TEXT,
                rejection_reason TEXT,
                FOREIGN KEY (car_id) REFERENCES cars (car_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (moderator_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица обратной связи
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                status TEXT DEFAULT 'new',
                admin_response TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Добавляем администратора по умолчанию
        self.add_default_admin()
    
    def add_default_admin(self):
        """Добавление администратора по умолчанию"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Проверяем, есть ли уже администратор
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO users (user_id, username, first_name, is_admin)
                VALUES (?, ?, ?, ?)
            ''', (123456789, 'admin', 'Администратор', 1))
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, 
                 last_name: str = None, phone_number: str = None) -> bool:
        """Добавление нового пользователя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, phone_number, last_activity)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name, phone_number, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка добавления пользователя: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Получение информации о пользователе"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        if row:
            columns = [description[0] for description in cursor.description]
            user = dict(zip(columns, row))
            conn.close()
            return user
        
        conn.close()
        return None
    
    def is_admin(self, user_id: int) -> bool:
        """Проверка, является ли пользователь администратором"""
        user = self.get_user(user_id)
        return user and user.get('is_admin', False)
    
    def is_seller(self, user_id: int) -> bool:
        """Проверка, является ли пользователь продавцом"""
        user = self.get_user(user_id)
        return user and user.get('is_seller', False)
    
    def add_car(self, user_id: int, brand: str, model: str, year: int, 
                mileage: int, price: int, engine_type: str = None,
                transmission: str = None, drive_type: str = None,
                color: str = None, region: str = None, description: str = None,
                photos: List[str] = None) -> int:
        """Добавление нового автомобиля"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            photos_json = json.dumps(photos or [])
            
            cursor.execute('''
                INSERT INTO cars (user_id, brand, model, year, mileage, price,
                               engine_type, transmission, drive_type, color, region,
                               description, photos, is_active, is_moderated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, brand, model, year, mileage, price, engine_type,
                 transmission, drive_type, color, region, description, photos_json,
                 0, 0))  # По умолчанию неактивен и не прошел модерацию
            
            car_id = cursor.lastrowid
            
            # Добавляем в очередь модерации
            cursor.execute('''
                INSERT INTO moderation_queue (car_id, user_id, status)
                VALUES (?, ?, ?)
            ''', (car_id, user_id, 'pending'))
            
            conn.commit()
            conn.close()
            return car_id
        except Exception as e:
            print(f"Ошибка добавления автомобиля: {e}")
            return None
    
    def get_cars(self, limit: int = 10, offset: int = 0, filters: Dict = None) -> List[Dict]:
        """Получение списка автомобилей с фильтрацией"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Базовый запрос
        query = '''
            SELECT c.*, u.first_name, u.username 
            FROM cars c 
            JOIN users u ON c.user_id = u.user_id 
            WHERE c.is_active = 1 AND c.is_moderated = 1
        '''
        params = []
        
        # Применяем фильтры
        if filters:
            if filters.get('brand'):
                query += ' AND c.brand = ?'
                params.append(filters['brand'])
            
            if filters.get('model'):
                query += ' AND c.model LIKE ?'
                params.append(f'%{filters["model"]}%')
            
            if filters.get('year_from'):
                query += ' AND c.year >= ?'
                params.append(filters['year_from'])
            
            if filters.get('year_to'):
                query += ' AND c.year <= ?'
                params.append(filters['year_to'])
            
            if filters.get('price_from'):
                query += ' AND c.price >= ?'
                params.append(filters['price_from'])
            
            if filters.get('price_to'):
                query += ' AND c.price <= ?'
                params.append(filters['price_to'])
            
            if filters.get('mileage_max'):
                query += ' AND c.mileage <= ?'
                params.append(filters['mileage_max'])
            
            if filters.get('engine_type'):
                query += ' AND c.engine_type = ?'
                params.append(filters['engine_type'])
            
            if filters.get('transmission'):
                query += ' AND c.transmission = ?'
                params.append(filters['transmission'])
            
            if filters.get('region'):
                query += ' AND c.region = ?'
                params.append(filters['region'])
        
        query += ' ORDER BY c.created_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        cars = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return cars
    
    def get_car_by_id(self, car_id: int) -> Optional[Dict]:
        """Получение автомобиля по ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.*, u.first_name, u.username, u.phone_number
            FROM cars c 
            JOIN users u ON c.user_id = u.user_id 
            WHERE c.car_id = ?
        ''', (car_id,))
        
        row = cursor.fetchone()
        if row:
            columns = [description[0] for description in cursor.description]
            car = dict(zip(columns, row))
            conn.close()
            return car
        
        conn.close()
        return None
    
    def add_to_favorites(self, user_id: int, car_id: int) -> bool:
        """Добавление автомобиля в избранное"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO favorites (user_id, car_id)
                VALUES (?, ?)
            ''', (user_id, car_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка добавления в избранное: {e}")
            return False
    
    def remove_from_favorites(self, user_id: int, car_id: int) -> bool:
        """Удаление автомобиля из избранного"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM favorites WHERE user_id = ? AND car_id = ?
            ''', (user_id, car_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка удаления из избранного: {e}")
            return False
    
    def get_favorites(self, user_id: int) -> List[Dict]:
        """Получение избранных автомобилей пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.*, u.first_name, u.username
            FROM cars c 
            JOIN favorites f ON c.car_id = f.car_id
            JOIN users u ON c.user_id = u.user_id
            WHERE f.user_id = ? AND c.is_active = 1 AND c.is_moderated = 1
            ORDER BY f.created_at DESC
        ''', (user_id,))
        
        columns = [description[0] for description in cursor.description]
        cars = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return cars
    
    def save_user_filters(self, user_id: int, filters: Dict) -> bool:
        """Сохранение фильтров пользователя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            filters_json = json.dumps(filters)
            cursor.execute('''
                INSERT OR REPLACE INTO user_filters (user_id, filter_json, updated_at)
                VALUES (?, ?, ?)
            ''', (user_id, filters_json, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка сохранения фильтров: {e}")
            return False
    
    def get_user_filters(self, user_id: int) -> Dict:
        """Получение сохраненных фильтров пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT filter_json FROM user_filters WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        if row:
            try:
                filters = json.loads(row[0])
                conn.close()
                return filters
            except:
                pass
        
        conn.close()
        return {}
    
    def get_moderation_queue(self) -> List[Dict]:
        """Получение очереди модерации"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT mq.*, c.brand, c.model, c.year, c.price, u.first_name, u.username
            FROM moderation_queue mq
            JOIN cars c ON mq.car_id = c.car_id
            JOIN users u ON mq.user_id = u.user_id
            WHERE mq.status = 'pending'
            ORDER BY mq.id ASC
        ''')
        
        columns = [description[0] for description in cursor.description]
        queue = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return queue
    
    def moderate_car(self, car_id: int, moderator_id: int, approved: bool, 
                     rejection_reason: str = None) -> bool:
        """Модерация автомобиля"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if approved:
                # Одобряем автомобиль
                cursor.execute('''
                    UPDATE cars SET is_active = 1, is_moderated = 1 WHERE car_id = ?
                ''', (car_id,))
                
                cursor.execute('''
                    UPDATE moderation_queue 
                    SET status = 'approved', moderator_id = ?, moderation_date = ?
                    WHERE car_id = ?
                ''', (moderator_id, datetime.now().isoformat(), car_id))
            else:
                # Отклоняем автомобиль
                cursor.execute('''
                    UPDATE cars SET is_active = 0, is_moderated = 1 WHERE car_id = ?
                ''', (car_id,))
                
                cursor.execute('''
                    UPDATE moderation_queue 
                    SET status = 'rejected', moderator_id = ?, moderation_date = ?, rejection_reason = ?
                    WHERE car_id = ?
                ''', (moderator_id, datetime.now().isoformat(), rejection_reason, car_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка модерации: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """Получение статистики для администратора"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Общее количество пользователей
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        # Количество активных объявлений
        cursor.execute('SELECT COUNT(*) FROM cars WHERE is_active = 1 AND is_moderated = 1')
        active_cars = cursor.fetchone()[0]
        
        # Количество объявлений на модерации
        cursor.execute('SELECT COUNT(*) FROM moderation_queue WHERE status = "pending"')
        pending_moderation = cursor.fetchone()[0]
        
        # Количество заказов
        cursor.execute('SELECT COUNT(*) FROM orders')
        total_orders = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_users': total_users,
            'active_cars': active_cars,
            'pending_moderation': pending_moderation,
            'total_orders': total_orders
        }
    
    def add_feedback(self, user_id: int, message: str) -> bool:
        """Добавление обратной связи"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO feedback (user_id, message)
                VALUES (?, ?)
            ''', (user_id, message))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка добавления обратной связи: {e}")
            return False

# Инициализация базы данных
db = DatabaseManager()




