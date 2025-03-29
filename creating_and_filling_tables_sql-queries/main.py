import sqlite3

# Подключение к базе данных и создание таблиц
connection = sqlite3.connect("baza.db")
cursor = connection.cursor()

# Создание таблиц 
cursor.execute("""
    CREATE TABLE IF NOT EXISTS `job_titles` (
        `id_job_title` integer primary key NOT NULL UNIQUE,
        `name` TEXT NOT NULL
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS `employees` (
        `id` integer primary key NOT NULL UNIQUE,
        `surname` TEXT NOT NULL,
        `name` TEXT NOT NULL,
        `id_job_title` INTEGER NOT NULL,
        FOREIGN KEY(`id_job_title`) REFERENCES `job_titles`(`id_job_title`)
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS `Clients` (
        `client_code` integer primary key NOT NULL UNIQUE,
        `organization` TEXT NOT NULL,
        `telephone` INTEGER NOT NULL
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS `Orders` (
        `order_code` integer primary key NOT NULL UNIQUE,
        `client_code` INTEGER NOT NULL,
        `employee_code` INTEGER NOT NULL,
        `sum` INTEGER NOT NULL,
        `date_of_completion` TEXT NOT NULL,
        `completion_mark` INTEGER NOT NULL,
        FOREIGN KEY(`client_code`) REFERENCES `Clients`(`client_code`),
        FOREIGN KEY(`employee_code`) REFERENCES `employees`(`id`)
    );
""")

# Вставка данных 
job_titles_data = [
    (1, "Менеджер"),
    (2, "Разработчик"),
    (3, "Аналитик"),
    (4, "Дизайнер")
]
cursor.executemany("INSERT OR IGNORE INTO `job_titles` (`id_job_title`, `name`) VALUES (?, ?)", job_titles_data)

employees_data = [
    (1, "Иванов", "Иван", 2),
    (2, "Петров", "Петр", 1),
    (3, "Сидорова", "Мария", 3),
    (4, "Козлов", "Алексей", 2),
]
cursor.executemany("INSERT OR IGNORE INTO `employees` (`id`, `surname`, `name`, `id_job_title`) VALUES (?, ?, ?, ?)", employees_data)

clients_data = [
    (1, "ООО Ромашка", 1234567890),
    (2, "ИП Иванов", 9876543210),
    (3, "ЗАО Тюльпан", 5555555555),
]
cursor.executemany("INSERT OR IGNORE INTO `Clients` (`client_code`, `organization`, `telephone`) VALUES (?, ?, ?)", clients_data)

orders_data = [
    (1, 1, 1, 10000, "2023-10-01", 1),
    (2, 2, 2, 15000, "2023-10-05", 0),
    (3, 3, 3, 20000, "2023-10-10", 1),
    (4, 1, 2, 12000, "2023-11-15", 1),
    (5, 3, 1, 18000, "2023-11-20", 0),
]
cursor.executemany("INSERT OR IGNORE INTO `Orders` (`order_code`, `client_code`, `employee_code`, `sum`, `date_of_completion`, `completion_mark`) VALUES (?, ?, ?, ?, ?, ?)", orders_data)

connection.commit()

# 1. Пять простых запросов (COUNT, MAX, SUM, AVG)
print("\n1. Пять простых запросов:")

# 1.1. Количество клиентов
cursor.execute("SELECT COUNT(*) FROM Clients")
print(f"1.1. Общее количество клиентов: {cursor.fetchone()[0]}")

# 1.2. Максимальная сумма заказа
cursor.execute("SELECT MAX(sum) FROM Orders")
print(f"1.2. Максимальная сумма заказа: {cursor.fetchone()[0]} руб.")

# 1.3. Средняя сумма заказа
cursor.execute("SELECT AVG(sum) FROM Orders")
print(f"1.3. Средняя сумма заказа: {round(cursor.fetchone()[0], 2)} руб.")

# 1.4. Количество выполненных заказов (completion_mark = 1)
cursor.execute("SELECT COUNT(*) FROM Orders WHERE completion_mark = 1")
print(f"1.4. Количество выполненных заказов: {cursor.fetchone()[0]}")

# 1.5. Сумма всех заказов
cursor.execute("SELECT SUM(sum) FROM Orders")
print(f"1.5. Общая сумма всех заказов: {cursor.fetchone()[0]} руб.")

# 2. Три запроса с агрегацией и GROUP BY
print("\n2. Три запроса с агрегацией:")

# 2.1. Количество заказов по каждому клиенту
cursor.execute("""
    SELECT c.organization, COUNT(o.order_code) as order_count
    FROM Orders o
    JOIN Clients c ON o.client_code = c.client_code
    GROUP BY c.organization
""")
print("2.1. Количество заказов по клиентам:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} заказов")

# 2.2. Средняя сумма заказа по должностям сотрудников
cursor.execute("""
    SELECT j.name, AVG(o.sum) as avg_order_sum
    FROM Orders o
    JOIN employees e ON o.employee_code = e.id
    JOIN job_titles j ON e.id_job_title = j.id_job_title
    GROUP BY j.name
""")
print("\n2.2. Средняя сумма заказа по должностям:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {round(row[1], 2)} руб.")

# 2.3. Общая сумма заказов по месяцам
cursor.execute("""
    SELECT strftime('%Y-%m', date_of_completion) as month, SUM(sum) as total_sum
    FROM Orders
    GROUP BY strftime('%Y-%m', date_of_completion)
""")
print("\n2.3. Общая сумма заказов по месяцам:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} руб.")

# 3. Три запроса с объединением таблиц и условиями
print("\n3. Три запроса с объединением и условиями:")

# 3.1. Заказы с информацией о клиентах и сотрудниках (сумма > 15000)
cursor.execute("""
    SELECT o.order_code, c.organization, e.surname || ' ' || e.name as employee, o.sum
    FROM Orders o
    JOIN Clients c ON o.client_code = c.client_code
    JOIN employees e ON o.employee_code = e.id
    WHERE o.sum > 15000
    ORDER BY o.sum DESC
""")
print("3.1. Заказы с суммой больше 15000 руб.:")
for row in cursor.fetchall():
    print(f"  Заказ {row[0]}: Клиент - {row[1]}, Сотрудник - {row[2]}, Сумма - {row[3]} руб.")

# 3.2. Невыполненные заказы (completion_mark = 0) с информацией о клиентах
cursor.execute("""
    SELECT o.order_code, c.organization, o.date_of_completion, o.sum
    FROM Orders o
    JOIN Clients c ON o.client_code = c.client_code
    WHERE o.completion_mark = 0
""")
print("\n3.2. Невыполненные заказы:")
for row in cursor.fetchall():
    print(f"  Заказ {row[0]}: Клиент - {row[1]}, Дата - {row[2]}, Сумма - {row[3]} руб.")

# 3.3. Заказы, выполненные разработчиками (id_job_title = 2)
cursor.execute("""
    SELECT o.order_code, c.organization, e.surname || ' ' || e.name as developer, o.sum
    FROM Orders o
    JOIN employees e ON o.employee_code = e.id
    JOIN Clients c ON o.client_code = c.client_code
    WHERE e.id_job_title = 2
""")
print("\n3.3. Заказы, выполненные разработчиками:")
for row in cursor.fetchall():
    print(f"  Заказ {row[0]}: Клиент - {row[1]}, Разработчик - {row[2]}, Сумма - {row[3]} руб.")

# Закрытие соединения
connection.close()