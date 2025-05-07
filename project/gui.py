import mysql.connector
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime, timedelta
import logging
logging.basicConfig(level=logging.DEBUG, filename='rental.log')

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1201Lena_",
            database="car_rental",
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Ошибка", f"Не удалось подключиться к БД: {err}")
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
        self.cars_tree = ttk.Treeview(self.cars_tab, columns=("ID", "Марка", "Модель", "Год", "Цвет", "Пробег", "Цена", "Доступен"), show="headings")
        
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
        Button(control_frame, text="Добавить авто", command=self.show_add_car_dialog).pack(side=LEFT, padx=5)
        Button(control_frame, text="Удалить", command=self.delete_car).pack(side=LEFT, padx=5)
        
        # Загрузка данных
        self.load_cars()

    def load_cars(self):
        """Загружает данные об автомобилях"""
        conn = get_db_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.car_id, b.brand_name, m.model_name, m.year, c.color, 
                       c.mileage, c.daily_price, 
                       CASE WHEN c.is_available THEN 'Да' ELSE 'Нет' END
                FROM Cars c
                JOIN Models m ON c.model_id = m.model_id
                JOIN Brands b ON m.brand_id = b.brand_id
                ORDER BY c.car_id
            """)
            
            # Очищаем таблицу
            for row in self.cars_tree.get_children():
                self.cars_tree.delete(row)
            
            # Добавляем данные
            for row in cursor:
                self.cars_tree.insert("", END, values=row)
                
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Ошибка загрузки автомобилей: {err}")
        finally:
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
        """Загружает данные об арендах"""
        conn = get_db_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.rental_id, 
                       CONCAT(c.first_name, ' ', c.last_name),
                       CONCAT(b.brand_name, ' ', m.model_name),
                       DATE_FORMAT(r.start_datetime, '%Y-%m-%d %H:%i'),
                       DATE_FORMAT(r.planned_end_datetime, '%Y-%m-%d %H:%i'),
                       CASE 
                           WHEN r.status = 'active' THEN 'Активна'
                           WHEN r.status = 'completed' THEN 'Завершена'
                           ELSE r.status
                       END
                FROM Rentals r
                JOIN Clients c ON r.client_id = c.client_id
                JOIN Cars car ON r.car_id = car.car_id
                JOIN Models m ON car.model_id = m.model_id
                JOIN Brands b ON m.brand_id = b.brand_id
                ORDER BY r.rental_id DESC
            """)
            
            # Очищаем таблицу
            for row in self.rentals_tree.get_children():
                self.rentals_tree.delete(row)
            
            # Добавляем данные
            for row in cursor:
                self.rentals_tree.insert("", END, values=row)
                
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
        """Диалоговое окно добавления автомобиля"""
        dialog = Toplevel(self.root)
        dialog.title("Добавить автомобиль")
        dialog.geometry("400x400")
        
        # Получаем список марок и моделей
        brands = self.get_brands_list()
        models = self.get_models_list()
        fuel_types = self.get_fuel_types_list()
        
        # Поля формы
        Label(dialog, text="Марка:").grid(row=0, column=0, padx=10, pady=5, sticky=W)
        brand_combobox = ttk.Combobox(dialog, values=brands, state="readonly")
        brand_combobox.grid(row=0, column=1, padx=10, pady=5, sticky=EW)
        if brands: brand_combobox.current(0)
        
        Label(dialog, text="Модель:").grid(row=1, column=0, padx=10, pady=5, sticky=W)
        model_combobox = ttk.Combobox(dialog, values=models, state="readonly")
        model_combobox.grid(row=1, column=1, padx=10, pady=5, sticky=EW)
        if models: model_combobox.current(0)
        
        Label(dialog, text="Тип топлива:").grid(row=2, column=0, padx=10, pady=5, sticky=W)
        fuel_combobox = ttk.Combobox(dialog, values=fuel_types, state="readonly")
        fuel_combobox.grid(row=2, column=1, padx=10, pady=5, sticky=EW)
        if fuel_types: fuel_combobox.current(0)
        
        Label(dialog, text="Год выпуска:").grid(row=3, column=0, padx=10, pady=5, sticky=W)
        year_entry = Entry(dialog)
        year_entry.grid(row=3, column=1, padx=10, pady=5, sticky=EW)
        
        Label(dialog, text="Цвет:").grid(row=4, column=0, padx=10, pady=5, sticky=W)
        color_entry = Entry(dialog)
        color_entry.grid(row=4, column=1, padx=10, pady=5, sticky=EW)
        
        Label(dialog, text="Пробег:").grid(row=5, column=0, padx=10, pady=5, sticky=W)
        mileage_entry = Entry(dialog)
        mileage_entry.grid(row=5, column=1, padx=10, pady=5, sticky=EW)
        
        Label(dialog, text="Цена/день:").grid(row=6, column=0, padx=10, pady=5, sticky=W)
        price_entry = Entry(dialog)
        price_entry.grid(row=6, column=1, padx=10, pady=5, sticky=EW)
        
        Button(dialog, text="Добавить", command=lambda: self.add_car(
            brand_combobox.get(),
            model_combobox.get(),
            fuel_combobox.get(),
            year_entry.get(),
            color_entry.get(),
            mileage_entry.get(),
            price_entry.get()
        )).grid(row=7, columnspan=2, pady=10)

    def add_car(self, brand_str, model_str, fuel_str, year, color, mileage, price):
        """Добавляет новый автомобиль в БД"""
        try:
            brand_id = int(brand_str.split(' - ')[0])
            model_id = int(model_str.split(' - ')[0])
            fuel_id = int(fuel_str.split(' - ')[0])
            year = int(year)
            mileage = int(mileage)
            price = float(price)
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте правильность введенных данных!")
            return
            
        conn = get_db_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Cars (model_id, fuel_id, color, mileage, daily_price, is_available)
                VALUES (%s, %s, %s, %s, %s, TRUE)
            """, (model_id, fuel_id, color, mileage, price))
            
            conn.commit()
            messagebox.showinfo("Успех", "Автомобиль добавлен!")
            self.load_cars()
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Ошибка добавления автомобиля: {err}")
        finally:
            conn.close()

    def delete_car(self):
        """Удаляет выбранный автомобиль"""
        selected = self.cars_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите автомобиль для удаления!")
            return
            
        car_id = self.cars_tree.item(selected[0])['values'][0]
        
        if not messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот автомобиль?"):
            return
            
        conn = get_db_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Cars WHERE car_id = %s", (car_id,))
            conn.commit()
            messagebox.showinfo("Успех", "Автомобиль удален!")
            self.load_cars()
        except mysql.connector.Error as err:
            messagebox.showerror("Ошибка", f"Ошибка удаления автомобиля: {err}")
        finally:
            conn.close()

    def get_brands_list(self):
        """Возвращает список марок автомобилей"""
        conn = get_db_connection()
        if not conn:
            return []
            
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT brand_id, brand_name FROM Brands ORDER BY brand_name")
            return [f"{row[0]} - {row[1]}" for row in cursor]
        except:
            return []
        finally:
            conn.close()

    def get_models_list(self):
        """Возвращает список моделей автомобилей"""
        conn = get_db_connection()
        if not conn:
            return []
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.model_id, CONCAT(b.brand_name, ' ', m.model_name)
                FROM Models m
                JOIN Brands b ON m.brand_id = b.brand_id
                ORDER BY b.brand_name, m.model_name
            """)
            return [f"{row[0]} - {row[1]}" for row in cursor]
        except:
            return []
        finally:
            conn.close()

    def get_fuel_types_list(self):
        """Возвращает список типов топлива"""
        conn = get_db_connection()
        if not conn:
            return []
            
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT fuel_id, fuel_name FROM FuelTypes ORDER BY fuel_name")
            return [f"{row[0]} - {row[1]}" for row in cursor]
        except:
            return []
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
                    
    def delete_car(self):
        selected_index = self.car_listbox.curselection()  # Получаем индекс выбранного автомобиля
        if selected_index:
            # Удаляем автомобиль из списка и из Listbox
            index = selected_index[0]
            self.car_listbox.delete(index)  # Удаляем из интерфейса
            del self.cars[index]  # Удаляем из внутреннего списка
            print(f"Автомобиль '{self.cars[index]}' удален.")
        else:
            print("Пожалуйста, выберите автомобиль для удаления.")


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