import tkinter as tk
from tkinter import ttk, messagebox
from database.connection import get_db_connection

class CarRentalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система автопроката")
        self.root.geometry("1200x800")
        
        self.create_widgets()
        self.load_initial_data()
    
    def create_widgets(self):
        # Создаем вкладки
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
        # Таблица автомобилей
        columns = ("ID", "Марка", "Модель", "Год", "Номер", "Категория", "Статус", "Цена/день")
        self.cars_tree = ttk.Treeview(self.cars_frame, columns=columns, show="headings")
        
        for col in columns:
            self.cars_tree.heading(col, text=col)
            self.cars_tree.column(col, width=100)
        
        self.cars_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Кнопки управления
        btn_frame = tk.Frame(self.cars_frame)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Обновить", command=self.load_cars).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Добавить авто", command=self.add_car_dialog).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Изменить статус", command=self.change_car_status).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Удалить", command=self.delete_car).pack(side=tk.LEFT, padx=5)
    
    def create_clients_tab(self):
        # Таблица клиентов
        columns = ("ID", "Фамилия", "Имя", "Телефон", "Права", "Рейтинг")
        self.clients_tree = ttk.Treeview(self.clients_frame, columns=columns, show="headings")
        
        for col in columns:
            self.clients_tree.heading(col, text=col)
            self.clients_tree.column(col, width=120)
        
        self.clients_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Кнопки управления
        btn_frame = tk.Frame(self.clients_frame)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Обновить", command=self.load_clients).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Добавить клиента", command=self.add_client_dialog).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Черный список", command=self.toggle_blacklist).pack(side=tk.LEFT, padx=5)
    
    def create_rentals_tab(self):
        # Таблица аренд
        columns = ("ID", "Клиент", "Автомобиль", "Начало", "Конец", "Стоимость", "Статус")
        self.rentals_tree = ttk.Treeview(self.rentals_frame, columns=columns, show="headings")
        
        for col in columns:
            self.rentals_tree.heading(col, text=col)
            self.rentals_tree.column(col, width=120)
        
        self.rentals_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Кнопки управления
        btn_frame = tk.Frame(self.rentals_frame)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Обновить", command=self.load_rentals).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Новая аренда", command=self.new_rental_dialog).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Завершить аренду", command=self.complete_rental).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Отчет о повреждениях", command=self.report_damage).pack(side=tk.LEFT, padx=5)
    
    def create_reports_tab(self):
        # Отчеты
        report_frame = tk.Frame(self.reports_frame)
        report_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Button(report_frame, text="Доход по месяцам", command=self.generate_income_report).pack(pady=5)
        tk.Button(report_frame, text="Популярные автомобили", command=self.generate_popular_cars_report).pack(pady=5)
        tk.Button(report_frame, text="Активные аренды", command=self.generate_active_rentals_report).pack(pady=5)
        
        self.report_text = tk.Text(report_frame, height=20, wrap=tk.WORD)
        self.report_text.pack(fill=tk.BOTH, expand=True)
    
    def load_initial_data(self):
        self.load_cars()
        self.load_clients()
        self.load_rentals()
    
    # Далее идут методы для работы с базой данных и диалоговыми окнами
    # (приведу несколько ключевых методов, остальные можно реализовать аналогично)
    
    def load_cars(self):
        """Загружает список автомобилей из БД"""
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
            
            # Очищаем таблицу
            for item in self.cars_tree.get_children():
                self.cars_tree.delete(item)
            
            # Заполняем данными
            for row in cursor.fetchall():
                self.cars_tree.insert("", tk.END, values=row)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить автомобили: {e}")
        finally:
            conn.close()
    
    def add_car_dialog(self):
        """Диалоговое окно добавления автомобиля"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить автомобиль")
        
        # Поля формы
        tk.Label(dialog, text="Марка:").grid(row=0, column=0, padx=5, pady=5)
        brand_entry = tk.Entry(dialog)
        brand_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Добавьте остальные поля: модель, год, номер и т.д.
        
        # Кнопка сохранения
        tk.Button(dialog, text="Сохранить", command=lambda: self.save_car(
            brand_entry.get()
            # Добавьте остальные параметры
        )).grid(row=10, columnspan=2, pady=10)
    
    def save_car(self, brand):
        """Сохраняет новый автомобиль в БД"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO cars (brand, model, year, license_plate, category_id, status)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (brand, model, year, license_plate, category_id, 'available'))
            
            conn.commit()
            messagebox.showinfo("Успех", "Автомобиль успешно добавлен")
            self.load_cars()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить автомобиль: {e}")
        finally:
            conn.close()
    
    # Аналогично реализуйте методы для работы с клиентами и арендами
    
    def generate_income_report(self):
        """Генерирует отчет о доходах по месяцам"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT strftime('%Y-%m', r.start_date) as month,
                   COUNT(*) as rentals_count,
                   SUM(r.total_cost) as total_income
            FROM rentals r
            WHERE r.status = 'completed'
            GROUP BY strftime('%Y-%m', r.start_date)
            ORDER BY month
            ''')
            
            report = "Отчет о доходах по месяцам:\n\n"
            report += "{:<10} {:<15} {:<15}\n".format("Месяц", "Кол-во аренд", "Доход")
            report += "-"*40 + "\n"
            
            for row in cursor.fetchall():
                report += "{:<10} {:<15} {:<15.2f}\n".format(row[0], row[1], row[2])
            
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(tk.END, report)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сформировать отчет: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = CarRentalApp(root)
    root.mainloop()