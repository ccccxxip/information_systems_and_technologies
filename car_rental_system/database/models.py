from sqlite3 import Connection

def create_tables(conn: Connection):
    """Создает все таблицы в базе данных"""
    cursor = conn.cursor()
    
    # Таблица категорий автомобилей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        daily_rate REAL NOT NULL CHECK(daily_rate > 0),
        deposit_amount REAL NOT NULL CHECK(deposit_amount >= 0),
        description TEXT
    )''')
    
    # Таблица дополнительных услуг
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS services (
        service_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        price REAL NOT NULL CHECK(price >= 0),
        description TEXT
    )''')
    
    # Таблица сотрудников
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        position TEXT NOT NULL,
        hire_date DATE NOT NULL,
        phone TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        salary REAL CHECK(salary >= 0),
        is_active BOOLEAN DEFAULT TRUE
    )''')
    
    # Таблица автомобилей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cars (
        car_id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand TEXT NOT NULL,
        model TEXT NOT NULL,
        year INTEGER NOT NULL CHECK(year > 1900),
        license_plate TEXT UNIQUE NOT NULL,
        category_id INTEGER NOT NULL,
        color TEXT,
        mileage INTEGER DEFAULT 0 CHECK(mileage >= 0),
        vin TEXT UNIQUE,
        status TEXT NOT NULL CHECK(status IN ('available', 'rented', 'maintenance', 'reserved')) DEFAULT 'available',
        purchase_date DATE,
        last_service_date DATE,
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
    )''')
    
    # Таблица клиентов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        client_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        birth_date DATE,
        passport_number TEXT UNIQUE NOT NULL,
        driver_license TEXT UNIQUE NOT NULL,
        phone TEXT NOT NULL,
        email TEXT,
        registration_date DATE NOT NULL DEFAULT CURRENT_DATE,
        rating INTEGER DEFAULT 5 CHECK(rating BETWEEN 1 AND 5),
        address TEXT,
        blacklisted BOOLEAN DEFAULT FALSE
    )''')
    
    # Таблица аренд
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rentals (
        rental_id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        car_id INTEGER NOT NULL,
        start_date DATETIME NOT NULL,
        end_date DATETIME NOT NULL,
        actual_end_date DATETIME,
        total_cost REAL NOT NULL CHECK(total_cost >= 0),
        deposit_amount REAL NOT NULL CHECK(deposit_amount >= 0),
        status TEXT NOT NULL CHECK(status IN ('reserved', 'active', 'completed', 'cancelled', 'overdue')),
        notes TEXT,
        employee_id INTEGER,
        FOREIGN KEY (client_id) REFERENCES clients(client_id),
        FOREIGN KEY (car_id) REFERENCES cars(car_id),
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
        CHECK (end_date > start_date)
    )''')
    
    # Таблица платежей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        rental_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        payment_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        payment_method TEXT NOT NULL CHECK(payment_method IN ('cash', 'card', 'bank_transfer', 'online')),
        transaction_id TEXT,
        status TEXT NOT NULL CHECK(status IN ('pending', 'completed', 'failed', 'refunded')),
        FOREIGN KEY (rental_id) REFERENCES rentals(rental_id)
    )''')
    
    # Таблица повреждений
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS damages (
        damage_id INTEGER PRIMARY KEY AUTOINCREMENT,
        rental_id INTEGER NOT NULL,

        car_id INTEGER NOT NULL,
        description TEXT NOT NULL,
        repair_cost REAL NOT NULL CHECK(repair_cost >= 0),
        reported_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        repaired_date DATETIME,
        status TEXT NOT NULL CHECK(status IN ('reported', 'under_repair', 'repaired', 'paid')),
        employee_id INTEGER,
        FOREIGN KEY (rental_id) REFERENCES rentals(rental_id),
        FOREIGN KEY (car_id) REFERENCES cars(car_id),
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
    )''')
    
    # Таблица связей аренда-услуги (многие-ко-многим)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rental_services (
        rental_service_id INTEGER PRIMARY KEY AUTOINCREMENT,
        rental_id INTEGER NOT NULL,
        service_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1 CHECK(quantity > 0),
        FOREIGN KEY (rental_id) REFERENCES rentals(rental_id),
        FOREIGN KEY (service_id) REFERENCES services(service_id),
        UNIQUE (rental_id, service_id)
    )''')
    
    conn.commit()
