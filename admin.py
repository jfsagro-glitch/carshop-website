import sqlite3
import json
from typing import List, Dict, Optional

class CarAdmin:
    """Класс для управления автомобилями в базе данных"""
    
    def __init__(self, db_path: str = "cars.db"):
        self.db_path = db_path
    
    def add_car(self, brand: str, model: str, year: int, price: int, 
                mileage: int, fuel_type: str, transmission: str, 
                color: str, description: str, photos: List[str] = None) -> bool:
        """Добавление нового автомобиля"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            photos_json = json.dumps(photos or [])
            
            cursor.execute('''
                INSERT INTO cars (brand, model, year, price, mileage, fuel_type, 
                               transmission, color, description, photos)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (brand, model, year, price, mileage, fuel_type, 
                 transmission, color, description, photos_json))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка добавления автомобиля: {e}")
            return False
    
    def update_car(self, car_id: int, **kwargs) -> bool:
        """Обновление информации об автомобиле"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Формируем SQL запрос динамически
            set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
            values = list(kwargs.values()) + [car_id]
            
            cursor.execute(f'''
                UPDATE cars SET {set_clause} WHERE id = ?
            ''', values)
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка обновления автомобиля: {e}")
            return False
    
    def delete_car(self, car_id: int) -> bool:
        """Удаление автомобиля"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM cars WHERE id = ?', (car_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка удаления автомобиля: {e}")
            return False
    
    def get_all_cars(self) -> List[Dict]:
        """Получение всех автомобилей"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM cars ORDER BY id DESC')
        columns = [description[0] for description in cursor.description]
        cars = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return cars
    
    def get_orders(self) -> List[Dict]:
        """Получение всех заказов"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT o.*, c.brand, c.model, c.price 
            FROM orders o 
            JOIN cars c ON o.car_id = c.id 
            ORDER BY o.order_date DESC
        ''')
        columns = [description[0] for description in cursor.description]
        orders = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return orders
    
    def update_order_status(self, order_id: int, status: str) -> bool:
        """Обновление статуса заказа"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE orders SET status = ? WHERE id = ?
            ''', (status, order_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка обновления статуса заказа: {e}")
            return False

def main():
    """Пример использования админ-панели"""
    admin = CarAdmin()
    
    print("=== Админ-панель автосалона ===\n")
    
    # Показать все автомобили
    cars = admin.get_all_cars()
    print(f"Всего автомобилей: {len(cars)}")
    for car in cars:
        print(f"ID: {car['id']}, {car['brand']} {car['model']} - {car['price']:,} ₽")
    
    print("\n" + "="*50 + "\n")
    
    # Показать заказы
    orders = admin.get_orders()
    print(f"Всего заказов: {len(orders)}")
    for order in orders:
        print(f"Заказ #{order['id']}: {order['brand']} {order['model']} - {order['status']}")
    
    print("\n" + "="*50 + "\n")
    
    # Пример добавления нового автомобиля
    print("Добавление нового автомобиля...")
    success = admin.add_car(
        brand="Mercedes-Benz",
        model="E-Class",
        year=2022,
        price=4500000,
        mileage=15000,
        fuel_type="Бензин",
        transmission="Автомат",
        color="Серебристый",
        description="Новый автомобиль, полная комплектация, гарантия",
        photos=["https://example.com/mercedes1.jpg", "https://example.com/mercedes2.jpg"]
    )
    
    if success:
        print("✅ Автомобиль успешно добавлен!")
    else:
        print("❌ Ошибка при добавлении автомобиля")

if __name__ == "__main__":
    main()

