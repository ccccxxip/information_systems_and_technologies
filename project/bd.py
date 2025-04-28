import sqlite3
from datetime import datetime

def create_database():
    conn = sqlite3.connect('autoservice.db')
    cursor = conn.cursor()
    
    # Создание таблиц
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Clients (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Phone TEXT,
        Email TEXT,
        Address TEXT,
        RegistrationDate TEXT DEFAULT CURRENT_DATE,
        Notes TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Cars (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        ClientID INTEGER NOT NULL,
        Brand TEXT NOT NULL,
        Model TEXT NOT NULL,
        Year INTEGER,
        VIN TEXT UNIQUE,
        LicensePlate TEXT UNIQUE,
        Mileage INTEGER,
        LastServiceDate TEXT,
        NextServiceDate TEXT,
        FOREIGN KEY (ClientID) REFERENCES Clients(ID) ON DELETE CASCADE
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Positions (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Title TEXT NOT NULL UNIQUE,
        Description TEXT,
        SalaryBase REAL NOT NULL,
        BonusPercent REAL DEFAULT 0
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Employees (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        PositionID INTEGER NOT NULL,
        Phone TEXT NOT NULL,
        Email TEXT,
        HireDate TEXT NOT NULL DEFAULT CURRENT_DATE,
        Salary REAL NOT NULL,
        Status TEXT DEFAULT 'Active',
        PassportData TEXT,
        FOREIGN KEY (PositionID) REFERENCES Positions(ID)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Suppliers (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        ContactPerson TEXT,
        Phone TEXT NOT NULL,
        Email TEXT,
        Address TEXT,
        Rating INTEGER DEFAULT 5,
        DeliveryTime INTEGER DEFAULT 3  -- дни
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Parts (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Description TEXT,
        Price REAL NOT NULL,
        Quantity INTEGER NOT NULL DEFAULT 0,
        MinQuantity INTEGER DEFAULT 5,
        SupplierID INTEGER,
        PartNumber TEXT UNIQUE,
        Location TEXT,  -- место хранения на складе
        FOREIGN KEY (SupplierID) REFERENCES Suppliers(ID)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Services (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL UNIQUE,
        Description TEXT,
        Price REAL NOT NULL,
        Duration INTEGER NOT NULL,  -- в минутах
        Category TEXT,
        WarrantyPeriod INTEGER DEFAULT 30  -- дни гарантии
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Orders (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        CarID INTEGER NOT NULL,
        EmployeeID INTEGER NOT NULL,
        DateIn TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        DateOut TEXT,
        Status TEXT NOT NULL DEFAULT 'New',  -- New, In Progress, Completed, Cancelled
        TotalCost REAL DEFAULT 0,
        ProblemDescription TEXT,
        Recommendations TEXT,
        PaymentMethod TEXT,  -- Cash, Card, Transfer
        PaymentStatus TEXT DEFAULT 'Unpaid',  -- Unpaid, PartiallyPaid, Paid
        FOREIGN KEY (CarID) REFERENCES Cars(ID),
        FOREIGN KEY (EmployeeID) REFERENCES Employees(ID)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS OrderServices (
        OrderID INTEGER NOT NULL,
        ServiceID INTEGER NOT NULL,
        EmployeeID INTEGER NOT NULL,
        HoursSpent REAL NOT NULL DEFAULT 1,
        Notes TEXT,
        WarrantyUntil TEXT,
        PRIMARY KEY (OrderID, ServiceID),
        FOREIGN KEY (OrderID) REFERENCES Orders(ID) ON DELETE CASCADE,
        FOREIGN KEY (ServiceID) REFERENCES Services(ID),
        FOREIGN KEY (EmployeeID) REFERENCES Employees(ID)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS OrderParts (
        OrderID INTEGER NOT NULL,
        PartID INTEGER NOT NULL,
        Quantity INTEGER NOT NULL DEFAULT 1,
        Price REAL NOT NULL,  -- цена на момент продажи (может отличаться от текущей)
        WarrantyUntil TEXT,
        PRIMARY KEY (OrderID, PartID),
        FOREIGN KEY (OrderID) REFERENCES Orders(ID) ON DELETE CASCADE,
        FOREIGN KEY (PartID) REFERENCES Parts(ID)
    )
    ''')
    
    # Дополнительные таблицы
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS WorkSchedule (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        EmployeeID INTEGER NOT NULL,
        WorkDate TEXT NOT NULL,
        StartTime TEXT NOT NULL,
        EndTime TEXT NOT NULL,
        FOREIGN KEY (EmployeeID) REFERENCES Employees(ID)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Promotions (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Description TEXT,
        DiscountPercent REAL,
        StartDate TEXT NOT NULL,
        EndDate TEXT NOT NULL,
        ApplicableServices TEXT  -- ID услуг через запятую
    )
    ''')
    
    # Создаем индексы для ускорения поиска
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_cars_client ON Cars(ClientID)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_car ON Orders(CarID)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_status ON Orders(Status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_parts_supplier ON Parts(SupplierID)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_date ON Orders(DateIn)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_employees_position ON Employees(PositionID)')
    
    # Создаем триггеры
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_order_total
    AFTER INSERT OR UPDATE OR DELETE ON OrderServices OR OrderParts
    BEGIN
        UPDATE Orders SET TotalCost = (
            SELECT IFNULL(SUM(Services.Price * OrderServices.HoursSpent), 0) + 
                   IFNULL(SUM(OrderParts.Price * OrderParts.Quantity), 0)
            FROM Orders
            LEFT JOIN OrderServices ON Orders.ID = OrderServices.OrderID
            LEFT JOIN Services ON OrderServices.ServiceID = Services.ID
            LEFT JOIN OrderParts ON Orders.ID = OrderParts.OrderID
            WHERE Orders.ID = NEW.OrderID OR Orders.ID = OLD.OrderID
        ) WHERE ID = NEW.OrderID OR ID = OLD.OrderID;
    END;
    ''')
    
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS check_part_quantity
    BEFORE UPDATE ON Parts
    FOR EACH ROW
    WHEN NEW.Quantity < 0
    BEGIN
        SELECT RAISE(ABORT, 'Недостаточное количество запчастей на складе');
    END;
    ''')
    
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_part_quantity
    AFTER INSERT ON OrderParts
    BEGIN
        UPDATE Parts SET Quantity = Quantity - NEW.Quantity 
        WHERE ID = NEW.PartID;
    END;
    ''')
    
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS set_warranty_dates
    AFTER INSERT ON OrderServices
    BEGIN
        UPDATE OrderServices SET WarrantyUntil = date('now', '+' || 
            (SELECT WarrantyPeriod FROM Services WHERE ID = NEW.ServiceID) || ' days')
        WHERE OrderID = NEW.OrderID AND ServiceID = NEW.ServiceID;
    END;
    ''')
    
    conn.commit()
    conn.close()

def fill_sample_data():
    conn = sqlite3.connect('autoservice.db')
    cursor = conn.cursor()
    
    # Очистка таблиц перед заполнением (для тестирования)
    cursor.execute("DELETE FROM OrderParts")
    cursor.execute("DELETE FROM OrderServices")
    cursor.execute("DELETE FROM Orders")
    cursor.execute("DELETE FROM Cars")
    cursor.execute("DELETE FROM Clients")
    cursor.execute("DELETE FROM Parts")
    cursor.execute("DELETE FROM Suppliers")
    cursor.execute("DELETE FROM Services")
    cursor.execute("DELETE FROM Employees")
    cursor.execute("DELETE FROM Positions")
    cursor.execute("DELETE FROM WorkSchedule")
    cursor.execute("DELETE FROM Promotions")
    
    # Добавляем тестовые данные
    clients = [
        ('Иванов Иван Иванович', '+79161234567', 'ivanov@mail.ru', 'ул. Ленина, 1', 'Постоянный клиент'),
        ('Петров Петр Петрович', '+79169876543', 'petrov@mail.ru', 'ул. Пушкина, 10', 'Корпоративный клиент'),
        ('Сидорова Анна Сергеевна', '+79167778899', 'sidorova@mail.ru', 'пр. Мира, 5', 'VIP клиент'),
        ('Кузнецов Дмитрий Алексеевич', '+79165554433', 'kuznetsov@mail.ru', 'ул. Гагарина, 15',),
        ('Смирнова Елена Владимировна', '+79163332211', 'smirnova@mail.ru', 'ул. Советская, 20', 'Новый клиент')
    ]
    cursor.executemany('''
    INSERT INTO Clients (Name, Phone, Email, Address, Notes) 
    VALUES (?, ?, ?, ?, ?)
    ''', clients)
    
    positions = [
        ('Механик', 'Ремонт и обслуживание автомобилей', 50000, 5),
        ('Старший механик', 'Руководство бригадой механиков, сложные ремонты', 70000, 10),
        ('Приемщик', 'Прием и оформление заказов, общение с клиентами', 40000, 3),
        ('Менеджер', 'Управление автосервисом, закупки', 60000, 7),
        ('Маляр', 'Покраска автомобилей', 45000, 5)
    ]
    cursor.executemany('''
    INSERT INTO Positions (Title, Description, SalaryBase, BonusPercent) 
    VALUES (?, ?, ?, ?)
    ''', positions)
    
    employees = [
        ('Соколов Алексей Николаевич', 2, '+79161112233', 'sokolov@autoservice.ru', '2020-05-10', 75000, 'Active', '4510 123456'),
        ('Васильев Игорь Дмитриевич', 1, '+79162223344', 'vasiliev@autoservice.ru', '2021-03-15', 55000, 'Active', '4510 654321'),
        ('Павлова Ольга Сергеевна', 3, '+79163334455', 'pavlova@autoservice.ru', '2022-01-20', 42000, 'Active', '4510 789012'),
        ('Николаев Андрей Викторович', 1, '+79164445566', 'nikolaev@autoservice.ru', '2021-11-05', 52000, 'Active', '4510 345678'),
        ('Ковалева Марина Игоревна', 4, '+79165556677', 'kovaleva@autoservice.ru', '2020-07-01', 65000, 'Active', '4510 901234')
    ]
    cursor.executemany('''
    INSERT INTO Employees (Name, PositionID, Phone, Email, HireDate, Salary, Status, PassportData) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', employees)
    
    suppliers = [
        ('Автозапчасти ООО', 'Смирнов Д.А.', '+74951234567', 'info@autoparts.ru', 'г. Москва, ул. Промышленная, 10', 5, 2),
        ('ТехноАвто', 'Козлов В.С.', '+74959876543', 'sales@tehnoauto.ru', 'г. Москва, ш. Энтузиастов, 25', 4, 3),
        ('МоторКомплект', 'Белов П.Н.', '+74957778899', 'order@motorkomplekt.ru', 'г. Москва, пр. Вернадского, 15', 5, 1),
        ('АвтоДеталь', 'Зайцева Е.В.', '+74956665544', 'avtodetal@mail.ru', 'г. Москва, ул. Текстильщиков, 5', 3, 5)
    ]
    cursor.executemany('''
    INSERT INTO Suppliers (Name, ContactPerson, Phone, Email, Address, Rating, DeliveryTime) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', suppliers)
    
    parts = [
        ('Масло моторное 5W-30', 'Синтетическое моторное масло 5л', 2500, 15, 5, 1, 'OIL-5W30-SYN', 'Секция A, полка 3'),
        ('Тормозные колодки', 'Передние тормозные колодки Toyota Camry', 4800, 8, 3, 2, 'BRAKE-PAD-TC', 'Секция B, полка 1'),
        ('Воздушный фильтр', 'Фильтр воздушный Honda CR-V', 1200, 12, 5, 1, 'AIR-FIL-HCRV', 'Секция C, полка 2'),
        ('Свечи зажигания', 'Иридиевые свечи NGK', 800, 25, 10, 3, 'SPARK-NGK-IR', 'Секция A, полка 5'),
        ('Аккумулятор', 'Аккумулятор 60Ah', 6500, 5, 2, 4, 'BAT-60AH', 'Секция D, полка 1')
    ]
    cursor.executemany('''
    INSERT INTO Parts (Name, Description, Price, Quantity, MinQuantity, SupplierID, PartNumber, Location) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', parts)
    
    services = [
        ('Замена масла', 'Замена моторного масла и фильтра', 1500, 30, 'Техобслуживание', 180),
        ('Замена тормозных колодок', 'Замена передних или задних тормозных колодок', 3000, 60, 'Тормозная система', 90),
        ('Диагностика подвески', 'Компьютерная диагностика подвески', 2500, 45, 'Диагностика', 30),
        ('Развал-схождение', 'Регулировка углов установки колес', 3500, 90, 'Подвеска', 60),
        ('Замена ремня ГРМ', 'Замена ремня ГРМ с роликами', 8000, 180, 'Двигатель', 365)
    ]
    cursor.executemany('''
    INSERT INTO Services (Name, Description, Price, Duration, Category, WarrantyPeriod) 
    VALUES (?, ?, ?, ?, ?, ?)
    ''', services)
    
    cars = [
        (1, 'Toyota', 'Camry', 2018, 'XTA21000000000001', 'А123БВ777', 65000, '2023-01-15', '2023-07-15'),
        (1, 'Honda', 'CR-V', 2020, 'XTA21000000000002', 'Б456УК777', 32000, '2023-03-20', '2023-09-20'),
        (2, 'BMW', 'X5', 2019, 'XTA21000000000003', 'В789ТТ777', 78000, '2022-11-10', '2023-05-10'),
        (3, 'Kia', 'Rio', 2021, 'XTA21000000000004', 'Е321КХ777', 25000, '2023-02-05', '2023-08-05'),
        (4, 'Volkswagen', 'Tiguan', 2017, 'XTA21000000000005', 'М654АС777', 92000, '2022-12-20', '2023-06-20'),
        (5, 'Hyundai', 'Solaris', 2022, 'XTA21000000000006', 'О987РН777', 15000, '2023-04-01', '2023-10-01')
    ]
    cursor.executemany('''
    INSERT INTO Cars (ClientID, Brand, Model, Year, VIN, LicensePlate, Mileage, LastServiceDate, NextServiceDate) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', cars)
    
    orders = [
        (1, 2, '2023-05-10 09:00:00', '2023-05-10 12:30:00', 'Completed', 0, 
         'Замена масла и диагностика подвески', 'Рекомендуем заменить воздушный фильтр', 'Card', 'Paid'),
        (3, 1, '2023-05-11 10:00:00', '2023-05-11 15:00:00', 'Completed', 0, 
         'Замена тормозных колодок', 'Тормозные диски в хорошем состоянии', 'Cash', 'Paid'),
        (2, 3, '2023-05-12 11:00:00', None, 'In Progress', 0, 
         'Замена ремня ГРМ', None, None, 'Unpaid'),
        (4, 4, '2023-05-13 14:00:00', None, 'New', 0, 
         'Развал-схождение', None, None, 'Unpaid'),
        (5, 2, '2023-05-09 09:30:00', '2023-05-09 10:15:00', 'Completed', 0, 
         'Диагностика подвески', 'Подвеска в отличном состоянии', 'Transfer', 'Paid')
    ]
    cursor.executemany('''
    INSERT INTO Orders (CarID, EmployeeID, DateIn, DateOut, Status, TotalCost, 
                       ProblemDescription, Recommendations, PaymentMethod, PaymentStatus) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', orders)
    
    order_services = [
        (1, 1, 2, 0.5, 'Использовано масло 5W-30', None),
        (1, 3, 1, 1, 'Подвеска в норме, износа нет', None),
        (2, 2, 2, 1.5, 'Заменены передние колодки', None),
        (3, 5, 4, 3, 'Полный комплект роликов', None),
        (4, 4, 3, 1.5, None, None),
        (5, 3, 1, 0.75, 'Быстрая диагностика', None)
    ]
    cursor.executemany('''
    INSERT INTO OrderServices (OrderID, ServiceID, EmployeeID, HoursSpent, Notes, WarrantyUntil) 
    VALUES (?, ?, ?, ?, ?, ?)
    ''', order_services)
    
    order_parts = [
        (1, 1, 1, 2500, None),
        (1, 3, 1, 1200, None),
        (2, 2, 1, 4800, None),
        (3, 5, 1, 6500, None)
    ]
    cursor.executemany('''
    INSERT INTO OrderParts (OrderID, PartID, Quantity, Price, WarrantyUntil) 
    VALUES (?, ?, ?, ?, ?)
    ''', order_parts)
    
    # График работы сотрудников
    work_schedule = [
        (1, '2023-05-15', '09:00', '18:00'),
        (2, '2023-05-15', '08:00', '17:00'),
        (3, '2023-05-15', '10:00', '19:00'),
        (4, '2023-05-15', '09:00', '18:00'),
        (1, '2023-05-16', '09:00', '18:00'),
        (2, '2023-05-16', '08:00', '17:00')
    ]
    cursor.executemany('''
    INSERT INTO WorkSchedule (EmployeeID, WorkDate, StartTime, EndTime) 
    VALUES (?, ?, ?, ?)
    ''', work_schedule)
    
    # Акции и скидки
    promotions = [
        ('Весеннее обслуживание', 'Скидка 15% на все услуги по ТО', 15, '2023-05-01', '2023-05-31', '1,3'),
        ('Комплексная диагностика', 'Бесплатная диагностика при комплексном обслуживании', 0, '2023-05-10', '2023-06-10', '3')
    ]
    cursor.executemany('''
    INSERT INTO Promotions (Name, Description, DiscountPercent, StartDate, EndDate, ApplicableServices) 
    VALUES (?, ?, ?, ?, ?, ?)
    ''', promotions)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    fill_sample_data()
    print("База данных 'autoservice.db' успешно создана и заполнена тестовыми данными")