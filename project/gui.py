import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
from database.connection import get_db_connection

class CarRentalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система автопроката")
        self.root.geometry("1200x800")
        
        self.create_widgets()
        self.load_initial_data()
    
    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка автомобилей
        self.cars_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.cars_frame, text="Автомобили")
        self.create_cars_tab()
        
        # Вкладка клиентов
        self.clients_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.clients_frame, text="Клиенты")
        self.create_clients_tab()
        
        # Вкладка аренд
        self.rentals_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.rentals_frame, text="Аренды")
        self.create_rentals_tab()
        
        # Вкладка отчетов
        self.reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_frame, text="Отчеты")
        self.create_reports_tab()
    
    def create_cars_tab(self):
        columns = ("ID", "Марка", "Модель", "Год", "Номер", "Категория", "Статус", "Цена/день")
        self.cars_tree = ttk.Treeview(self.cars_frame, columns=columns, show="headings")
        
        for col in columns:
            self.cars_tree.heading(col, text=col)
            self.cars_tree.column(col, width=100)
        
        self.cars_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        btn_frame = tk.Frame(self.cars_frame)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Обновить", command=self.load_cars).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Добавить авто", command=self.add_car_dialog).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Изменить статус", command=self.change_car_status_dialog).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Удалить", command=self.delete_car).pack(side=tk.LEFT, padx=5)
    
    def create_clients_tab(self):
        columns = ("ID", "Фамилия", "Имя", "Телефон", "Права", "Рейтинг", "Черный список")
        self.clients_tree = ttk.Treeview(self.clients_frame, columns=columns, show="headings")
        
        for col in columns:
            self.clients_tree.heading(col, text=col)
            self.clients_tree.column(col, width=120)
        
        self.clients_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        btn_frame = tk.Frame(self.clients_frame)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Обновить", command=self.load_clients).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Добавить клиента", command=self.add_client_dialog).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Добавить в ЧС", command=self.toggle_blacklist).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Поиск", command=self.search_clients_dialog).pack(side=tk.LEFT, padx=5)
    
    def create_rentals_tab(self):
        columns = ("ID", "Клиент", "Автомобиль", "Начало", "Конец", "Стоимость", "Статус")
        self.rentals_tree = ttk.Treeview(self.rentals_frame, columns=columns, show="headings")
        
        for col in columns:
            self.rentals_tree.heading(col, text=col)
            self.rentals_tree.column(col, width=120)
        
        self.rentals_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        btn_frame = tk.Frame(self.rentals_frame)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Обновить", command=self.load_rentals).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Новая аренда", command=self.new_rental_dialog).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Завершить аренду", command=self.complete_rental).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Отменить аренду", command=self.cancel_rental).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Отчет о повреждениях", command=self.report_damage_dialog).pack(side=tk.LEFT, padx=5)
    
    def create_reports_tab(self):
        report_frame = tk.Frame(self.reports_frame)
        report_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Button(report_frame, text="Доход по месяцам", command=self.generate_income_report).pack(pady=5)
        tk.Button(report_frame, text="Популярные автомобили", command=self.generate_popular_cars_report).pack(pady=5)
        tk.Button(report_frame, text="Активные аренды", command=self.generate_active_rentals_report).pack(pady=5)
        tk.Button(report_frame, text="Автомобили в ремонте", command=self.generate_maintenance_report).pack(pady=5)
        
        self.report_text = tk.Text(report_frame, height=20, wrap=tk.WORD)
        self.report_text.pack(fill=tk.BOTH, expand=True)
    
    def load_initial_data(self):
        self.load_cars()
        self.load_clients()
        self.load_rentals()
    
    # ========== Методы для работы с автомобилями ==========
    def load_cars(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT c.car_id, c.brand, c.model, c.year, c.license_plate, 
                   cat.name, c.status, cat.daily_rate
            FROM cars c
            JOIN categories cat ON c.category_id = cat.category_id
            ORDER BY c.car_id
            ''')
            
            for item in self.cars_tree.get_children():
                self.cars_tree.delete(item)
            
            for row in cursor.fetchall():
                self.cars_tree.insert("", tk.END, values=row)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить автомобили: {e}")
        finally:
            conn.close()
    
    def add_car_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить автомобиль")
        dialog.geometry("400x300")
        
        # Поля формы
        tk.Label(dialog, text="Марка:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        brand_entry = tk.Entry(dialog)
        brand_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(dialog, text="Модель:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        model_entry = tk.Entry(dialog)
        model_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(dialog, text="Год:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        year_entry = tk.Entry(dialog)
        year_entry.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(dialog, text="Номер:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        license_entry = tk.Entry(dialog)
        license_entry.grid(row=3, column=1, padx=5, pady=5)
        
        tk.Label(dialog, text="Категория:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT category_id, name FROM categories")
        categories = cursor.fetchall()
        conn.close()
        
        category_var = tk.StringVar(dialog)
        category_dropdown = ttk.Combobox(dialog, textvariable=category_var, state="readonly")
        category_dropdown['values'] = [f"{cat[0]} - {cat[1]}" for cat in categories]
        if categories:
            category_dropdown.current(0)
        category_dropdown.grid(row=4, column=1, padx=5, pady=5)
        
        def save():
            try:
                category_id = int(category_var.get().split(" - ")[0])
                conn = get_db_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                INSERT INTO cars (brand, model, year, license_plate, category_id, status)
                VALUES (?, ?, ?, ?, ?, 'available')
                ''', (
                    brand_entry.get(),
                    model_entry.get(),
                    int(year_entry.get()),
                    license_entry.get(),
                    category_id
                ))
                
                conn.commit()
                messagebox.showinfo("Успех", "Автомобиль успешно добавлен")
                self.load_cars()
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить автомобиль: {e}")
            finally:
                conn.close()
        
        tk.Button(dialog, text="Сохранить", command=save).grid(row=5, columnspan=2, pady=10)
    
    def change_car_status_dialog(self):
        selected = self.cars_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите автомобиль из списка")
            return
        
        car_id = self.cars_tree.item(selected[0])['values'][0]
        current_status = self.cars_tree.item(selected[0])['values'][6]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Изменить статус автомобиля")
        
        tk.Label(dialog, text=f"Текущий статус: {current_status}").pack(padx=10, pady=5)
        
        status_var = tk.StringVar(dialog)
        status_var.set(current_status)
        
        statuses = ['available', 'rented', 'maintenance']
        if current_status not in statuses:
            statuses.append(current_status)
        
        for status in statuses:
            tk.Radiobutton(dialog, text=status, variable=status_var, value=status).pack(anchor="w")
        
        def save():
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                UPDATE cars SET status = ? WHERE car_id = ?
                ''', (status_var.get(), car_id))
                
                conn.commit()
                messagebox.showinfo("Успех", "Статус автомобиля обновлен")
                self.load_cars()
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось изменить статус: {e}")
            finally:
                conn.close()
        
        tk.Button(dialog, text="Сохранить", command=save).pack(pady=10)
    
    def delete_car(self):
        selected = self.cars_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите автомобиль из списка")
            return
        
        car_id = self.cars_tree.item(selected[0])['values'][0]
        
        if not messagebox.askyesno("Подтверждение", "Удалить выбранный автомобиль?"):
            return
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Проверяем, нет ли активных аренд
            cursor.execute('''
            SELECT COUNT(*) FROM rentals 
            WHERE car_id = ? AND status IN ('reserved', 'active')
            ''', (car_id,))
            
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Ошибка", "Нельзя удалить автомобиль с активными арендами")
                return
            
            cursor.execute('DELETE FROM cars WHERE car_id = ?', (car_id,))
            conn.commit()
            messagebox.showinfo("Успех", "Автомобиль удален")
            self.load_cars()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить автомобиль: {e}")
        finally:
            conn.close()
    
    # ========== Методы для работы с клиентами ==========
    def load_clients(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT client_id, last_name, first_name, phone, driver_license, rating, 
                   CASE WHEN blacklisted THEN 'Да' ELSE 'Нет' END as blacklist
            FROM clients
            ORDER BY last_name, first_name
            ''')
            
            for item in self.clients_tree.get_children():
                self.clients_tree.delete(item)
            
            for row in cursor.fetchall():
                self.clients_tree.insert("", tk.END, values=row)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить клиентов: {e}")
        finally:
            conn.close()
    
    def add_client_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить клиента")
        dialog.geometry("400x400")
        
        # Поля формы
        fields = [
            ("Фамилия:", "last_name"),
            ("Имя:", "first_name"),
            ("Дата рождения (ГГГГ-ММ-ДД):", "birth_date"),
            ("Паспорт:", "passport"),
            ("Водительские права:", "license"),
            ("Телефон:", "phone"),
            ("Email:", "email")
        ]
        
        entries = {}
        for i, (label, name) in enumerate(fields):
            tk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            entry = tk.Entry(dialog)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[name] = entry
        
        def save():
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                INSERT INTO clients 
                (last_name, first_name, birth_date, passport_number, driver_license, phone, email, registration_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, date('now'))
                ''', (
                    entries['last_name'].get(),
                    entries['first_name'].get(),
                    entries['birth_date'].get(),
                    entries['passport'].get(),
                    entries['license'].get(),
                    entries['phone'].get(),
                    entries['email'].get()
                ))
                
                conn.commit()
                messagebox.showinfo("Успех", "Клиент успешно добавлен")
                self.load_clients()
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить клиента: {e}")
            finally:
                conn.close()
        
        tk.Button(dialog, text="Сохранить", command=save).grid(row=len(fields), columnspan=2, pady=10)
    
    def toggle_blacklist(self):
        selected = self.clients_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите клиента из списка")
            return
        
        client_id = self.clients_tree.item(selected[0])['values'][0]
        current_status = self.clients_tree.item(selected[0])['values'][6]
        
        new_status = current_status == 'Нет'
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            UPDATE clients SET blacklisted = ? WHERE client_id = ?
            ''', (new_status, client_id))
            
            conn.commit()
            messagebox.showinfo("Успех", "Статус клиента обновлен")
            self.load_clients()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось изменить статус: {e}")
        finally:
            conn.close()
    
    def search_clients_dialog(self):
        search_term = simpledialog.askstring("Поиск клиентов", "Введите фамилию или имя:")
        if not search_term:
            return
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT client_id, last_name, first_name, phone, driver_license, rating, 
                   CASE WHEN blacklisted THEN 'Да' ELSE 'Нет' END as blacklist
            FROM clients
            WHERE last_name LIKE ? OR first_name LIKE ?
            ORDER BY last_name, first_name
            ''', (f"%{search_term}%", f"%{search_term}%"))
            
            for item in self.clients_tree.get_children():
                self.clients_tree.delete(item)
            
            for row in cursor.fetchall():
                self.clients_tree.insert("", tk.END, values=row)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить поиск: {e}")
        finally:
            conn.close()
    
    # ========== Методы для работы с арендами ==========
    def load_rentals(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT r.rental_id, 
                   c.last_name || ' ' || c.first_name as client,
                   car.brand || ' ' || car.model as car,
                   r.start_date, r.end_date, r.total_cost, r.status
            FROM rentals r
            JOIN clients c ON r.client_id = c.client_id
            JOIN cars car ON r.car_id = car.car_id
            ORDER BY r.start_date DESC
            ''')
            
            for item in self.rentals_tree.get_children():
                self.rentals_tree.delete(item)
            
            for row in cursor.fetchall():
                self.rentals_tree.insert("", tk.END, values=row)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить аренды: {e}")
        finally:
            conn.close()
    
    def new_rental_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Новая аренда")
        dialog.geometry("600x500")
        
        # Выбор клиента
        tk.Label(dialog, text="Клиент:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT client_id, last_name || ' ' || first_name as name 
        FROM clients 
        WHERE blacklisted = 0
        ORDER BY last_name
        ''')
        clients = cursor.fetchall()
        
        client_var = tk.StringVar(dialog)
        client_dropdown = ttk.Combobox(dialog, textvariable=client_var, state="readonly")
        client_dropdown['values'] = [f"{c[0]} - {c[1]}" for c in clients]
        if clients:
            client_dropdown.current(0)
        client_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Выбор автомобиля
        tk.Label(dialog, text="Автомобиль:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        
        cursor.execute('''
        SELECT c.car_id, c.brand || ' ' || c.model || ' (' || cat.name || ')' as car_info
        FROM cars c
        JOIN categories cat ON c.category_id = cat.category_id
        WHERE c.status = 'available'
        ''')
        cars = cursor.fetchall()
        
        car_var = tk.StringVar(dialog)
        car_dropdown = ttk.Combobox(dialog, textvariable=car_var, state="readonly")
        car_dropdown['values'] = [f"{c[0]} - {c[1]}" for c in cars]
        if cars:
            car_dropdown.current(0)
        car_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Даты аренды
        tk.Label(dialog, text="Дата начала (ГГГГ-ММ-ДД):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        start_date_entry = tk.Entry(dialog)
        start_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        start_date_entry.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(dialog, text="Дата окончания (ГГГГ-ММ-ДД):").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        end_date_entry = tk.Entry(dialog)
        end_date_entry.insert(0, (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'))
        end_date_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Дополнительные услуги
        tk.Label(dialog, text="Дополнительные услуги:").grid(row=4, column=0, padx=5, pady=5, sticky="ne")
        
        services_frame = tk.Frame(dialog)
        services_frame.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        
        cursor.execute('SELECT service_id, name, price FROM services')
        services = cursor.fetchall()
        conn.close()
        
        self.service_vars = {}
        for i, (service_id, name, price) in enumerate(services):
            var = tk.IntVar()
            cb = tk.Checkbutton(services_frame, text=f"{name} ({price} руб.)", variable=var)
            cb.pack(anchor="w")
            self.service_vars[service_id] = var
        
        def calculate_cost():
            try:
                car_id = int(car_var.get().split(" - ")[0])
                start_date = datetime.strptime(start_date_entry.get(), '%Y-%m-%d')
                end_date = datetime.strptime(end_date_entry.get(), '%Y-%m-%d')
                
                if end_date <= start_date:
                    messagebox.showerror("Ошибка", "Дата окончания должна быть позже даты начала")
                    return
                
                days = (end_date - start_date).days
                
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Получаем стоимость аренды автомобиля
                cursor.execute('''
                SELECT cat.daily_rate, cat.deposit_amount 
                FROM cars c
                JOIN categories cat ON c.category_id = cat.category_id
                WHERE c.car_id = ?
                ''', (car_id,))
                
                daily_rate, deposit = cursor.fetchone()
                base_cost = daily_rate * days
                
                # Добавляем стоимость услуг
                services_cost = 0
                for service_id, var in self.service_vars.items():
                    if var.get() == 1:
                        cursor.execute('SELECT price FROM services WHERE service_id = ?', (service_id,))
                        services_cost += cursor.fetchone()[0] * days
                
                total_cost = base_cost + services_cost
                
                messagebox.showinfo("Стоимость", 
                    f"Базовая стоимость: {base_cost:.2f} руб.\n"
                    f"Стоимость услуг: {services_cost:.2f} руб.\n"
                    f"Депозит: {deposit:.2f} руб.\n"
                    f"Итого: {total_cost:.2f} руб.")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось рассчитать стоимость: {e}")
            finally:
                conn.close()
        
        def create_rental():
            try:
                client_id = int(client_var.get().split(" - ")[0])
                car_id = int(car_var.get().split(" - ")[0])
                start_date = start_date_entry.get()
                end_date = end_date_entry.get()
                
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Получаем стоимость аренды
                cursor.execute('''
                SELECT cat.daily_rate, cat.deposit_amount 
                FROM cars c
                JOIN categories cat ON c.category_id = cat.category_id
                WHERE c.car_id = ?
                ''', (car_id,))
                
                daily_rate, deposit = cursor.fetchone()
                days = (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days
                base_cost = daily_rate * days
                
                # Добавляем стоимость услуг
                services_cost = 0
                for service_id, var in self.service_vars.items():
                    if var.get() == 1:
                        cursor.execute('SELECT price FROM services WHERE service_id = ?', (service_id,))
                        services_cost += cursor.fetchone()[0] * days
                
                total_cost = base_cost + services_cost
                
                # Создаем аренду
                cursor.execute('''
                INSERT INTO rentals 
                (client_id, car_id, start_date, end_date, total_cost, deposit_amount, status, employee_id)
                VALUES (?, ?, ?, ?, ?, ?, 'reserved', 1)
                ''', (client_id, car_id, start_date, end_date, total_cost, deposit))
                
                rental_id = cursor.lastrowid
                
                # Добавляем услуги
                for service_id, var in self.service_vars.items():
                    if var.get() == 1:
                        cursor.execute('''
                        INSERT INTO rental_services (rental_id, service_id, quantity)
                        VALUES (?, ?, 1)
                        ''', (rental_id, service_id))
                
                # Обновляем статус автомобиля
                cursor.execute('''
                UPDATE cars SET status = 'reserved' WHERE car_id = ?
                ''', (car_id,))
                
                conn.commit()
                messagebox.showinfo("Успех", "Аренда успешно создана")
                self.load_rentals()
                self.load_cars()
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать аренду: {e}")
            finally:
                conn.close()
        
        btn_frame = tk.Frame(dialog)
        btn_frame.grid(row=5, columnspan=2, pady=10)
        
        tk.Button(btn_frame, text="Рассчитать стоимость", command=calculate_cost).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Создать аренду", command=create_rental).pack(side=tk.LEFT, padx=5)
    
    def complete_rental(self):
        selected = self.rentals_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите аренду из списка")
            return
        
        rental_id = self.rentals_tree.item(selected[0])['values'][0]
        status = self.rentals_tree.item(selected[0])['values'][6]
        
        if status != 'active':
            messagebox.showwarning("Внимание", "Можно завершить только активные аренды")
            return
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Получаем информацию об аренде
            cursor.execute('''
            SELECT car_id, end_date, total_cost 
            FROM rentals 
            WHERE rental_id = ?
            ''', (rental_id,))
            
            car_id, planned_end_date, planned_cost = cursor.fetchone()
            
            # Запрашиваем фактическую дату возврата
            actual_end_date = simpledialog.askstring(
                "Завершение аренды", 
                "Введите фактическую дату возврата (ГГГГ-ММ-ДД):",
                initialvalue=datetime.now().strftime('%Y-%m-%d'))
            
            if not actual_end_date:
                return
            
            # Пересчитываем стоимость, если вернули раньше/позже
            planned_end = datetime.strptime(planned_end_date, '%Y-%m-%d')
            actual_end = datetime.strptime(actual_end_date, '%Y-%m-%d')
            
            if actual_end > planned_end:
                # Если с опозданием - добавляем штраф
                extra_days = (actual_end - planned_end).days
                cursor.execute('''
                SELECT daily_rate FROM cars c
                JOIN categories cat ON c.category_id = cat.category_id
                WHERE c.car_id = ?
                ''', (car_id,))
                
                daily_rate = cursor.fetchone()[0]
                penalty = daily_rate * extra_days * 1.5  # Штраф 50%
                final_cost = planned_cost + penalty
                
                messagebox.showwarning("Опоздание", 
                    f"Клиент опоздал на {extra_days} дней.\n"
                    f"Штраф: {penalty:.2f} руб.\n"
                    f"Итоговая стоимость: {final_cost:.2f} руб.")
            else:
                final_cost = planned_cost
            
            # Обновляем аренду
            cursor.execute('''
            UPDATE rentals SET 
            status = 'completed',
            actual_end_date = ?,
            total_cost = ?
            WHERE rental_id = ?
            ''', (actual_end_date, final_cost, rental_id))
            
            # Возвращаем автомобиль в доступные
            cursor.execute('''
            UPDATE cars SET status = 'available' WHERE car_id = ?
            ''', (car_id,))
            
            conn.commit()
            messagebox.showinfo("Успех", "Аренда успешно завершена")
            self.load_rentals()
            self.load_cars()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось завершить аренду: {e}")
        finally:
            conn.close()
    
    def cancel_rental(self):
        selected = self.rentals_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите аренду из списка")
            return
        
        rental_id = self.rentals_tree.item(selected[0])['values'][0]
        status = self.rentals_tree.item(selected[0])['values'][6]
        
        if status not in ['reserved', 'active']:
            messagebox.showwarning("Внимание", "Можно отменить только резервирования или активные аренды")
            return
        
        if not messagebox.askyesno("Подтверждение", "Отменить выбранную аренду?"):
            return
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Получаем car_id для обновления статуса автомобиля
            cursor.execute('SELECT car_id FROM rentals WHERE rental_id = ?', (rental_id,))
            car_id = cursor.fetchone()[0]
            
            # Отменяем аренду
            cursor.execute('''
            UPDATE rentals SET 
            status = 'cancelled',
            actual_end_date = date('now')
            WHERE rental_id = ?
            ''', (rental_id,))
            
            # Возвращаем автомобиль в доступные
            cursor.execute('''
            UPDATE cars SET status = 'available' WHERE car_id = ?
            ''', (car_id,))
            
            conn.commit()
            messagebox.showinfo("Успех", "Аренда отменена")
            self.load_rentals()
            self.load_cars()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось отменить аренду: {e}")
        finally:
            conn.close()
    
    def report_damage_dialog(self):
        selected = self.rentals_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите аренду из списка")
            return
        
        rental_id = self.rentals_tree.item(selected[0])['values'][0]
        status = self.rentals_tree.item(selected[0])['values'][6]
        
        if status not in ['completed', 'overdue']:
            messagebox.showwarning("Внимание", "Можно сообщить о повреждениях только для завершенных аренд")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Отчет о повреждениях")
        dialog.geometry("400x300")
        
        tk.Label(dialog, text="Описание повреждения:").pack(padx=10, pady=5)
        damage_desc = tk.Text(dialog, height=5, width=40)
        damage_desc.pack(padx=10, pady=5)
        
        tk.Label(dialog, text="Стоимость ремонта:").pack(padx=10, pady=5)
        repair_cost = tk.Entry(dialog)
        repair_cost.pack(padx=10, pady=5)
        
        def submit():
            try:
                cost = float(repair_cost.get())
                if cost <= 0:
                    raise ValueError("Стоимость должна быть положительной")
                
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Получаем car_id из аренды
                cursor.execute('SELECT car_id FROM rentals WHERE rental_id = ?', (rental_id,))
                car_id = cursor.fetchone()[0]
                
                # Добавляем повреждение
                cursor.execute('''
                INSERT INTO damages 
                (rental_id, car_id, description, repair_cost, reported_date, status, employee_id)
                VALUES (?, ?, ?, ?, date('now'), 'reported', 1)
                ''', (rental_id, car_id, damage_desc.get("1.0", tk.END).strip(), cost))
                
                # Если есть депозит, вычитаем из него стоимость ремонта
                cursor.execute('''
                UPDATE rentals SET 
                deposit_amount = deposit_amount - ?
                WHERE rental_id = ? AND deposit_amount >= ?
                ''', (cost, rental_id, cost))
                
                conn.commit()
                messagebox.showinfo("Успех", "Повреждение зарегистрировано")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось зарегистрировать повреждение: {e}")
            finally:
                conn.close()
        
        tk.Button(dialog, text="Отправить отчет", command=submit).pack(pady=10)
    
    # ========== Методы для отчетов ==========
    def generate_income_report(self):
        try:
            conn = get_db_connection()
            cursor