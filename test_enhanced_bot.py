#!/usr/bin/env python3
"""
Тесты для CarSalesBot
"""

import unittest
import tempfile
import os
import json
import sqlite3
from unittest.mock import Mock, patch
from database_schema import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    """Тесты для DatabaseManager"""
    
    def setUp(self):
        """Настройка тестовой базы данных"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        self.db = DatabaseManager(self.temp_db.name)
    
    def tearDown(self):
        """Очистка после тестов"""
        os.unlink(self.temp_db.name)
    
    def test_add_user(self):
        """Тест добавления пользователя"""
        success = self.db.add_user(
            user_id=123456,
            username="testuser",
            first_name="Test",
            last_name="User"
        )
        self.assertTrue(success)
        
        user = self.db.get_user(123456)
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], "testuser")
        self.assertEqual(user['first_name'], "Test")
    
    def test_add_car(self):
        """Тест добавления автомобиля"""
        # Сначала добавляем пользователя
        self.db.add_user(123456, "testuser", "Test")
        
        car_id = self.db.add_car(
            user_id=123456,
            brand="Toyota",
            model="Camry",
            year=2020,
            mileage=50000,
            price=2000000,
            engine_type="Бензин",
            transmission="Автомат",
            color="Белый",
            description="Отличное состояние"
        )
        
        self.assertIsNotNone(car_id)
        
        car = self.db.get_car_by_id(car_id)
        self.assertIsNotNone(car)
        self.assertEqual(car['brand'], "Toyota")
        self.assertEqual(car['model'], "Camry")
    
    def test_get_cars_with_filters(self):
        """Тест получения автомобилей с фильтрами"""
        # Добавляем пользователя
        self.db.add_user(123456, "testuser", "Test")
        
        # Добавляем несколько автомобилей
        car1_id = self.db.add_car(
            user_id=123456,
            brand="Toyota",
            model="Camry",
            year=2020,
            mileage=50000,
            price=2000000,
            engine_type="Бензин"
        )
        
        car2_id = self.db.add_car(
            user_id=123456,
            brand="BMW",
            model="X5",
            year=2019,
            mileage=60000,
            price=4000000,
            engine_type="Бензин"
        )
        
        # Одобряем автомобили
        self.db.moderate_car(car1_id, 123456, True)
        self.db.moderate_car(car2_id, 123456, True)
        
        # Тест фильтрации по марке
        cars = self.db.get_cars(filters={'brand': 'Toyota'})
        self.assertEqual(len(cars), 1)
        self.assertEqual(cars[0]['brand'], 'Toyota')
        
        # Тест фильтрации по цене
        cars = self.db.get_cars(filters={'price_to': 3000000})
        self.assertEqual(len(cars), 1)
        self.assertEqual(cars[0]['brand'], 'Toyota')
    
    def test_favorites(self):
        """Тест системы избранного"""
        # Добавляем пользователя
        self.db.add_user(123456, "testuser", "Test")
        
        # Добавляем автомобиль
        car_id = self.db.add_car(
            user_id=123456,
            brand="Toyota",
            model="Camry",
            year=2020,
            mileage=50000,
            price=2000000
        )
        
        # Одобряем автомобиль
        self.db.moderate_car(car_id, 123456, True)
        
        # Добавляем в избранное
        success = self.db.add_to_favorites(123456, car_id)
        self.assertTrue(success)
        
        # Проверяем избранное
        favorites = self.db.get_favorites(123456)
        self.assertEqual(len(favorites), 1)
        self.assertEqual(favorites[0]['car_id'], car_id)
        
        # Удаляем из избранного
        success = self.db.remove_from_favorites(123456, car_id)
        self.assertTrue(success)
        
        favorites = self.db.get_favorites(123456)
        self.assertEqual(len(favorites), 0)
    
    def test_moderation_queue(self):
        """Тест очереди модерации"""
        # Добавляем пользователя
        self.db.add_user(123456, "testuser", "Test")
        
        # Добавляем автомобиль (он должен попасть в очередь модерации)
        car_id = self.db.add_car(
            user_id=123456,
            brand="Toyota",
            model="Camry",
            year=2020,
            mileage=50000,
            price=2000000
        )
        
        # Проверяем очередь модерации
        queue = self.db.get_moderation_queue()
        self.assertEqual(len(queue), 1)
        self.assertEqual(queue[0]['car_id'], car_id)
        self.assertEqual(queue[0]['status'], 'pending')
        
        # Одобряем автомобиль
        success = self.db.moderate_car(car_id, 123456, True)
        self.assertTrue(success)
        
        # Проверяем, что автомобиль стал активным
        car = self.db.get_car_by_id(car_id)
        self.assertTrue(car['is_active'])
        self.assertTrue(car['is_moderated'])
    
    def test_user_filters(self):
        """Тест сохранения фильтров пользователя"""
        # Добавляем пользователя
        self.db.add_user(123456, "testuser", "Test")
        
        # Сохраняем фильтры
        filters = {
            'brand': 'Toyota',
            'year_from': 2018,
            'price_to': 3000000
        }
        
        success = self.db.save_user_filters(123456, filters)
        self.assertTrue(success)
        
        # Получаем фильтры
        saved_filters = self.db.get_user_filters(123456)
        self.assertEqual(saved_filters, filters)
    
    def test_statistics(self):
        """Тест получения статистики"""
        # Добавляем пользователей
        self.db.add_user(123456, "user1", "User1")
        self.db.add_user(789012, "user2", "User2")
        
        # Добавляем автомобиль
        car_id = self.db.add_car(
            user_id=123456,
            brand="Toyota",
            model="Camry",
            year=2020,
            mileage=50000,
            price=2000000
        )
        
        # Одобряем автомобиль
        self.db.moderate_car(car_id, 123456, True)
        
        # Получаем статистику
        stats = self.db.get_statistics()
        # Учитываем, что может быть администратор по умолчанию
        self.assertGreaterEqual(stats['total_users'], 2)
        self.assertEqual(stats['active_cars'], 1)
        self.assertEqual(stats['pending_moderation'], 0)

class TestBotFunctionality(unittest.TestCase):
    """Тесты функциональности бота"""
    
    def setUp(self):
        """Настройка тестов"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        self.db = DatabaseManager(self.temp_db.name)
    
    def tearDown(self):
        """Очистка после тестов"""
        os.unlink(self.temp_db.name)
    
    def test_admin_check(self):
        """Тест проверки прав администратора"""
        # Добавляем обычного пользователя
        self.db.add_user(123456, "user", "User")
        
        # Добавляем администратора через прямое обновление БД
        self.db.add_user(789012, "admin", "Admin")
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET is_admin = 1 WHERE user_id = ?', (789012,))
        conn.commit()
        conn.close()
        
        # Проверяем права
        self.assertFalse(self.db.is_admin(123456))
        self.assertTrue(self.db.is_admin(789012))
    
    def test_seller_check(self):
        """Тест проверки прав продавца"""
        # Добавляем обычного пользователя
        self.db.add_user(123456, "user", "User")
        
        # Добавляем продавца через прямое обновление БД
        self.db.add_user(789012, "seller", "Seller")
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET is_seller = 1 WHERE user_id = ?', (789012,))
        conn.commit()
        conn.close()
        
        # Проверяем права
        self.assertFalse(self.db.is_seller(123456))
        self.assertTrue(self.db.is_seller(789012))

def run_tests():
    """Запуск всех тестов"""
    print("🧪 Запуск тестов CarSalesBot...")
    print("=" * 50)
    
    # Создаем test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем тесты
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseManager))
    suite.addTests(loader.loadTestsFromTestCase(TestBotFunctionality))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Выводим результаты
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ Все тесты прошли успешно!")
    else:
        print(f"❌ Тесты завершились с ошибками:")
        print(f"   Ошибок: {len(result.errors)}")
        print(f"   Провалов: {len(result.failures)}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
