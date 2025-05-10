# SQL-запросы
import mysql.connector
from typing import List, Dict, Union, Optional
from datetime import datetime, timedelta

class CarRentalQueries:
    def __init__(self, connection_params: Dict):
        self.connection_params = connection_params
    
    def _get_connection(self):
        """Устанавливает соединение с базой данных"""
        return mysql.connector.connect(**self.connection_params)
    # 1. Основные методы для работы с автомобилями
    def get_available_cars(self) -> List[Dict]:
        """Получить все доступные автомобили"""
        query = """
        SELECT 
            c.car_id, 
            b.brand_name, 
            m.model_name, 
            c.color, 
            c.daily_price,
            c.registration_number
        FROM Cars c
        JOIN Models m ON c.model_id = m.model_id
        JOIN Brands b ON m.brand_id = b.brand_id
        WHERE c.is_available = TRUE
        ORDER BY c.daily_price
        """
        with self._get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            return cursor.fetchall()
    
    def get_car_details(self, car_id: int) -> Optional[Dict]:
        """Получить подробную информацию об автомобиле"""
        query = """
        SELECT 
            c.*,
            b.brand_name,
            m.model_name,
            f.fuel_name,
            p.address AS parking_address
        FROM Cars c
        JOIN Models m ON c.model_id = m.model_id
        JOIN Brands b ON m.brand_id = b.brand_id
        JOIN FuelTypes f ON c.fuel_id = f.fuel_id
        LEFT JOIN Parkings p ON c.parking_id = p.parking_id
        WHERE c.car_id = %s
        """
        with self._get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (car_id,))
            return cursor.fetchone()
    
    # 2. Методы для работы с клиентами
    def get_client_info(self, client_id: int) -> Optional[Dict]:
        """Получить информацию о клиенте"""
        query = "SELECT * FROM Clients WHERE client_id = %s"
        with self._get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (client_id,))
            return cursor.fetchone()
    
    # 3. Методы для работы с арендами
    def get_active_rentals(self) -> List[Dict]:
        """Получить список активных аренд"""
        query = """
        SELECT 
            r.rental_id,
            c.first_name,
            c.last_name,
            b.brand_name,
            m.model_name,
            r.start_datetime,
            r.planned_end_datetime
        FROM Rentals r
        JOIN Clients c ON r.client_id = c.client_id
        JOIN Cars car ON r.car_id = car.car_id
        JOIN Models m ON car.model_id = m.model_id
        JOIN Brands b ON m.brand_id = b.brand_id
        WHERE r.status = 'active'
        ORDER BY r.planned_end_datetime
        """
        with self._get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            return cursor.fetchall()
    
    # 4. Примеры аналитических запросов
    def get_monthly_stats(self, year: int) -> List[Dict]:
        """Статистика по месяцам за указанный год"""
        query = """
        SELECT 
            MONTH(start_datetime) AS month,
            COUNT(*) AS rentals_count,
            SUM(total_cost) AS total_income
        FROM Rentals
        WHERE YEAR(start_datetime) = %s
        GROUP BY MONTH(start_datetime)
        ORDER BY month
        """
        with self._get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (year,))
            return cursor.fetchall()
    
    # Простые CRUD-запросы
    # Добавление нового клиента
    def add_client(first_name, last_name, phone, driver_license):
        query = """
        INSERT INTO Clients (first_name, last_name, phone, driver_license, rating)
        VALUES (%s, %s, %s, %s, 5.0)
        """
        params = (first_name, last_name, phone, driver_license)
        

    # Обновление информации об автомобиле
    def update_car_price(car_id, new_price):
        query = "UPDATE Cars SET daily_price = %s WHERE car_id = %s"
        params = (new_price, car_id)
        

    # Удаление автомобиля
    def delete_car(car_id):
        query = "DELETE FROM Cars WHERE car_id = %s"
        params = (car_id,)



    # 2. Вычисляемые запросы с агрегацией
    # Средняя стоимость аренды по классам автомобилей
    def avg_price_by_class():
        query = """
        SELECT 
            m.car_class,
            AVG(c.daily_price) AS avg_price,
            COUNT(*) AS cars_count
        FROM Cars c
        JOIN Models m ON c.model_id = m.model_id
        GROUP BY m.car_class
        ORDER BY avg_price DESC
        """
        # выполнение запроса...

    # Статистика по клиентам
    def client_stats():
        query = """
        SELECT 
            COUNT(*) AS total_clients,
            AVG(rating) AS avg_rating,
            MAX(rating) AS max_rating,
            MIN(rating) AS min_rating
        FROM Clients
        """
        # выполнение запроса...





    # 3. Параметризованные запросы
    # Поиск автомобилей по параметрам
    def search_cars(brand=None, min_price=None, max_price=None, color=None):
        query = """
        SELECT 
            c.car_id, b.brand_name, m.model_name, c.color, c.daily_price
        FROM Cars c
        JOIN Models m ON c.model_id = m.model_id
        JOIN Brands b ON m.brand_id = b.brand_id
        WHERE c.is_available = TRUE
        """
        params = []
        
        if brand:
            query += " AND b.brand_name = %s"
            params.append(brand)
        if min_price:
            query += " AND c.daily_price >= %s"
            params.append(min_price)
        if max_price:
            query += " AND c.daily_price <= %s"
            params.append(max_price)
        if color:
            query += " AND c.color = %s"
            params.append(color)
        
        query += " ORDER BY c.daily_price"
        # выполнение запроса с params...

    # Аренды за период
    def rentals_in_period(start_date, end_date):
        query = """
        SELECT 
            r.rental_id, c.first_name, c.last_name,
            b.brand_name, m.model_name, r.total_cost
        FROM Rentals r
        JOIN Clients c ON r.client_id = c.client_id
        JOIN Cars car ON r.car_id = car.car_id
        JOIN Models m ON car.model_id = m.model_id
        JOIN Brands b ON m.brand_id = b.brand_id
        WHERE r.start_datetime BETWEEN %s AND %s
        ORDER BY r.start_datetime
        """
        params = (start_date, end_date)
        # выполнение запроса...



    # 4. Сложные аналитические запросы
    # Отчет о загрузке автопарка
    def fleet_utilization_report():
        query = """
        SELECT 
            c.car_id,
            b.brand_name,
            m.model_name,
            COUNT(r.rental_id) AS rental_count,
            SUM(DATEDIFF(IFNULL(r.actual_end_datetime, CURDATE()), r.start_datetime)) AS total_rental_days,
            ROUND(SUM(DATEDIFF(IFNULL(r.actual_end_datetime, CURDATE()), r.start_datetime)) / 
                DATEDIFF(MAX(r.actual_end_datetime), MIN(r.start_datetime)) * 100, 2) AS utilization_percentage
        FROM Cars c
        LEFT JOIN Rentals r ON c.car_id = r.car_id
        JOIN Models m ON c.model_id = m.model_id
        JOIN Brands b ON m.brand_id = b.brand_id
        GROUP BY c.car_id, b.brand_name, m.model_name
        ORDER BY utilization_percentage DESC
        """
        # выполнение запроса...

    # Прогноз доходов на следующий месяц
    def next_month_revenue_forecast():
        query = """
        SELECT 
            b.brand_name,
            m.model_name,
            c.daily_price,
            COUNT(r.rental_id) AS historical_rentals,
            c.daily_price * COUNT(r.rental_id) * 0.8 AS forecast_revenue  # 0.8 - коэффициент сезонности
        FROM Cars c
        JOIN Models m ON c.model_id = m.model_id
        JOIN Brands b ON m.brand_id = b.brand_id
        LEFT JOIN Rentals r ON c.car_id = r.car_id 
            AND MONTH(r.start_datetime) = MONTH(DATE_ADD(CURDATE(), INTERVAL 1 MONTH))
            AND YEAR(r.start_datetime) = YEAR(CURDATE())
        GROUP BY b.brand_name, m.model_name, c.daily_price
        ORDER BY forecast_revenue DESC
        """
        # выполнение запроса...


    # 5. Операционные запросы
    # Автомобили, требующие техобслуживания
    def cars_due_for_maintenance(mileage_threshold=50000):
        query = """
        SELECT 
            c.car_id,
            b.brand_name,
            m.model_name,
            c.mileage,
            c.registration_number,
            DATEDIFF(CURDATE(), MAX(r.actual_end_datetime)) AS days_since_last_rental
        FROM Cars c
        JOIN Models m ON c.model_id = m.model_id
        JOIN Brands b ON m.brand_id = b.brand_id
        LEFT JOIN Rentals r ON c.car_id = r.car_id AND r.status = 'completed'
        WHERE c.mileage >= %s
        GROUP BY c.car_id, b.brand_name, m.model_name, c.mileage, c.registration_number
        ORDER BY c.mileage DESC
        """
        params = (mileage_threshold,)
        # выполнение запроса...

    # Клиенты с истекающими арендами
    def expiring_rentals(days_threshold=1):
        query = """
        SELECT 
            r.rental_id,
            c.first_name,
            c.last_name,
            c.phone,
            b.brand_name,
            m.model_name,
            DATEDIFF(r.planned_end_datetime, CURDATE()) AS days_remaining
        FROM Rentals r
        JOIN Clients c ON r.client_id = c.client_id
        JOIN Cars car ON r.car_id = car.car_id
        JOIN Models m ON car.model_id = m.model_id
        JOIN Brands b ON m.brand_id = b.brand_id
        WHERE r.status = 'active'
        AND DATEDIFF(r.planned_end_datetime, CURDATE()) <= %s
        ORDER BY days_remaining
        """
        params = (days_threshold,)
        # выполнение запроса...



    # 6. Отчеты для руководства
    # Финансовый отчет по месяцам
    def financial_report_by_month(year):
        query = """
        SELECT 
            MONTH(r.start_datetime) AS month,
            COUNT(r.rental_id) AS rentals_count,
            SUM(r.total_cost) AS total_revenue,
            SUM(r.total_cost) - SUM(c.daily_price * DATEDIFF(r.actual_end_datetime, r.start_datetime) * 0.3 AS profit,  # 30% операционных расходов
            GROUP_CONCAT(DISTINCT b.brand_name) AS brands
        FROM Rentals r
        JOIN Cars c ON r.car_id = c.car_id
        JOIN Models m ON c.model_id = m.model_id
        JOIN Brands b ON m.brand_id = b.brand_id
        WHERE YEAR(r.start_datetime) = %s
        AND r.status = 'completed'
        GROUP BY MONTH(r.start_datetime)
        ORDER BY month
        """
        params = (year,)
        # выполнение запроса...

    # Анализ клиентской базы
    def client_analysis():
        query = """
        SELECT 
            CASE 
                WHEN TIMESTAMPDIFF(YEAR, birth_date, CURDATE()) BETWEEN 18 AND 25 THEN '18-25'
                WHEN TIMESTAMPDIFF(YEAR, birth_date, CURDATE()) BETWEEN 26 AND 35 THEN '26-35'
                WHEN TIMESTAMPDIFF(YEAR, birth_date, CURDATE()) BETWEEN 36 AND 50 THEN '36-50'
                ELSE '50+'
            END AS age_group,
            COUNT(*) AS clients_count,
            AVG(rating) AS avg_rating,
            COUNT(DISTINCT r.rental_id) AS rentals_count,
            SUM(r.total_cost) AS total_spent
        FROM Clients c
        LEFT JOIN Rentals r ON c.client_id = r.client_id
        GROUP BY age_group
        ORDER BY age_group
        """
    #


    # 7. Оптимизационные запросы
    # Определение оптимального количества автомобилей каждой модели
    def optimal_fleet_composition():
        query = """
        WITH demand AS (
            SELECT 
                m.model_id,
                m.model_name,
                b.brand_name,
                COUNT(r.rental_id) AS rental_count,
                SUM(DATEDIFF(r.actual_end_datetime, r.start_datetime)) AS total_days
            FROM Models m
            JOIN Brands b ON m.brand_id = b.brand_id
            LEFT JOIN Cars c ON m.model_id = c.model_id
            LEFT JOIN Rentals r ON c.car_id = r.car_id AND r.start_datetime >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY m.model_id, m.model_name, b.brand_name
        )
        SELECT 
            model_id,
            brand_name,
            model_name,
            rental_count,
            total_days,
            CEIL(total_days / 180) AS recommended_count  # 180 дней в 6 месяцах
        FROM demand
        ORDER BY rental_count DESC
        """
        # выполнение запроса...

    # Выявление невостребованных автомобилей
    def underutilized_cars(threshold_days=30):
        query = """
        SELECT 
            c.car_id,
            b.brand_name,
            m.model_name,
            c.daily_price,
            DATEDIFF(CURDATE(), MAX(IFNULL(r.actual_end_datetime, c.purchase_date))) AS days_idle
        FROM Cars c
        JOIN Models m ON c.model_id = m.model_id
        JOIN Brands b ON m.brand_id = b.brand_id
        LEFT JOIN Rentals r ON c.car_id = r.car_id
        WHERE c.is_available = TRUE
        GROUP BY c.car_id, b.brand_name, m.model_name, c.daily_price
        HAVING days_idle > %s
        ORDER BY days_idle DESC
        """
        params = (threshold_days,)
        # выполнение запроса...



    # 8. Запросы для интеграции с другими системами
    # Экспорт данных для бухгалтерии
    def accounting_export(year, month):
        query = """
        SELECT 
            r.rental_id,
            r.start_datetime,
            r.actual_end_datetime,
            r.total_cost,
            c.first_name,
            c.last_name,
            c.phone,
            car.registration_number,
            b.brand_name,
            m.model_name
        FROM Rentals r
        JOIN Clients c ON r.client_id = c.client_id
        JOIN Cars car ON r.car_id = car.car_id
        JOIN Models m ON car.model_id = m.model_id
        JOIN Brands b ON m.brand_id = b.brand_id
        WHERE YEAR(r.start_datetime) = %s
        AND MONTH(r.start_datetime) = %s
        AND r.status = 'completed'
        ORDER BY r.start_datetime
        """
        params = (year, month)
        # выполнение запроса...

    # Данные для CRM-системы
    def crm_export():
        query = """
        SELECT 
            c.client_id,
            c.first_name,
            c.last_name,
            c.phone,
            c.email,
            c.rating,
            COUNT(r.rental_id) AS rentals_count,
            SUM(r.total_cost) AS total_spent,
            MAX(r.start_datetime) AS last_rental_date
        FROM Clients c
        LEFT JOIN Rentals r ON c.client_id = r.client_id
        GROUP BY c.client_id, c.first_name, c.last_name, c.phone, c.email, c.rating
        ORDER BY total_spent DESC
        """
        # выполнение запроса...

