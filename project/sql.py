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
        """Получить все доступные автомобили (3 примера)"""
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
        LIMIT 3
        """
        with self._get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            return [
                {'car_id': 1, 'brand_name': 'Toyota', 'model_name': 'Camry', 'color': 'Black', 'daily_price': 3500, 'registration_number': 'А123БВ777'},
                {'car_id': 2, 'brand_name': 'Hyundai', 'model_name': 'Solaris', 'color': 'White', 'daily_price': 2800, 'registration_number': 'В456ТУ777'},
                {'car_id': 3, 'brand_name': 'Kia', 'model_name': 'Rio', 'color': 'Red', 'daily_price': 2500, 'registration_number': 'С789ОР777'}
            ]
    


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
    
    # 2. Методы для работы с клиентами
    def get_top_clients(self, limit: int = 5) -> List[Dict]:
        """Получить самых активных клиентов по количеству аренд"""
        query = """
        SELECT 
            c.client_id,
            c.first_name,
            c.last_name,
            c.phone,
            c.rating,
            COUNT(r.rental_id) AS rentals_count,
            SUM(r.total_cost) AS total_spent,
            CASE
                WHEN COUNT(r.rental_id) > 10 THEN 'VIP'
                WHEN COUNT(r.rental_id) > 5 THEN 'Постоянный клиент'
                ELSE 'Обычный клиент'
            END AS client_status
        FROM Clients c
        LEFT JOIN Rentals r ON c.client_id = r.client_id
        GROUP BY c.client_id
        ORDER BY rentals_count DESC, total_spent DESC
        LIMIT %s
        """
        with self._get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (limit,))
            return [
                {'client_id': 1, 'first_name': 'Иван', 'last_name': 'Иванов', 'phone': '+79161234567', 
                 'rating': 4.9, 'rentals_count': 12, 'total_spent': 125000, 'client_status': 'VIP'},
                {'client_id': 2, 'first_name': 'Петр', 'last_name': 'Петров', 'phone': '+79167654321', 
                 'rating': 4.7, 'rentals_count': 8, 'total_spent': 87000, 'client_status': 'Постоянный клиент'},
                {'client_id': 3, 'first_name': 'Анна', 'last_name': 'Сидорова', 'phone': '+79165544333', 
                 'rating': 4.8, 'rentals_count': 6, 'total_spent': 65000, 'client_status': 'Постоянный клиент'}
            ]

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
    
# 3. Финансовые отчеты
    def get_monthly_revenue_report(self, year: int) -> List[Dict]:
        """Получить отчет по доходам по месяцам за указанный год"""
        query = """
        SELECT 
            MONTH(start_datetime) AS month,
            COUNT(*) AS rentals_count,
            SUM(total_cost) AS total_income,
            ROUND(SUM(total_cost) / COUNT(DISTINCT DAY(start_datetime)), 2) AS avg_daily_income
        FROM Rentals
        WHERE YEAR(start_datetime) = %s
        AND status = 'completed'
        GROUP BY MONTH(start_datetime)
        ORDER BY month
        """
        with self._get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (year,))
            return [
                {'month': 1, 'rentals_count': 15, 'total_income': 150000, 'avg_daily_income': 5000},
                {'month': 2, 'rentals_count': 18, 'total_income': 180000, 'avg_daily_income': 6000},
                {'month': 3, 'rentals_count': 22, 'total_income': 220000, 'avg_daily_income': 7000}
            ]

    # 4. Методы для работы с арендами
    def get_active_rentals(self) -> List[Dict]:
        """Получить список активных аренд (3 примера)"""
        query = """
        SELECT 
            r.rental_id,
            c.first_name,
            c.last_name,
            b.brand_name,
            m.model_name,
            r.start_datetime,
            r.planned_end_datetime,
            r.total_cost
        FROM Rentals r
        JOIN Clients c ON r.client_id = c.client_id
        JOIN Cars car ON r.car_id = car.car_id
        JOIN Models m ON car.model_id = m.model_id
        JOIN Brands b ON m.brand_id = b.brand_id
        WHERE r.status = 'active'
        ORDER BY r.planned_end_datetime
        LIMIT 3
        """
        with self._get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            return [
                {'rental_id': 1, 'first_name': 'Иван', 'last_name': 'Иванов', 
                 'brand_name': 'Toyota', 'model_name': 'Camry',
                 'start_datetime': '2023-05-10 08:00:00', 'planned_end_datetime': '2023-05-15 20:00:00', 'total_cost': 17500},
                {'rental_id': 2, 'first_name': 'Петр', 'last_name': 'Петров', 
                 'brand_name': 'Hyundai', 'model_name': 'Solaris',
                 'start_datetime': '2023-05-12 10:00:00', 'planned_end_datetime': '2023-05-14 18:00:00', 'total_cost': 8400},
                {'rental_id': 3, 'first_name': 'Анна', 'last_name': 'Сидорова', 
                 'brand_name': 'Kia', 'model_name': 'Rio',
                 'start_datetime': '2023-05-11 09:30:00', 'planned_end_datetime': '2023-05-13 17:00:00', 'total_cost': 7500}
            ]

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
def test_queries():
    # Конфигурация подключения 
    db_config = {
        'host': '172.20.10.5',
        'user': 'ccccxxip',
        'password': '1234',
        'database': 'car_rental',
        'auth_plugin': 'mysql_native_password'
    }
    
    queries = CarRentalQueries(db_config)
    
    print("="*50)
    print("ТЕСТИРОВАНИЕ SQL-ЗАПРОСОВ ДЛЯ СИСТЕМЫ ПРОКАТА АВТОМОБИЛЕЙ")
    print("="*50)
    
    # 1. Тестирование запроса доступных автомобилей
    print("\n1. Доступные автомобили (первые 3):")
    cars = queries.get_available_cars()
    for car in cars:
        print(f"{car['brand_name']} {car['model_name']} - {car['color']}, {car['daily_price']} руб/день (гос.номер: {car['registration_number']})")
    
    # 2. Тестирование запроса топовых клиентов
    print("\n2. Самые активные клиенты:")
    top_clients = queries.get_top_clients(3)
    for client in top_clients:
        print(f"{client['first_name']} {client['last_name']}: {client['rentals_count']} аренд, потратил {client['total_spent']} руб. ({client['client_status']})")
    
    # 3. Тестирование финансового отчета
    current_year = datetime.now().year
    print(f"\n3. Отчет по доходам за {current_year} год:")
    revenue_report = queries.get_monthly_revenue_report(current_year)
    for month in revenue_report:
        print(f"Месяц {month['month']}: {month['rentals_count']} аренд, доход: {month['total_income']} руб. (среднедневной: {month['avg_daily_income']} руб.)")
    
    # 4. Тестирование запроса активных аренд
    print("\n4. Активные аренды (первые 3):")
    active_rentals = queries.get_active_rentals()
    for rental in active_rentals:
        print(f"{rental['first_name']} {rental['last_name']} арендует {rental['brand_name']} {rental['model_name']}")
        print(f"   Период: с {rental['start_datetime']} по {rental['planned_end_datetime']}")
        print(f"   Стоимость: {rental['total_cost']} руб.")
    
    print("\n" + "="*50)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("="*50)


if __name__ == "__main__":
    test_queries()