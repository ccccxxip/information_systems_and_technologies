import mysql.connector
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime, timedelta
import logging
from mysql.connector import Error
import mysql.connector
import configparser
from pathlib import Path
import time

#logging.basicConfig(level=logging.DEBUG, filename='rental.log')


def get_db_connection():
    """
    Универсальная функция подключения к MySQL с:
    - Чтением конфига из файла
    - Таймаутами подключения
    - Проверкой минимальных требований
    - Безопасным закрытием ресурсов
    """
    # Путь к конфигу (кросс-платформенный)
    config_path = Path.home() / ".car_rental_config.ini"
    
    # Параметры по умолчанию
    config = {
        'host': 'localhost',
        'user': 'ccccxxip',
        'password': '1234',
        'database': 'car_rental',
        'port': '3306',
        'auth_plugin': 'mysql_native_password',
        'connect_timeout': 5,
        'connection_retries': 3
    }

    try:
        # Чтение конфига если существует
        if config_path.exists():
            cfg = configparser.ConfigParser()
            cfg.read(config_path)
            if 'database' in cfg:
                config.update(cfg['database'])

        # Попытка подключения с ретраями
        for attempt in range(int(config['connection_retries'])):
            try:
                conn = mysql.connector.connect(
                    host=config['host'],
                    user=config['user'],
                    password=config['password'],
                    database=config['database'],
                    port=int(config['port']),
                    auth_plugin=config['auth_plugin'],
                    connect_timeout=int(config['connect_timeout'])
                )
                
                # Проверка работоспособности подключения
                with conn.cursor() as test_cursor:
                    test_cursor.execute("SELECT 1")
                    if test_cursor.fetchone()[0] == 1:
                        return conn
                    
            except Error as e:
                if attempt == int(config['connection_retries']) - 1:
                    raise  # Последняя попытка - пробрасываем исключение
                time.sleep(1)  # Задержка между попытками

    except Error as e:
        messagebox.showerror(
            "Ошибка БД", 
            f"Не удалось подключиться к MySQL:\n"
            f"Ошибка: {e}\n"
            f"Проверьте:\n"
            f"1. Запущен ли сервер MySQL\n"
            f"2. Правильность логина/пароля\n"
            f"3. Доступность хоста {config['host']}:{config['port']}"
        )
    except Exception as e:
        messagebox.showerror(
            "Критическая ошибка", 
            f"Непредвиденная ошибка:\n{type(e).__name__}: {e}"
        )
    
    return None



class CarRentalSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Система управления автопрокатом")
        self.root.geometry("1000x700")
        
        # Стили
        self.style = ttk.Style()
        self.style.configure("Treeview", font=('Arial', 10))
        self.style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        
        # Создаем вкладки
        self.notebook = ttk.Notebook(root)
        
        # Вкладки
        self.cars_tab = ttk.Frame(self.notebook)
        self.clients_tab = ttk.Frame(self.notebook)
        self.rentals_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.cars_tab, text="Автомобили")
        self.notebook.add(self.clients_tab, text="Клиенты")
        self.notebook.add(self.rentals_tab, text="Аренда")
        
        self.notebook.pack(expand=True, fill="both")
        
        # Инициализация вкладок
        self.init_cars_tab()
        self.init_clients_tab()
        self.init_rentals_tab()

    # ===== ВКЛАДКА АВТОМОБИЛИ =====
    def init_cars_tab(self):
        # Таблица автомобилей
        self.cars_tree = ttk.Treeview(self.cars_tab, columns=("ID", "Марка", "Модель",
                                                               "Год", "Цвет", "Пробег",
                                                                 "Цена", "Доступен"), show="headings")
        
        
        # Настройка колонок
        columns = [
            ("ID", 50), ("Марка", 120), ("Модель", 120), 
            ("Год", 60), ("Цвет", 80), ("Пробег", 80), 
            ("Цена", 80), ("Доступен", 80)
        ]
        
        for col, width in columns:
            self.cars_tree.heading(col, text=col)
            self.cars_tree.column(col, width=width, anchor=CENTER)
        
        self.cars_tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Панель управления
        control_frame = Frame(self.root)
        control_frame.pack(fill=X, padx=10, pady=5)
        
        Button(control_frame, text="Обновить", command=self.load_cars).pack(side=LEFT, padx=5)
        Button(control_frame, text="Удалить", command=self.delete_car).pack(side=LEFT, padx=5)
        Button(control_frame, text="Добавить авто", command=self.show_add_car_dialog).pack(side=LEFT, padx=5)
        Button(control_frame, text="Добавить бренд", command=self.show_add_brand_dialog).pack(side=LEFT, padx=5)
        Button(control_frame, text="Добавить модель", command=self.show_add_model_dialog).pack(side=LEFT, padx=5)
        
        # Загрузка данных
        self.load_cars()

    def load_cars(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Тестовый запрос - подсчет всех автомобилей
            cursor.execute("SELECT COUNT(*) FROM Cars")
            total_cars = cursor.fetchone()[0]
            print(f"Всего автомобилей в БД: {total_cars}")  # Должно быть 9 по вашим данным
            
            # Основной запрос
            cursor.execute("""
                SELECT c.car_id, b.brand_name, m.model_name, m.year, 
                    c.color, c.mileage, c.daily_price, c.is_available
                FROM Cars c
                LEFT JOIN Models m ON c.model_id = m.model_id
                LEFT JOIN Brands b ON m.brand_id = b.brand_id
            """)
            
            print(f"Загружено строк: {cursor.rowcount}")  # Должно быть 9
            
            # Очистка и заполнение Treeview
            self.cars_tree.delete(*self.cars_tree.get_children())
            for row in cursor:
                print("Добавляем авто:", row)  # Выведет каждую строку
                self.cars_tree.insert("", END, values=row)
                
        except Exception as e:
            print("Ошибка загрузки:", e)
            messagebox.showerror("Ошибка", f"Не удалось загрузить авто: {e}")
        finally:
            if conn.is_connected():
                conn.close()

    # ===== ВКЛАДКА КЛИЕНТЫ =====
    def init_clients_tab(self):
        # Таблица клиентов
        self.clients_tree = ttk.Treeview(self.clients_tab, columns=("ID", "Имя", "Фамилия", "Телефон", "Рейтинг"), show="headings")
        
        # Настройка колонок
        columns = [
            ("ID", 50), ("Имя", 120), ("Фамилия", 120), 
            ("Телефон", 120), ("Рейтинг", 80)
        ]
        
        for col, width in columns:
            self.clients_tree.heading(col, text=col)
            self.clients_tree.column(col, width=width, anchor=CENTER)
        
        self.clients_tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Панель управления
        control_frame = Frame(self.clients_tab)
        control_frame.pack(fill=X, padx=10, pady=5)
        
        Button(control_frame, text="Обновить", command=self.load_clients).pack(side=LEFT, padx=5)
        Button(control_frame, text="Добавить клиента", command=self.show_add_client_dialog).pack(side=LEFT, padx=5)
        Button(control_frame, text="Удалить", command=self.delete_client, bg='#ffcccc').pack(side=LEFT, padx=5)
        
        # Загрузка данных
        self.load_clients()

    def load_clients(self):
        """Загружает данные о клиентах"""
        conn = get_db_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT client_id, first_name, last_name, phone, rating
                FROM Clients
                ORDER BY client_id
            """)
            
            # Очищаем таблицу
            for row in self.clients_tree.get_children():
                self.clients_tree.delete(row)
            
            # Добавляем данные
            for row in cursor:
                self.clients_tree.insert("", END, values=row)
                
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Ошибка загрузки клиентов: {err}")
        finally:
            conn.close()

    # ===== ВКЛАДКА АРЕНДА =====
    def init_rentals_tab(self):
        # Таблица аренд
        self.rentals_tree = ttk.Treeview(
            self.rentals_tab, 
            columns=("ID", "Клиент", "Автомобиль", "Начало", "Конец", "Статус"), 
            show="headings"
        )
        
        # Настройка колонок
        columns = [
            ("ID", 50), ("Клиент", 150), ("Автомобиль", 150), 
            ("Начало", 120), ("Конец", 120), ("Статус", 100)
        ]
        
        for col, width in columns:
            self.rentals_tree.heading(col, text=col)
            self.rentals_tree.column(col, width=width, anchor=CENTER)
        
        self.rentals_tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Панель управления
        control_frame = Frame(self.rentals_tab)
        control_frame.pack(fill=X, padx=10, pady=5)
        
        Button(control_frame, text="Обновить", command=self.load_rentals).pack(side=LEFT, padx=5)
        Button(control_frame, text="Новая аренда", command=self.show_new_rental_dialog).pack(side=LEFT, padx=5)
        Button(control_frame, text="Завершить аренду", command=self.complete_rental, bg='#ffcccc').pack(side=LEFT, padx=5)
        
        # Загрузка данных
        self.load_rentals()

    def load_rentals(self):
        """Загрузка аренд с учетом новой структуры"""
        conn = get_db_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    r.rental_id,
                    CONCAT(c.first_name, ' ', c.last_name) AS client_name,
                    CONCAT(b.brand_name, ' ', m.model_name) AS car_name,
                    DATE_FORMAT(r.start_datetime, '%Y-%m-%d %H:%i') AS start_date,
                    DATE_FORMAT(r.planned_end_datetime, '%Y-%m-%d %H:%i') AS end_date,
                    CASE 
                        WHEN r.status = 'active' THEN 'Активна'
                        WHEN r.status = 'completed' THEN 'Завершена'
                        ELSE r.status
                    END AS status_text
                FROM Rentals r
                JOIN Clients c ON r.client_id = c.client_id
                JOIN Cars car ON r.car_id = car.car_id
                JOIN Models m ON car.model_id = m.model_id
                JOIN Brands b ON m.brand_id = b.brand_id
                ORDER BY r.rental_id DESC
            """)
            
            # Очистка таблицы
            for row in self.rentals_tree.get_children():
                self.rentals_tree.delete(row)
                
            # Заполнение данными
            for row in cursor:
                self.rentals_tree.insert("", END, values=(
                    row['rental_id'],
                    row['client_name'],
                    row['car_name'],
                    row['start_date'],
                    row['end_date'],
                    row['status_text']
                ))
                
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Ошибка загрузки аренд: {err}")
        finally:
            conn.close()

    # ===== ДИАЛОГОВЫЕ ОКНА =====
    def show_add_client_dialog(self):
        """Показывает диалог добавления клиента"""
        dialog = Toplevel(self.root)
        dialog.title("Добавить клиента")
        dialog.geometry("400x300")
        
        # Поля формы
        fields = [
            ("Имя*", "first_name"),
            ("Фамилия*", "last_name"),
            ("Дата рождения (ГГГГ-ММ-ДД)*", "birth_date"),
            ("Водительские права*", "driver_license"),
            ("Телефон*", "phone"),
            ("Email", "email")
        ]
        
        self.entries = {}
        for i, (label, field) in enumerate(fields):
            Label(dialog, text=label).grid(row=i, column=0, padx=10, pady=5, sticky=W)
            entry = Entry(dialog)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky=EW)
            self.entries[field] = entry
        
        Button(dialog, text="Добавить", command=self._add_client).grid(
            row=len(fields), columnspan=2, pady=10)
        
    def show_add_brand_dialog(self):
        dialog = Toplevel(self.root)
        dialog.title("Добавить новый бренд")
        
        Label(dialog, text="Название бренда*:").grid(row=0, column=0, padx=10, pady=5)
        brand_entry = Entry(dialog)
        brand_entry.grid(row=0, column=1, padx=10, pady=5)
        
        Label(dialog, text="Страна:").grid(row=1, column=0, padx=10, pady=5)
        country_entry = Entry(dialog)
        country_entry.grid(row=1, column=1, padx=10, pady=5)
        
        def save_brand():
            brand = brand_entry.get().strip()
            country = country_entry.get().strip() or None
            
            if not brand:
                messagebox.showwarning("Ошибка", "Название бренда обязательно!")
                return
                
            if self.add_brand(brand, country):
                messagebox.showinfo("Успех", "Бренд успешно добавлен!")
                dialog.destroy()
                self.load_cars()  # Обновить список
        
        Button(dialog, text="Сохранить", command=save_brand).grid(row=2, columnspan=2, pady=10)
        
    def _add_client(self):
        """Добавление клиента с проверкой всех полей"""
        try:
            # Собираем данные
            data = {
                'first_name': self.entries['first_name'].get().strip(),
                'last_name': self.entries['last_name'].get().strip(),
                'birth_date': self.entries['birth_date'].get().strip(),
                'driver_license': self.entries['driver_license'].get().strip(),
                'phone': self.entries['phone'].get().strip(),
                'email': self.entries['email'].get().strip() or None
            }
            
            # Проверка обязательных полей
            required = ['first_name', 'last_name', 'birth_date', 'driver_license', 'phone']
            if not all(data[field] for field in required):
                raise ValueError("Все поля, помеченные *, обязательны для заполнения")
            
            # Проверка формата даты
            datetime.strptime(data['birth_date'], '%Y-%m-%d')
            
            # Проверка уникальности прав и телефона
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM Clients 
                    WHERE driver_license = %s OR phone = %s
                """, (data['driver_license'], data['phone']))
                if cursor.fetchone()[0] > 0:
                    raise ValueError("Клиент с такими правами или телефоном уже существует")
                
                # Добавление клиента
                cursor.execute("""
                    INSERT INTO Clients 
                    (first_name, last_name, birth_date, driver_license, phone, email)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, tuple(data.values()))
                
                conn.commit()
                messagebox.showinfo("Успех", "Клиент успешно добавлен!")
                self.load_clients()
                
        except ValueError as ve:
            messagebox.showerror("Ошибка ввода", str(ve))
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка БД", f"Ошибка MySQL: {err}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неизвестная ошибка: {str(e)}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                conn.close()


    def show_new_rental_dialog(self):
        """Показывает диалог оформления новой аренды"""
        dialog = Toplevel(self.root)
        dialog.title("Новая аренда")
        dialog.geometry("400x300")
        
        # Получаем список клиентов
        clients = self.get_clients_list()
        cars = self.get_available_cars_list()
        
        if not clients or not cars:
            messagebox.showwarning("Предупреждение", "Нет доступных клиентов или автомобилей")
            dialog.destroy()
            return
        
        Label(dialog, text="Клиент:").grid(row=0, column=0, padx=10, pady=5, sticky=W)
        client_combobox = ttk.Combobox(dialog, values=clients, state="readonly")
        client_combobox.grid(row=0, column=1, padx=10, pady=5, sticky=EW)
        client_combobox.current(0)
        
        Label(dialog, text="Автомобиль:").grid(row=1, column=0, padx=10, pady=5, sticky=W)
        car_combobox = ttk.Combobox(dialog, values=cars, state="readonly")
        car_combobox.grid(row=1, column=1, padx=10, pady=5, sticky=EW)
        car_combobox.current(0)
        
        Label(dialog, text="Срок (дней):").grid(row=2, column=0, padx=10, pady=5, sticky=W)
        days_entry = Entry(dialog)
        days_entry.insert(0, "3")
        days_entry.grid(row=2, column=1, padx=10, pady=5, sticky=EW)
        
        Button(dialog, text="Оформить", command=lambda: self.add_rental(
            client_combobox.get(),
            car_combobox.get(),
            days_entry.get()
        )).grid(row=3, columnspan=2, pady=10)
        
    def show_add_car_dialog(self):
        dialog = Toplevel(self.root)
        dialog.title("Добавить автомобиль")
        dialog.geometry("600x500")
        
        # Получаем данные для выпадающих списков
        brands = self.get_brands_list()
        models = self.get_models_list()
        fuel_types = self.get_fuel_types_list()
        parkings = self.get_parkings_list()


        if not all([brands, models, fuel_types]):
            messagebox.showerror("Ошибка", "Не удалось загрузить справочные данные!")
            dialog.destroy()
            return
        
        # Создаем и размещаем элементы формы
        self.car_entries = {}
        fields = [
            ("Марка*", "brand", brands),
            ("Модель*", "model", models),
            ("Тип топлива*", "fuel_type", fuel_types),
            ("Парковка", "parking", parkings),
            ("Рег. номер*", "reg_number", None),
            ("VIN-код*", "vin", None),
            ("Цвет", "color", None),
            ("Пробег", "mileage", None),
            ("Цена/день*", "price", None),
            ("Дата покупки (ГГГГ-ММ-ДД)", "purchase_date", None)
        ]

        for i, (label, field, values) in enumerate(fields):
            Label(dialog, text=label).grid(row=i, column=0, padx=10, pady=5, sticky=W)
            if values:
                cb = ttk.Combobox(dialog, values=values, state="readonly")
                cb.grid(row=i, column=1, padx=10, pady=5, sticky=EW)
                if values: cb.current(0)
                self.car_entries[field] = cb
            else:
                entry = Entry(dialog)
                entry.grid(row=i, column=1, padx=10, pady=5, sticky=EW)
                self.car_entries[field] = entry

        # Кнопки управления (добавлены в отдельный фрейм)
        button_frame = Frame(dialog)
        button_frame.grid(row=len(fields)+1, columnspan=2, pady=10)
        
        # Основная кнопка добавления
        Button(button_frame, text="Добавить автомобиль", 
            command=self._add_car, bg='#4CAF50', fg='white').pack(side=LEFT, padx=5)
        
        # Вспомогательные кнопки
        Button(button_frame, text="Добавить бренд", 
            command=self.show_add_brand_dialog).pack(side=LEFT, padx=5)
        Button(button_frame, text="Добавить модель", 
            command=self.show_add_model_dialog).pack(side=LEFT, padx=5)
        Button(button_frame, text="Отмена", 
            command=dialog.destroy).pack(side=LEFT, padx=5)
    def show_add_model_dialog(self):
        dialog = Toplevel(self.root)
        dialog.title("Добавить новую модель")
        dialog.geometry("400x300")
        
        # Получаем список брендов
        brands = self.get_brands_list()
        if not brands:
            messagebox.showerror("Ошибка", "Нет доступных брендов!")
            dialog.destroy()
            return
        
        # Элементы формы
        Label(dialog, text="Бренд*:").grid(row=0, column=0, padx=10, pady=5, sticky=W)
        brand_combobox = ttk.Combobox(dialog, values=brands, state="readonly")
        brand_combobox.grid(row=0, column=1, padx=10, pady=5, sticky=EW)
        brand_combobox.current(0)
        
        Label(dialog, text="Название модели*:").grid(row=1, column=0, padx=10, pady=5, sticky=W)
        model_entry = Entry(dialog)
        model_entry.grid(row=1, column=1, padx=10, pady=5, sticky=EW)
        
        Label(dialog, text="Год выпуска:").grid(row=2, column=0, padx=10, pady=5, sticky=W)
        year_entry = Entry(dialog)
        year_entry.grid(row=2, column=1, padx=10, pady=5, sticky=EW)
        
        Label(dialog, text="Класс автомобиля:").grid(row=3, column=0, padx=10, pady=5, sticky=W)
        class_entry = Entry(dialog)
        class_entry.grid(row=3, column=1, padx=10, pady=5, sticky=EW)
        
        def save_model():
            try:
                brand_id = int(brand_combobox.get().split(' - ')[0])
                model_name = model_entry.get().strip()
                year = year_entry.get().strip() or None
                car_class = class_entry.get().strip() or None
                
                if not model_name:
                    raise ValueError("Название модели обязательно!")
                    
                if year:
                    year = int(year)
                    if year < 1900 or year > datetime.now().year + 1:
                        raise ValueError(f"Некорректный год (должен быть между 1900 и {datetime.now().year + 1})")
                
                if self.add_model(brand_id, model_name, year, car_class):
                    messagebox.showinfo("Успех", "Модель успешно добавлена!")
                    # Обновляем список моделей в диалоге добавления автомобиля, если он открыт
                    for widget in self.root.winfo_children():
                        if isinstance(widget, Toplevel) and widget.title() == "Добавить автомобиль":
                            self.update_model_combobox(widget)
                    dialog.destroy()
                    
            except ValueError as ve:
                messagebox.showerror("Ошибка ввода", str(ve))
            except Exception as e:
                messagebox.showerror("Ошибка", f"Неизвестная ошибка: {str(e)}")
        
        Button(dialog, text="Сохранить", command=save_model).grid(
            row=4, columnspan=2, pady=10)
        
        def update_model_combobox(self, dialog):
            """Обновляет combobox с моделями в диалоге добавления автомобиля"""
            for widget in dialog.winfo_children():
                if isinstance(widget, ttk.Combobox) and "Модель" in str(widget.master.winfo_children()[0].cget("text")):
                    models = self.get_models_list()
                    widget['values'] = models
                    if models:
                        widget.current(0)
                    break

    def _add_car(self):
        # Проверка данных
        errors = self.validate_car_data()
        if errors:
            messagebox.showerror("Ошибка", "Обнаружены ошибки:\n- " + "\n- ".join(errors))
            return
        
        try:
            # Получаем данные из формы
            model_id = int(self.car_entries['model'].get().split(' - ')[0])
            fuel_id = int(self.car_entries['fuel_type'].get().split(' - ')[0])
            reg_number = self.car_entries['reg_number'].get().strip()
            vin = self.car_entries['vin'].get().strip()
            daily_price = float(self.car_entries['price'].get())
            
            # Необязательные поля
            parking = self.car_entries['parking'].get()
            parking_id = int(parking.split(' - ')[0]) if parking else None
            color = self.car_entries['color'].get().strip() or None
            mileage = int(self.car_entries['mileage'].get()) if self.car_entries['mileage'].get().strip() else 0
            purchase_date = self.car_entries['purchase_date'].get().strip() or None
            
            # Проверка уникальности регистрационного номера и VIN
            conn = get_db_connection()
            if not conn:
                return
                
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Cars WHERE registration_number = %s OR vin = %s", 
                        (reg_number, vin))
            if cursor.fetchone()[0] > 0:
                raise ValueError("Автомобиль с таким регистрационным номером или VIN уже существует")
            
            # Вставка данных
            cursor.execute("""
                INSERT INTO Cars (
                    model_id, fuel_id, parking_id,
                    registration_number, vin, color,
                    mileage, purchase_date, daily_price
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                model_id, fuel_id, parking_id,
                reg_number, vin, color,
                mileage, purchase_date, daily_price
            ))
            
            conn.commit()
            messagebox.showinfo("Успех", "Автомобиль успешно добавлен!")
            self.load_cars()
            
        except ValueError as ve:
            messagebox.showerror("Ошибка ввода", str(ve))
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка БД", f"Ошибка {err.errno}: {err.msg}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неизвестная ошибка: {str(e)}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                conn.close()

    def delete_car(self):
        """Удаление автомобиля с проверкой зависимостей"""
        selected = self.cars_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите автомобиль для удаления!")
            return
            
        car_id = self.cars_tree.item(selected[0])['values'][0]
        
        conn = get_db_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            
            # Проверяем, есть ли активные аренды
            cursor.execute("""
                SELECT COUNT(*) FROM Rentals 
                WHERE car_id = %s AND status = 'active'
            """, (car_id,))
            
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Ошибка", 
                                "Нельзя удалить автомобиль с активной арендой!")
                return
                
            if not messagebox.askyesno("Подтверждение", 
                                    f"Удалить автомобиль ID {car_id}? Это также удалит все связанные записи."):
                return
                
            # Удаляем связанные записи в CarConditions
            cursor.execute("DELETE FROM CarConditions WHERE car_id = %s", (car_id,))
            
            # Удаляем связанные аренды
            cursor.execute("DELETE FROM Rentals WHERE car_id = %s", (car_id,))
            
            # Удаляем сам автомобиль
            cursor.execute("DELETE FROM Cars WHERE car_id = %s", (car_id,))
            
            conn.commit()
            messagebox.showinfo("Успех", "Автомобиль и связанные данные удалены!")
            self.load_cars()
            self.load_rentals()
            
        except mysql.connector.Error as err:
            conn.rollback()
            messagebox.showerror("Ошибка", f"Не удалось удалить автомобиль:\n{err}")
        finally:
            conn.close()

    def get_brands_list(self):
        """Список марок для Combobox"""
        conn = get_db_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT brand_id, brand_name FROM Brands ORDER BY brand_name")
            return [f"{row[0]} - {row[1]}" for row in cursor]
        finally:
            conn.close()

    def get_models_list(self):
        """Возвращает список моделей в формате 'ID - Бренд Модель (Год)'"""
        conn = get_db_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.model_id, b.brand_name, m.model_name, m.year
                FROM Models m 
                JOIN Brands b ON m.brand_id = b.brand_id
                ORDER BY b.brand_name, m.model_name
            """)
            return [f"{row[0]} - {row[1]} {row[2]}" + (f" ({row[3]})" if row[3] else "") for row in cursor]
        finally:
            conn.close()

    def get_fuel_types_list(self):
        """Возвращает список типов топлива"""
        conn = get_db_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT fuel_id, fuel_name FROM FuelTypes")
            return [f"{row[0]} - {row[1]}" for row in cursor]
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Не удалось загрузить типы топлива: {err}")
            return []
        finally:
            if conn.is_connected():
                conn.close()
    
    def get_parkings_list(self):
        """Список парковок"""
        conn = get_db_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT parking_id, address FROM Parkings ORDER BY address")
            return [f"{row[0]} - {row[1]}" for row in cursor]
        finally:
            conn.close()

    # ===== ОСНОВНЫЕ МЕТОДЫ РАБОТЫ С БД =====
    def add_client(self, first_name, last_name, phone):
        """Добавляет нового клиента с проверкой ошибок"""
        if not first_name or not last_name:
            messagebox.showwarning("Ошибка", "Имя и фамилия обязательны!")
            return
        
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return
                
            cursor = conn.cursor()
            
            # Проверяем, существует ли уже клиент с таким телефоном
            cursor.execute("SELECT COUNT(*) FROM Clients WHERE phone = %s", (phone,))
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Ошибка", "Клиент с таким телефоном уже существует!")
                return
                
            # Вставляем нового клиента
            cursor.execute(
                "INSERT INTO Clients (first_name, last_name, phone, rating) VALUES (%s, %s, %s, %s)",
                (first_name.strip(), last_name.strip(), phone.strip(), 5.0)  # Начальный рейтинг 5.0
            )
            conn.commit()
            messagebox.showinfo("Успех", "Клиент успешно добавлен!")
            self.load_clients()
            
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка БД", f"Не удалось добавить клиента:\n{err}")
            if conn:
                conn.rollback()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неожиданная ошибка:\n{e}")
        finally:
            if conn:
                conn.close()
    
    def validate_car_data(self):
        """Проверяет обязательные поля перед добавлением автомобиля"""
        errors = []
        
        if not self.car_entries['model'].get():
            errors.append("Не выбрана модель")
        if not self.car_entries['fuel_type'].get():
            errors.append("Не выбран тип топлива")
        if not self.car_entries['reg_number'].get().strip():
            errors.append("Не указан регистрационный номер")
        if not self.car_entries['vin'].get().strip():
            errors.append("Не указан VIN-код")
        try:
            float(self.car_entries['price'].get())
        except:
            errors.append("Некорректная цена")
        
        return errors

    def add_rental(self, client_str, car_str, days_str):
        """Оформление аренды с учётом всех проверенных данных"""
        try:
            # 1. Извлечение данных
            client_id = int(client_str.split('-')[0].strip())
            car_id = int(car_str.split('-')[0].strip())
            days = int(days_str)
            
            if days <= 0:
                raise ValueError("Срок аренды должен быть больше 0 дней")

            # 2. Подключение к БД
            conn = get_db_connection()
            if not conn:
                return
                
            cursor = conn.cursor(dictionary=True)
            
            try:
                # 3. Проверка клиента
                cursor.execute("SELECT client_id FROM Clients WHERE client_id = %s", (client_id,))
                if not cursor.fetchone():
                    raise ValueError("Клиент не найден")

                # 4. Проверка авто и получение данных
                cursor.execute("""
                    SELECT 
                        c.car_id, 
                        c.daily_price,
                        c.parking_id,
                        (SELECT condition_id FROM CarConditions WHERE car_id = c.car_id ORDER BY check_datetime DESC LIMIT 1) AS current_condition
                    FROM Cars c
                    WHERE c.car_id = %s AND c.is_available = TRUE
                    FOR UPDATE
                """, (car_id,))
                
                car_data = cursor.fetchone()
                if not car_data:
                    raise ValueError("Автомобиль недоступен для аренды")
                    
                if not car_data['current_condition']:
                    raise ValueError("Не найдено текущее состояние автомобиля")

                # 5. Получаем первый доступный тариф
                cursor.execute("SELECT tariff_id FROM Tariffs ORDER BY tariff_id LIMIT 1")
                tariff = cursor.fetchone()
                if not tariff:
                    raise ValueError("Не найдено ни одного тарифа")

                # 6. Подготовка данных для аренды
                start_date = datetime.now()
                end_date = start_date + timedelta(days=days)
                total_price = car_data['daily_price'] * days
                
                # 7. Создание аренды
                cursor.execute("""
                    INSERT INTO Rentals (
                        client_id, 
                        car_id, 
                        tariff_id,
                        start_condition_id,
                        start_parking_id,
                        start_datetime, 
                        planned_end_datetime,
                        total_cost,
                        status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'active')
                """, (
                    client_id,
                    car_id,
                    tariff['tariff_id'],
                    car_data['current_condition'],
                    car_data['parking_id'],
                    start_date,
                    end_date,
                    total_price
                ))
                
                # 8. Обновление статуса авто
                cursor.execute("""
                    UPDATE Cars SET is_available = FALSE 
                    WHERE car_id = %s
                """, (car_id,))
                
                conn.commit()
                messagebox.showinfo(
                    "Успех", 
                    f"Аренда оформлена!\n"
                    f"Стоимость: {total_price:.2f} руб.\n"
                    f"Период: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}"
                )
                
                self.load_rentals()
                self.load_cars()
                
            except mysql.connector.Error as err:
                conn.rollback()
                raise err
                
        except ValueError as ve:
            messagebox.showerror("Ошибка ввода", str(ve))
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка БД", f"Ошибка MySQL {err.errno}:\n{err.msg}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неизвестная ошибка:\n{str(e)}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                conn.close()
                
    def add_brand(self, brand_name, country=None):
        conn = get_db_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Brands (brand_name, country) VALUES (%s, %s)", 
                        (brand_name, country))
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Не удалось добавить бренд: {err}")
            return None
        finally:
            conn.close()
    
    def add_model(self, brand_id, model_name, year=None, car_class=None):
        conn = get_db_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Models (brand_id, model_name, year, car_class)
                VALUES (%s, %s, %s, %s)
            """, (brand_id, model_name, year, car_class))
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Не удалось добавить модель: {err}")
            return None
        finally:
            conn.close()
                    
    def delete_car(self):
        """Удаление выбранного автомобиля из базы данных"""
        # Получаем выделенный элемент в Treeview
        selected_item = self.cars_tree.selection()
        
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите автомобиль для удаления!")
            return
        
        # Получаем ID автомобиля из первого столбца выделенной строки
        car_id = self.cars_tree.item(selected_item[0])['values'][0]
        
        # Подтверждение удаления
        if not messagebox.askyesno("Подтверждение", 
                                f"Вы точно хотите удалить автомобиль ID {car_id}?\nЭто действие нельзя отменить!"):
            return
        
        conn = get_db_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            
            # 1. Проверяем активные аренды этого автомобиля
            cursor.execute("""
                SELECT COUNT(*) FROM Rentals 
                WHERE car_id = %s AND status = 'active'
            """, (car_id,))
            
            active_rentals = cursor.fetchone()[0]
            if active_rentals > 0:
                messagebox.showerror("Ошибка", 
                                f"Нельзя удалить автомобиль!\nНайдено {active_rentals} активных аренд.")
                return
            
            # 2. Удаляем связанные записи (в правильном порядке)
            # Сначала условия автомобиля
            cursor.execute("DELETE FROM CarConditions WHERE car_id = %s", (car_id,))
            
            # Затем аренды этого автомобиля
            cursor.execute("DELETE FROM Rentals WHERE car_id = %s", (car_id,))
            
            # И наконец сам автомобиль
            cursor.execute("DELETE FROM Cars WHERE car_id = %s", (car_id,))
            
            conn.commit()
            messagebox.showinfo("Успех", "Автомобиль и связанные данные успешно удалены!")
            
            # Обновляем отображение
            self.load_cars()
            self.load_rentals()
            
        except mysql.connector.Error as err:
            conn.rollback()
            messagebox.showerror("Ошибка БД", f"Ошибка при удалении:\n{err}")
        finally:
            if conn.is_connected():
                conn.close()
    
    def delete_client(self):
        """Удаление выбранного клиента"""
        selected = self.clients_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите клиента для удаления!")
            return
            
        client_id = self.clients_tree.item(selected[0])['values'][0]
        
        if not messagebox.askyesno("Подтверждение", 
                                f"Удалить клиента ID {client_id}? Это также удалит все его аренды."):
            return
            
        conn = get_db_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            
            # Сначала удаляем связанные аренды
            cursor.execute("DELETE FROM Rentals WHERE client_id = %s", (client_id,))
            
            # Затем удаляем клиента
            cursor.execute("DELETE FROM Clients WHERE client_id = %s", (client_id,))
            
            conn.commit()
            messagebox.showinfo("Успех", "Клиент и его аренды удалены!")
            self.load_clients()
            self.load_rentals()  # Обновляем список аренд
            
        except mysql.connector.Error as err:
            conn.rollback()
            messagebox.showerror("Ошибка", f"Не удалось удалить клиента:\n{err}")
        finally:
            conn.close()

    def complete_rental(self):
        """Завершает выбранную аренду"""
        selected = self.rentals_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите аренду для завершения!")
            return
            
        rental_id = self.rentals_tree.item(selected[0])['values'][0]
        
        conn = get_db_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            
            # Получаем car_id для обновления статуса авто
            cursor.execute("SELECT car_id FROM Rentals WHERE rental_id = %s", (rental_id,))
            car_id = cursor.fetchone()[0]
            
            # Завершаем аренду
            cursor.execute("""
                UPDATE Rentals 
                SET status = 'completed', actual_end_datetime = NOW()
                WHERE rental_id = %s
            """, (rental_id,))
            
            # Делаем авто доступным
            cursor.execute("UPDATE Cars SET is_available = TRUE WHERE car_id = %s", (car_id,))
            
            conn.commit()
            messagebox.showinfo("Успех", "Аренда завершена!")
            self.load_rentals()
            self.load_cars()
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Ошибка завершения аренды: {err}")
        finally:
            conn.close()

    # ===== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ =====
    def get_clients_list(self):
        """Возвращает список клиентов в формате 'ID - Фамилия Имя'"""
        conn = get_db_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT client_id, last_name, first_name 
                FROM Clients 
                ORDER BY last_name, first_name
            """)
            return [f"{row[0]} - {row[1]} {row[2]}" for row in cursor]
        finally:
            conn.close()

    def get_available_cars_list(self):
        """Возвращает список доступных авто"""
        conn = get_db_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.car_id, b.brand_name, m.model_name 
                FROM Cars c
                JOIN Models m ON c.model_id = m.model_id
                JOIN Brands b ON m.brand_id = b.brand_id
                WHERE c.is_available = TRUE
            """)
            return [f"{row[0]} - {row[1]} {row[2]}" for row in cursor]
        finally:
            conn.close()


if __name__ == "__main__":
    root = Tk()
    app = CarRentalSystem(root)
    root.mainloop()