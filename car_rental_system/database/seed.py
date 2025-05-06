import sys
from pathlib import Path
from datetime import datetime, timedelta
from random import choice, randint, uniform
import sqlite3
   


# Добавляем родительскую директорию в PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from database.connection import get_db_connection

def fill_test_data():
    """Заполняет базу данных тестовыми данными"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Категории автомобилей
        categories = [
            ('Эконом', 1500, 5000, 'Компактные городские автомобили'),
            ('Комфорт', 2500, 10000, 'Седаны среднего класса'),
            ('Бизнес', 4000, 15000, 'Премиальные автомобили'),
            ('Внедорожник', 3500, 12000, 'SUV и кроссоверы'),
            ('Минивэн', 3000, 10000, 'Для больших компаний'),
            ('Спорт', 6000, 20000, 'Спортивные автомобили'),
            ('Электромобиль', 4500, 15000, 'Экологичный транспорт')
        ]
        cursor.executemany(
            'INSERT OR IGNORE INTO categories (name, daily_rate, deposit_amount, description) VALUES (?, ?, ?, ?)',
            categories
        )

        # 2. Дополнительные услуги
        services = [
            ('Детское кресло', 300, 'Детское удерживающее устройство'),
            ('Навигатор', 200, 'GPS навигация'),
            ('Полная страховка', 500, 'Страховка без франшизы'),
            ('Дополнительный водитель', 1000, 'Второй водитель в договоре'),
            ('Доставка авто', 1500, 'Доставка автомобиля клиенту'),
            ('Зимние шины', 800, 'Комплект зимней резины'),
            ('Wi-Fi роутер', 400, 'Мобильный интернет в авто')
        ]
        cursor.executemany(
            'INSERT OR IGNORE INTO services (name, price, description) VALUES (?, ?, ?)',
            services
        )

        # 3. Сотрудники
        employees = [
            ('Иван', 'Петров', 'Менеджер', '2020-01-15', '+79161234567', 'manager@rental.ru', 50000),
            ('Ольга', 'Сидорова', 'Администратор', '2021-03-10', '+79169876543', 'admin@rental.ru', 45000),
            ('Алексей', 'Козлов', 'Механик', '2019-05-20', '+79151112233', 'mechanic@rental.ru', 40000)
        ]
        cursor.executemany(
            '''INSERT OR IGNORE INTO employees 
            (first_name, last_name, position, hire_date, phone, email, salary) 
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            employees
        )

        # 4. Автомобили (30+ записей)
        brands_models = [
            ('Toyota', 'Camry'), ('Toyota', 'Corolla'), ('Toyota', 'RAV4'), ('Toyota', 'Prius'),
            ('Kia', 'Rio'), ('Kia', 'Optima'), ('Kia', 'Sportage'), ('Kia', 'Sorento'),
            ('Hyundai', 'Solaris'), ('Hyundai', 'Sonata'), ('Hyundai', 'Tucson'), ('Hyundai', 'Santa Fe'),
            ('BMW', '3 Series'), ('BMW', '5 Series'), ('BMW', 'X3'), ('BMW', 'X5'),
            ('Mercedes', 'C-Class'), ('Mercedes', 'E-Class'), ('Mercedes', 'GLC'), ('Mercedes', 'GLE'),
            ('Audi', 'A4'), ('Audi', 'A6'), ('Audi', 'Q5'), ('Audi', 'Q7'),
            ('Volkswagen', 'Polo'), ('Volkswagen', 'Passat'), ('Volkswagen', 'Tiguan'), ('Volkswagen', 'Teramont'),
            ('Skoda', 'Octavia'), ('Skoda', 'Superb'), ('Skoda', 'Kodiaq')
        ]


        for i, (brand, model) in enumerate(brands_models):
            try:
                cursor.execute(
                    '''INSERT OR IGNORE INTO cars 
                    (brand, model, year, license_plate, category_id, color, mileage, vin, status, purchase_date, last_service_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (
                        brand,
                        model,
                        2018 + i % 6,
                        f"{chr(1040 + i//10)}{i%1000:03d}{chr(1040 + (i//10)%32)}{chr(1040 + (i//5)%32)}777",
                        (i % 7) + 1,
                        choice(['Белый', 'Серый', 'Черный', 'Серебристый', 'Красный', 'Синий']),
                        10000 + i*2000,
                        f"VIN{randint(10000000000000000, 99999999999999999)}",
                        choice(['available', 'available', 'available', 'rented', 'maintenance']),
                        f"202{randint(0,3)}-{randint(1,12):02d}-{randint(1,28):02d}",
                        f"2023-{randint(1,12):02d}-{randint(1,28):02d}" if i % 3 == 0 else None
                    )
                )
            except sqlite3.IntegrityError:
                continue  # Пропускаем дубликаты

        # 5. Клиенты (50+ записей)
        first_names = ['Иван', 'Алексей', 'Дмитрий', 'Сергей', 'Андрей', 'Михаил',
                      'Мария', 'Елена', 'Анна', 'Ольга', 'Наталья', 'Татьяна']
        last_names = ['Иванов', 'Петров', 'Сидоров', 'Смирнов', 'Кузнецов', 'Васильев',
                     'Павлов', 'Семенов', 'Голубев', 'Виноградов', 'Козлов', 'Лебедев']

        for i in range(50):
            try:
                cursor.execute(
                    '''INSERT OR IGNORE INTO clients 
                    (first_name, last_name, birth_date, passport_number, driver_license, phone, email, registration_date, rating, address)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (
                        choice(first_names),
                        choice(last_names),
                        f"19{randint(60,99)}-{randint(1,12):02d}-{randint(1,28):02d}",
                        f"{randint(1000,9999)} {randint(100000,999999)}",
                        f"{randint(10,99)} {randint(100000,999999)}",
                        f"+79{randint(10000000,99999999)}",
                        f"{choice(first_names).lower()}.{choice(last_names).lower()}@example.com",
                        f"202{randint(0,3)}-{randint(1,12):02d}-{randint(1,28):02d}",
                        randint(3, 5),
                        f"г. Москва, ул. {choice(['Ленина', 'Пушкина', 'Гагарина'])}, д. {randint(1,100)}"
                    )
                )
            except sqlite3.IntegrityError:
                continue  # Пропускаем дубликаты

        # 6. Аренды (100+ записей)
        for _ in range(100):
            car_id = randint(1, 30)
            cursor.execute('SELECT category_id, status FROM cars WHERE car_id = ?', (car_id,))
            car_data = cursor.fetchone()
            
            if not car_data or car_data[1] != 'available':
                continue
                
            category_id = car_data[0]
            
            cursor.execute('SELECT daily_rate, deposit_amount FROM categories WHERE category_id = ?', (category_id,))
            rates = cursor.fetchone()
            if not rates:
                continue
                
            daily_rate, deposit = rates


            start_date = datetime.now() - timedelta(days=randint(1, 180))
            end_date = start_date + timedelta(days=randint(1, 14))
            
            # Определяем статус аренды
            if randint(1,5) == 1:  # 20% chance of overdue
                actual_end_date = end_date + timedelta(days=randint(1,7))
                status = 'overdue'
            else:
                actual_end_date = end_date if randint(0,1) else None
                status = choice(['reserved', 'active', 'completed', 'cancelled'])
            
            # Расчет стоимости
            days = (end_date - start_date).days
            total_cost = daily_rate * max(1, days) * uniform(0.9, 1.1)
            
            try:
                cursor.execute(
                    '''INSERT INTO rentals 
                    (client_id, car_id, start_date, end_date, actual_end_date, total_cost, deposit_amount, status, notes, employee_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (
                        randint(1, 50),
                        car_id,
                        start_date.strftime('%Y-%m-%d %H:%M:%S'),
                        end_date.strftime('%Y-%m-%d %H:%M:%S'),
                        actual_end_date.strftime('%Y-%m-%d %H:%M:%S') if actual_end_date else None,
                        round(total_cost, 2),
                        deposit,
                        status,
                        f"Дополнительные пожелания: {choice(['нет', 'нужна детская кресло', 'доставка', 'полная страховка'])}",
                        randint(1, 3)
                    )
                )

                # Обновляем статус автомобиля
                new_status = 'rented' if status in ['active', 'overdue'] else 'reserved' if status == 'reserved' else 'available'
                cursor.execute('UPDATE cars SET status = ? WHERE car_id = ?', (new_status, car_id))
                
                # Добавляем услуги (30% chance)
                if randint(1,10) <= 3:
                    service_id = randint(1,7)
                    cursor.execute(
                        'INSERT OR IGNORE INTO rental_services (rental_id, service_id, quantity) VALUES (?, ?, ?)',
                        (cursor.lastrowid, service_id, randint(1,3))
                    )
            except sqlite3.IntegrityError:
                conn.rollback()
                continue


        # 7. Платежи
        cursor.execute('SELECT rental_id, total_cost, deposit_amount, status FROM rentals')
        for rental_id, total_cost, deposit, status in cursor.fetchall():
            if status in ['active', 'completed', 'overdue']:
                # Основной платеж
                cursor.execute(
                    '''INSERT INTO payments 
                    (rental_id, amount, payment_date, payment_method, transaction_id, status)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                    (
                        rental_id,
                        total_cost + deposit,
                        (datetime.now() - timedelta(days=randint(0,30))).strftime('%Y-%m-%d %H:%M:%S'),
                        choice(['cash', 'card', 'bank_transfer', 'online']),
                        f"TR{randint(1000000000,9999999999)}",
                        'completed'
                    )
                )
                
                # Возврат депозита (50% chance)
                if status in ['completed', 'overdue'] and randint(0,1) and deposit > 0:
                    cursor.execute(
                        '''INSERT INTO payments 
                        (rental_id, amount, payment_date, payment_method, transaction_id, status)
                        VALUES (?, ?, ?, ?, ?, ?)''',
                        (
                            rental_id,
                            -deposit,
                            (datetime.now() + timedelta(days=randint(1,14))).strftime('%Y-%m-%d %H:%M:%S'),
                            'bank_transfer',
                            f"REF{randint(1000000000,9999999999)}",
                            'completed'
                        )
                    )

        # 8. Повреждения (10% от завершенных аренд)
        cursor.execute('SELECT rental_id, car_id FROM rentals WHERE status IN ("completed", "overdue")')
        for rental_id, car_id in cursor.fetchall():
            if randint(1,10) == 1:
                cursor.execute(
                    '''INSERT INTO damages 
                    (rental_id, car_id, description, repair_cost, reported_date, repaired_date, status, employee_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (
                        rental_id,
                        car_id,
                        choice(['Царапина на двери', 'Вмятина на бампере', 'Разбитое зеркало', 
                               'Повреждение салона', 'Потертости на кузове']),
                        round(uniform(1000, 20000), 2),
                        (datetime.now() - timedelta(days=randint(1,30))).strftime('%Y-%m-%d %H:%M:%S'),
                        (datetime.now() + timedelta(days=randint(1,14))).strftime('%Y-%m-%d %H:%M:%S') if randint(0,1) else None,
                        choice(['reported', 'under_repair', 'repaired', 'paid']),
                        randint(1,3)
                    )
                )

        conn.commit()
        print("База данных успешно заполнена данными!")
        print(f"• Категории: {len(categories)}")
        print(f"• Автомобили: {len(brands_models)}") 
        print(f"• Клиенты: 50")
        print(f"• Аренды: 100")
    
    except Exception as e:
        conn.rollback()
        print(f"Ошибка: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    fill_test_data()