def test_all_methods():
    # Конфигурация подключения к БД
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '1201Lena_',
        'database': 'car_rental',
        'auth_plugin': 'mysql_native_password'
    }
    
    # Создаем экземпляр класса
    rental_db = CarRentalQueries(db_config)
    
    try:
        print("="*50)
        print("ТЕСТИРОВАНИЕ МЕТОДОВ CarRentalQueries")
        print("="*50)
        
        # 1. Тестирование методов для работы с автомобилями
        print("\n1. Тестирование методов для автомобилей:")
        
        # 1.1. Доступные автомобили
        print("\n1.1. get_available_cars():")
        available_cars = rental_db.get_available_cars()
        print(f"Найдено {len(available_cars)} доступных автомобилей:")
        for i, car in enumerate(available_cars[:3], 1):  # Выводим первые 3 для примера
            print(f"{i}. {car['brand_name']} {car['model_name']} - {car['color']}, {car['daily_price']} руб/день")
        
        # 1.2. Информация об автомобиле (возьмем первый из доступных)
        if available_cars:
            car_id = available_cars[0]['car_id']
            print(f"\n1.2. get_car_details(car_id={car_id}):")
            car_details = rental_db.get_car_details(car_id)
            if car_details:
                print(f"Детали автомобиля ID {car_id}:")
                print(f"Марка: {car_details['brand_name']}")
                print(f"Модель: {car_details['model_name']}")
                print(f"Цвет: {car_details['color']}")
                print(f"Пробег: {car_details['mileage']} км")
                print(f"Цена: {car_details['daily_price']} руб/день")
            else:
                print(f"Автомобиль с ID {car_id} не найден")
        
        # 2. Тестирование методов для работы с клиентами
        print("\n2. Тестирование методов для клиентов:")
        
        # 2.1. Получаем клиента (предполагаем, что в БД есть хотя бы один клиент)
        print("\n2.1. get_client_info():")
        # Сначала найдем существующего клиента
        with rental_db._get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT client_id FROM Clients LIMIT 1")
            client = cursor.fetchone()
        
        if client:
            client_id = client['client_id']
            client_info = rental_db.get_client_info(client_id)
            print(f"Информация о клиенте ID {client_id}:")
            print(f"Имя: {client_info['first_name']} {client_info['last_name']}")
            print(f"Телефон: {client_info['phone']}")
            print(f"Рейтинг: {client_info['rating']}")
        else:
            print("В базе нет клиентов для тестирования")
        
        # 3. Тестирование методов для работы с арендами
        print("\n3. Тестирование методов для аренд:")
        
        # 3.1. Активные аренды
        print("\n3.1. get_active_rentals():")
        active_rentals = rental_db.get_active_rentals()
        print(f"Найдено {len(active_rentals)} активных аренд:")
        for i, rental in enumerate(active_rentals[:3], 1):  # Выводим первые 3 для примера
            print(f"{i}. {rental['first_name']} {rental['last_name']} арендует {rental['brand_name']} {rental['model_name']}")
            print(f"   с {rental['start_datetime']} по {rental['planned_end_datetime']}")
        
        # 4. Тестирование аналитических методов
        print("\n4. Тестирование аналитических методов:")
        
        # 4.1. Статистика по месяцам
        current_year = datetime.now().year
        print(f"\n4.1. get_monthly_stats(year={current_year}):")
        monthly_stats = rental_db.get_monthly_stats(current_year)
        if monthly_stats:
            print(f"Статистика за {current_year} год:")
            for stat in monthly_stats:
                print(f"Месяц {stat['month']}: {stat['rentals_count']} аренд, доход: {stat['total_income']} руб.")
        else:
            print(f"Нет данных за {current_year} год")
        
        # 4.2. Проверим статистику за прошлый год (должна быть пустая, если нет данных)
        last_year = current_year - 1
        print(f"\n4.2. get_monthly_stats(year={last_year}):")
        last_year_stats = rental_db.get_monthly_stats(last_year)
        if last_year_stats:
            print(f"Статистика за {last_year} год:")
            for stat in last_year_stats:
                print(f"Месяц {stat['month']}: {stat['rentals_count']} аренд, доход: {stat['total_income']} руб.")
        else:
            print(f"Нет данных за {last_year} год (ожидаемо, если аренд не было)")
        
        print("\n" + "="*50)
        print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
        print("="*50)
    
    except mysql.connector.Error as err:
        print(f"\nОШИБКА MySQL: {err}")
    except Exception as e:
        print(f"\nОБЩАЯ ОШИБКА: {e}")
    finally:
        print("\nПроверка завершена. ")

if __name__ == "__main__":
    test_all_methods()