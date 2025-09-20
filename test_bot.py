"""
Тесты для бота автосалона
"""

import unittest
import sqlite3
import os
from bot import CarDatabase, Car

class TestCarDatabase(unittest.TestCase):
    """Тесты для базы данных автомобилей"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.test_db_path = "test_cars.db"
        self.db = CarDatabase(self.test_db_path)
    
    def tearDown(self):
        """Очистка после каждого теста"""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_database_creation(self):
        """Тест создания базы данных"""
        self.assertTrue(os.path.exists(self.test_db_path))
    
    def test_add_car(self):
        """Тест добавления автомобиля"""
        cars_before = len(self.db.get_cars())
        
        # Добавляем тестовый автомобиль
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO cars (brand, model, year, price, mileage, fuel_type, 
                           transmission, color, description, photos)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('TestBrand', 'TestModel', 2023, 1000000, 0, 'Бензин', 
              'Автомат', 'Белый', 'Тестовый автомобиль', '[]'))
        conn.commit()
        conn.close()
        
        cars_after = len(self.db.get_cars())
        self.assertEqual(cars_after, cars_before + 1)
    
    def test_get_cars(self):
        """Тест получения списка автомобилей"""
        cars = self.db.get_cars()
        self.assertIsInstance(cars, list)
        self.assertGreater(len(cars), 0)  # Должны быть тестовые данные
    
    def test_get_brands(self):
        """Тест получения брендов"""
        brands = self.db.get_brands()
        self.assertIsInstance(brands, list)
        self.assertGreater(len(brands), 0)
    
    def test_get_car_by_id(self):
        """Тест получения автомобиля по ID"""
        cars = self.db.get_cars(limit=1)
        if cars:
            car_id = cars[0]['id']
            car = self.db.get_car_by_id(car_id)
            self.assertIsNotNone(car)
            self.assertEqual(car['id'], car_id)
    
    def test_create_order(self):
        """Тест создания заказа"""
        cars = self.db.get_cars(limit=1)
        if cars:
            car_id = cars[0]['id']
            user_id = 12345
            
            result = self.db.create_order(user_id, car_id)
            self.assertTrue(result)
    
    def test_get_cars_with_brand_filter(self):
        """Тест фильтрации по бренду"""
        brands = self.db.get_brands()
        if brands:
            brand = brands[0]
            cars = self.db.get_cars(brand=brand)
            for car in cars:
                self.assertEqual(car['brand'], brand)

class TestCarClass(unittest.TestCase):
    """Тесты для класса Car"""
    
    def test_car_creation(self):
        """Тест создания объекта Car"""
        car = Car(
            id=1,
            brand="TestBrand",
            model="TestModel",
            year=2023,
            price=1000000,
            mileage=0,
            fuel_type="Бензин",
            transmission="Автомат",
            color="Белый",
            description="Тестовый автомобиль",
            photos=["photo1.jpg", "photo2.jpg"]
        )
        
        self.assertEqual(car.brand, "TestBrand")
        self.assertEqual(car.model, "TestModel")
        self.assertEqual(car.year, 2023)
        self.assertEqual(car.price, 1000000)
        self.assertTrue(car.is_available)
    
    def test_car_to_dict(self):
        """Тест преобразования Car в словарь"""
        car = Car(
            id=1,
            brand="TestBrand",
            model="TestModel",
            year=2023,
            price=1000000,
            mileage=0,
            fuel_type="Бензин",
            transmission="Автомат",
            color="Белый",
            description="Тестовый автомобиль",
            photos=["photo1.jpg"]
        )
        
        car_dict = asdict(car)
        self.assertIsInstance(car_dict, dict)
        self.assertEqual(car_dict['brand'], "TestBrand")

def run_tests():
    """Запуск всех тестов"""
    print("🧪 Запуск тестов бота автосалона...")
    print("=" * 50)
    
    # Создаем test suite
    test_suite = unittest.TestSuite()
    
    # Добавляем тесты
    test_suite.addTest(unittest.makeSuite(TestCarDatabase))
    test_suite.addTest(unittest.makeSuite(TestCarClass))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Выводим результаты
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ Все тесты прошли успешно!")
    else:
        print(f"❌ Тесты завершились с ошибками: {len(result.failures)} failures, {len(result.errors)} errors")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    run_tests()
    

