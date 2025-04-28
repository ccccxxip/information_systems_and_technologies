import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class StoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Магазин - система учета продаж")
        self.root.geometry("1000x700")
        
        # Подключение к БД
        self.conn = sqlite3.connect('store.db')
        self.create_tables()
        self.add_sample_data()
        
        # Создание вкладок
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)
        
        # Вкладка товаров
        self.products_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.products_tab, text='Товары')
        self.setup_products_tab()
        
        # Вкладка новой продажи
        self.sale_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.sale_tab, text='Новая продажа')
        self.setup_sale_tab()
        
        # Вкладка отчетов
        self.reports_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_tab, text='Отчеты')
        self.setup_reports_tab()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Таблица категорий
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name TEXT NOT NULL UNIQUE
            )
        ''')
        
        # Таблица товаров
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                category_id INTEGER NOT NULL,
                price REAL NOT NULL,
                quantity_in_stock INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (category_id) REFERENCES categories(category_id)
            )
        ''')
        
        # Таблица продаж
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                total_amount REAL NOT NULL
            )
        ''')
        
        # Таблица позиций в продаже
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sale_items (
                sale_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price_per_unit REAL NOT NULL,
                total_price REAL NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales(sale_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        ''')
        
        self.conn.commit()
    
    def add_sample_data(self):
        cursor = self.conn.cursor()
        
        # Добавляем категории, если их нет
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            categories = ["Электроника", "Одежда", "Продукты", "Книги"]
            for cat in categories:
                cursor.execute("INSERT INTO categories (category_name) VALUES (?)", (cat,))
        
        # Добавляем товары, если их нет
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            products = [
                ("Ноутбук", "Электроника", 999.99, 10),
                ("Смартфон", "Электроника", 499.99, 15),
                ("Наушники", "Электроника", 99.99, 20),
                ("Футболка", "Одежда", 19.99, 50),
                ("Джинсы", "Одежда", 49.99, 30),
                ("Хлеб", "Продукты", 1.99, 100),
                ("Молоко", "Продукты", 2.49, 80),
                ("Python для начинающих", "Книги", 29.99, 25)
            ]
            for name, cat, price, qty in products:
                cursor.execute("SELECT category_id FROM categories WHERE category_name=?", (cat,))
                cat_id = cursor.fetchone()[0]
                cursor.execute('''
                    INSERT INTO products (product_name, category_id, price, quantity_in_stock)
                    VALUES (?, ?, ?, ?)
                ''', (name, cat_id, price, qty))
        
        self.conn.commit()
    
    def setup_products_tab(self):
        # Фрейм для добавления/редактирования товара
        edit_frame = ttk.LabelFrame(self.products_tab, text="Добавить/Изменить товар")
        edit_frame.pack(pady=10, padx=10, fill="x")
        
        # Поля ввода
        ttk.Label(edit_frame, text="Название:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.product_name_entry = ttk.Entry(edit_frame)
        self.product_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="we")
        
        ttk.Label(edit_frame, text="Категория:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.category_combobox = ttk.Combobox(edit_frame, state="readonly")
        self.category_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="we")
        self.load_categories()
        
        ttk.Label(edit_frame, text="Цена:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.price_entry = ttk.Entry(edit_frame)
        self.price_entry.grid(row=2, column=1, padx=5, pady=5, sticky="we")
        
        ttk.Label(edit_frame, text="Количество:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.quantity_entry = ttk.Entry(edit_frame)
        self.quantity_entry.grid(row=3, column=1, padx=5, pady=5, sticky="we")
        
        # Кнопки управления
        button_frame = ttk.Frame(edit_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Добавить", command=self.add_product).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Обновить", command=self.update_product).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Удалить", command=self.delete_product).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Очистить", command=self.clear_product_fields).pack(side="left", padx=5)
        
        # Таблица товаров
        self.products_tree = ttk.Treeview(
            self.products_tab, 
            columns=("ID", "Название", "Категория", "Цена", "Количество"), 
            show="headings"
        )
        
        # Настройка столбцов
        self.products_tree.heading("ID", text="ID")
        self.products_tree.heading("Название", text="Название")
        self.products_tree.heading("Категория", text="Категория")
        self.products_tree.heading("Цена", text="Цена")
        self.products_tree.heading("Количество", text="Количество")
        
        self.products_tree.column("ID", width=50, anchor="center")
        self.products_tree.column("Название", width=200, anchor="w")
        self.products_tree.column("Категория", width=150, anchor="w")
        self.products_tree.column("Цена", width=100, anchor="e")
        self.products_tree.column("Количество", width=100, anchor="center")
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(self.products_tab, orient="vertical", command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.products_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Загрузка данных
        self.load_products()
        
        # Привязка события выбора товара
        self.products_tree.bind("<<TreeviewSelect>>", self.on_product_select)
    
    def load_categories(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT category_name FROM categories ORDER BY category_name")
        categories = [row[0] for row in cursor.fetchall()]
        self.category_combobox["values"] = categories
    
    def load_products(self):
        # Очистка таблицы
        for row in self.products_tree.get_children():
            self.products_tree.delete(row)
        
        # Загрузка данных
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT p.product_id, p.product_name, c.category_name, p.price, p.quantity_in_stock 
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            ORDER BY p.product_name
        ''')
        
        for product in cursor.fetchall():
            self.products_tree.insert("", "end", values=product)
    
    def on_product_select(self, event):
        selected = self.products_tree.focus()
        if selected:
            product = self.products_tree.item(selected, "values")
            self.clear_product_fields()
            
            self.product_name_entry.insert(0, product[1])
            self.category_combobox.set(product[2])
            self.price_entry.insert(0, product[3])
            self.quantity_entry.insert(0, product[4])
    
    def clear_product_fields(self):
        self.product_name_entry.delete(0, tk.END)
        self.category_combobox.set('')
        self.price_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.products_tree.selection_remove(self.products_tree.selection())
    
    def validate_product_fields(self):
        name = self.product_name_entry.get().strip()
        category = self.category_combobox.get().strip()
        price = self.price_entry.get().strip()
        quantity = self.quantity_entry.get().strip()
        
        if not name:
            messagebox.showerror("Ошибка", "Введите название товара!")
            return False
        
        if not category:
            messagebox.showerror("Ошибка", "Выберите категорию!")
            return False
        
        try:
            float(price)
        except ValueError:
            messagebox.showerror("Ошибка", "Цена должна быть числом!")
            return False
        
        try:
            int(quantity)
        except ValueError:
            messagebox.showerror("Ошибка", "Количество должно быть целым числом!")
            return False
        
        return True
    
    def add_product(self):
        if not self.validate_product_fields():
            return
        
        name = self.product_name_entry.get().strip()
        category = self.category_combobox.get().strip()
        price = float(self.price_entry.get().strip())
        quantity = int(self.quantity_entry.get().strip())
        
        try:
            cursor = self.conn.cursor()
            
            # Проверяем, есть ли уже товар с таким названием
            cursor.execute("SELECT product_id FROM products WHERE product_name=?", (name,))
            existing_product = cursor.fetchone()
            
            if existing_product:
                messagebox.showerror("Ошибка", "Товар с таким названием уже существует!")
                return
            
            # Получаем ID категории
            cursor.execute("SELECT category_id FROM categories WHERE category_name=?", (category,))
            category_id = cursor.fetchone()[0]
            
            # Добавляем товар
            cursor.execute('''
                INSERT INTO products (product_name, category_id, price, quantity_in_stock)
                VALUES (?, ?, ?, ?)
            ''', (name, category_id, price, quantity))
            
            self.conn.commit()
            self.load_products()
            self.clear_product_fields()
            messagebox.showinfo("Успех", "Товар успешно добавлен!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить товар: {str(e)}")
    
    def update_product(self):
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите товар для обновления!")
            return
        
        if not self.validate_product_fields():
            return
        
        product_id = self.products_tree.item(selected, "values")[0]
        name = self.product_name_entry.get().strip()
        category = self.category_combobox.get().strip()
        price = float(self.price_entry.get().strip())
        quantity = int(self.quantity_entry.get().strip())
        
        try:
            cursor = self.conn.cursor()
            
            # Проверяем, есть ли уже товар с таким названием (кроме текущего)
            cursor.execute("SELECT product_id FROM products WHERE product_name=? AND product_id!=?", (name, product_id))
            if cursor.fetchone():
                messagebox.showerror("Ошибка", "Товар с таким названием уже существует!")
                return
            
            # Получаем ID категории
            cursor.execute("SELECT category_id FROM categories WHERE category_name=?", (category,))
            category_id = cursor.fetchone()[0]
            
            # Обновляем товар
            cursor.execute('''
                UPDATE products 
                SET product_name=?, category_id=?, price=?, quantity_in_stock=?
                WHERE product_id=?
            ''', (name, category_id, price, quantity, product_id))
            
            self.conn.commit()
            self.load_products()
            self.clear_product_fields()
            messagebox.showinfo("Успех", "Товар успешно обновлен!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить товар: {str(e)}")
    
    def delete_product(self):
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите товар для удаления!")
            return
        
        product_id = self.products_tree.item(selected, "values")[0]
        
        if not messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот товар?"):
            return
        
        try:
            cursor = self.conn.cursor()
            
            # Проверяем, есть ли товар в продажах
            cursor.execute("SELECT COUNT(*) FROM sale_items WHERE product_id=?", (product_id,))
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Ошибка", "Нельзя удалить товар, который есть в продажах!")
                return
            
            # Удаляем товар
            cursor.execute("DELETE FROM products WHERE product_id=?", (product_id,))
            
            self.conn.commit()
            self.load_products()
            self.clear_product_fields()
            messagebox.showinfo("Успех", "Товар успешно удален!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить товар: {str(e)}")
    
    def setup_sale_tab(self):
        # Фрейм для поиска и выбора товаров
        search_frame = ttk.LabelFrame(self.sale_tab, text="Поиск и выбор товаров")
        search_frame.pack(pady=10, padx=10, fill="x")
        
        # Поле поиска
        ttk.Label(search_frame, text="Поиск:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_products_for_sale)
        
        # Таблица доступных товаров
        self.available_products_tree = ttk.Treeview(
            search_frame,
            columns=("ID", "Название", "Цена", "В наличии"),
            show="headings",
            height=8
        )
        
        self.available_products_tree.heading("ID", text="ID")
        self.available_products_tree.heading("Название", text="Название")
        self.available_products_tree.heading("Цена", text="Цена")
        self.available_products_tree.heading("В наличии", text="В наличии")
        
        self.available_products_tree.column("ID", width=50, anchor="center")
        self.available_products_tree.column("Название", width=250, anchor="w")
        self.available_products_tree.column("Цена", width=100, anchor="e")
        self.available_products_tree.column("В наличии", width=80, anchor="center")
        
        scrollbar = ttk.Scrollbar(search_frame, orient="vertical", command=self.available_products_tree.yview)
        self.available_products_tree.configure(yscrollcommand=scrollbar.set)
        
        self.available_products_tree.pack(fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")
        
        # Загрузка доступных товаров
        self.load_available_products()
        
        # Привязка двойного клика для добавления товара
        self.available_products_tree.bind("<Double-1>", self.add_product_to_sale)
        
        # Фрейм для текущего чека
        sale_frame = ttk.LabelFrame(self.sale_tab, text="Текущий чек")
        sale_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Таблица товаров в чеке
        self.current_sale_tree = ttk.Treeview(
            sale_frame,
            columns=("ID", "Название", "Цена", "Количество", "Сумма"),
            show="headings"
        )
        
        self.current_sale_tree.heading("ID", text="ID")
        self.current_sale_tree.heading("Название", text="Название")
        self.current_sale_tree.heading("Цена", text="Цена")
        self.current_sale_tree.heading("Количество", text="Количество")
        self.current_sale_tree.heading("Сумма", text="Сумма")
        
        self.current_sale_tree.column("ID", width=50, anchor="center")
        self.current_sale_tree.column("Название", width=250, anchor="w")
        self.current_sale_tree.column("Цена", width=100, anchor="e")
        self.current_sale_tree.column("Количество", width=80, anchor="center")
        self.current_sale_tree.column("Сумма", width=100, anchor="e")
        
        scrollbar = ttk.Scrollbar(sale_frame, orient="vertical", command=self.current_sale_tree.yview)
        self.current_sale_tree.configure(yscrollcommand=scrollbar.set)
        
        self.current_sale_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")
        
        # Фрейм для кнопок управления чеком
        button_frame = ttk.Frame(sale_frame)
        button_frame.pack(side="right", fill="y", padx=5)
        
        ttk.Button(button_frame, text="Удалить", command=self.remove_from_sale).pack(pady=5, fill="x")
        ttk.Button(button_frame, text="Очистить", command=self.clear_sale).pack(pady=5, fill="x")
        
        # Итоговая сумма
        self.total_label = ttk.Label(sale_frame, text="Итого: 0.00 руб.", font=("Arial", 12, "bold"))
        self.total_label.pack(side="bottom", pady=10)
        
        # Кнопка оформления продажи
        ttk.Button(self.sale_tab, text="Оформить продажу", command=self.process_sale).pack(pady=10)
    
    def load_available_products(self):
        # Очистка таблицы
        for row in self.available_products_tree.get_children():
            self.available_products_tree.delete(row)
        
        # Загрузка товаров с ненулевым остатком
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT product_id, product_name, price, quantity_in_stock
            FROM products
            WHERE quantity_in_stock > 0
            ORDER BY product_name
        ''')
        
        for product in cursor.fetchall():
            self.available_products_tree.insert("", "end", values=product)
    
    def search_products_for_sale(self, event=None):
        query = self.search_entry.get().strip()
        
        # Очистка таблицы
        for row in self.available_products_tree.get_children():
            self.available_products_tree.delete(row)
        
        # Поиск товаров
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT product_id, product_name, price, quantity_in_stock
            FROM products
            WHERE product_name LIKE ? AND quantity_in_stock > 0
            ORDER BY product_name
        ''', (f"%{query}%",))
        
        for product in cursor.fetchall():
            self.available_products_tree.insert("", "end", values=product)
    
    def add_product_to_sale(self, event):
        selected = self.available_products_tree.focus()
        if not selected:
            return
        
        product = self.available_products_tree.item(selected, "values")
        product_id = product[0]
        product_name = product[1]
        price = float(product[2])
        available = int(product[3])
        
        # Проверяем, есть ли уже этот товар в чеке
        existing_item = None
        current_qty = 0
        for item in self.current_sale_tree.get_children():
            if self.current_sale_tree.item(item, "values")[0] == product_id:
                existing_item = item
                current_qty = int(self.current_sale_tree.item(item, "values")[3])
                break
        
        if existing_item:
            # Товар уже есть в чеке - обновляем количество
            self.update_existing_product_in_sale(existing_item, product_id, product_name, price, available, current_qty)
        else:
            # Товара нет в чеке - добавляем новый
            self.ask_quantity_for_product(product_id, product_name, price, available)
    
    def update_existing_product_in_sale(self, item_id, product_id, product_name, price, available, current_qty):
        top = tk.Toplevel(self.root)
        top.title("Обновление количества")
        top.resizable(False, False)
        
        ttk.Label(top, text=f"Товар: {product_name}\nЦена: {price:.2f} руб.\nДоступно: {available}").pack(pady=10)
        
        ttk.Label(top, text=f"Текущее количество: {current_qty}").pack()
        ttk.Label(top, text="Добавить количество:").pack()
        
        add_qty_entry = ttk.Entry(top)
        add_qty_entry.pack(pady=5)
        add_qty_entry.insert(0, "1")
        add_qty_entry.focus()
        
        def update_sale():
            try:
                add_qty = int(add_qty_entry.get())
                if add_qty <= 0:
                    messagebox.showerror("Ошибка", "Количество должно быть положительным!")
                    return
                
                new_qty = current_qty + add_qty
                if new_qty > available:
                    messagebox.showerror("Ошибка", 
                        f"Недостаточно товара! Доступно: {available}, уже в чеке: {current_qty}")
                    return
                
                total = price * new_qty
                self.current_sale_tree.item(item_id, 
                    values=(product_id, product_name, price, new_qty, total))
                self.update_sale_total()
                top.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Введите целое число!")
        
        ttk.Button(top, text="Обновить", command=update_sale).pack(pady=10)
        top.bind("<Return>", lambda e: update_sale())
    
    def ask_quantity_for_product(self, product_id, product_name, price, available):
        top = tk.Toplevel(self.root)
        top.title("Выбор количества")
        top.resizable(False, False)
        
        ttk.Label(top, text=f"Товар: {product_name}\nЦена: {price:.2f} руб.\nДоступно: {available}").pack(pady=10)
        
        ttk.Label(top, text="Количество:").pack()
        quantity_entry = ttk.Entry(top)
        quantity_entry.pack(pady=5)
        quantity_entry.insert(0, "1")
        quantity_entry.focus()
        
        def add_to_sale():
            try:
                quantity = int(quantity_entry.get())
                if quantity <= 0:
                    messagebox.showerror("Ошибка", "Количество должно быть положительным!")
                    return
                if quantity > available:
                    messagebox.showerror("Ошибка", f"Недостаточно товара! Доступно: {available}")
                    return
                
                total = price * quantity
                self.current_sale_tree.insert(
                    "", "end", 
                    values=(product_id, product_name, price, quantity, total),
                    tags=(product_id,)
                )
                self.update_sale_total()
                top.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Введите целое число!")
        
        ttk.Button(top, text="Добавить", command=add_to_sale).pack(pady=10)
        top.bind("<Return>", lambda e: add_to_sale())
    
    def remove_from_sale(self):
        selected = self.current_sale_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите товар для удаления!")
            return
        
        self.current_sale_tree.delete(selected)
        self.update_sale_total()
    
    def clear_sale(self):
        if not self.current_sale_tree.get_children():
            return
        
        if messagebox.askyesno("Подтверждение", "Очистить текущий чек?"):
            self.current_sale_tree.delete(*self.current_sale_tree.get_children())
            self.update_sale_total()
    
    def update_sale_total(self):
        total = 0.0
        for item in self.current_sale_tree.get_children():
            total += float(self.current_sale_tree.item(item, "values")[4])
        self.total_label.config(text=f"Итого: {total:.2f} руб.")
    
    def process_sale(self):
        if not self.current_sale_tree.get_children():
            messagebox.showerror("Ошибка", "Чек пуст!")
            return
        
        total = sum(float(self.current_sale_tree.item(item, "values")[4]) 
                  for item in self.current_sale_tree.get_children())
        
        try:
            cursor = self.conn.cursor()
            
            # Начинаем транзакцию
            cursor.execute("BEGIN TRANSACTION")
            
            # Создаем запись о продаже
            cursor.execute("INSERT INTO sales (total_amount) VALUES (?)", (total,))
            sale_id = cursor.lastrowid
            
            # Добавляем товары в продажу
            for item in self.current_sale_tree.get_children():
                values = self.current_sale_tree.item(item, "values")
                product_id = values[0]
                quantity = int(values[3])
                price = float(values[2])
                total_price = float(values[4])
                
                # Добавляем позицию в чек
                cursor.execute('''
                    INSERT INTO sale_items (sale_id, product_id, quantity, price_per_unit, total_price)
                    VALUES (?, ?, ?, ?, ?)
                ''', (sale_id, product_id, quantity, price, total_price))
                
                # Уменьшаем количество на складе
                cursor.execute('''
                    UPDATE products 
                    SET quantity_in_stock = quantity_in_stock - ?
                    WHERE product_id = ?
                ''', (quantity, product_id))
            
            # Завершаем транзакцию
            self.conn.commit()
            
            # Очищаем чек
            self.current_sale_tree.delete(*self.current_sale_tree.get_children())
            self.update_sale_total()
            
            # Обновляем список доступных товаров
            self.load_available_products()
            
            messagebox.showinfo("Успех", f"Продажа #{sale_id} оформлена!\nСумма: {total:.2f} руб.")
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Ошибка", f"Не удалось оформить продажу: {str(e)}")
    
    def setup_reports_tab(self):
        # Фрейм для фильтров
        filter_frame = ttk.LabelFrame(self.reports_tab, text="Фильтры")
        filter_frame.pack(pady=10, padx=10, fill="x")
        
        # Период
        ttk.Label(filter_frame, text="От:").grid(row=0, column=0, padx=5, pady=5)
        self.date_from_entry = ttk.Entry(filter_frame)
        self.date_from_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="До:").grid(row=0, column=2, padx=5, pady=5)
        self.date_to_entry = ttk.Entry(filter_frame)
        self.date_to_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Кнопка применения фильтров
        ttk.Button(filter_frame, text="Применить", command=self.load_sales_report).grid(row=0, column=4, padx=10)
        
        # Таблица продаж
        self.sales_report_tree = ttk.Treeview(
            self.reports_tab,
            columns=("ID", "Дата", "Сумма"),
            show="headings"
        )
        
        self.sales_report_tree.heading("ID", text="ID")
        self.sales_report_tree.heading("Дата", text="Дата")
        self.sales_report_tree.heading("Сумма", text="Сумма")
        
        self.sales_report_tree.column("ID", width=50, anchor="center")
        self.sales_report_tree.column("Дата", width=150, anchor="center")
        self.sales_report_tree.column("Сумма", width=100, anchor="e")
        
        scrollbar = ttk.Scrollbar(self.reports_tab, orient="vertical", command=self.sales_report_tree.yview)
        self.sales_report_tree.configure(yscrollcommand=scrollbar.set)
        
        self.sales_report_tree.pack(fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Привязка события выбора продажи
        self.sales_report_tree.bind("<<TreeviewSelect>>", self.show_sale_details)
        
        # Фрейм для деталей продажи
        details_frame = ttk.LabelFrame(self.reports_tab, text="Детали продажи")
        details_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Таблица товаров в продаже
        self.sale_details_tree = ttk.Treeview(
            details_frame,
            columns=("Товар", "Цена", "Кол-во", "Сумма"),
            show="headings"
        )
        
        self.sale_details_tree.heading("Товар", text="Товар")
        self.sale_details_tree.heading("Цена", text="Цена")
        self.sale_details_tree.heading("Кол-во", text="Кол-во")
        self.sale_details_tree.heading("Сумма", text="Сумма")
        
        self.sale_details_tree.column("Товар", width=250, anchor="w")
        self.sale_details_tree.column("Цена", width=100, anchor="e")
        self.sale_details_tree.column("Кол-во", width=80, anchor="center")
        self.sale_details_tree.column("Сумма", width=100, anchor="e")
        
        scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=self.sale_details_tree.yview)
        self.sale_details_tree.configure(yscrollcommand=scrollbar.set)
        
        self.sale_details_tree.pack(fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")
        
        # Итоговая статистика
        self.stats_label = ttk.Label(details_frame, text="", font=("Arial", 10))
        self.stats_label.pack(side="bottom", pady=5)
        
        # Загрузка данных
        self.load_sales_report()
    
    def load_sales_report(self):
        # Очистка таблицы
        for row in self.sales_report_tree.get_children():
            self.sales_report_tree.delete(row)
        
        # Получение параметров фильтра
        date_from = self.date_from_entry.get().strip() or "1970-01-01"
        date_to = self.date_to_entry.get().strip() or "2100-01-01"
        
        try:
            cursor = self.conn.cursor()
            
            # Загрузка продаж за период
            cursor.execute('''
                SELECT sale_id, strftime('%Y-%m-%d %H:%M', sale_date), total_amount
                FROM sales
                WHERE date(sale_date) BETWEEN ? AND ?
                ORDER BY sale_date DESC
            ''', (date_from, date_to))
            
            for sale in cursor.fetchall():
                self.sales_report_tree.insert("", "end", values=sale)
            
            # Расчет общей выручки
            cursor.execute('''
                SELECT COUNT(*), SUM(total_amount)
                FROM sales
                WHERE date(sale_date) BETWEEN ? AND ?
            ''', (date_from, date_to))
            
            count, total = cursor.fetchone()
            count = count or 0
            total = total or 0.0
            
            self.stats_label.config(
                text=f"Всего продаж: {count} | Общая выручка: {total:.2f} руб. | Средний чек: {total/count:.2f} руб." if count else "Нет данных"
            )
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить отчет: {str(e)}")
    
    def show_sale_details(self, event):
        selected = self.sales_report_tree.focus()
        if not selected:
            return
        
        sale_id = self.sales_report_tree.item(selected, "values")[0]
        
        # Очистка таблицы
        for row in self.sale_details_tree.get_children():
            self.sale_details_tree.delete(row)
        
        try:
            cursor = self.conn.cursor()
            
            # Загрузка деталей продажи
            cursor.execute('''
                SELECT p.product_name, si.price_per_unit, si.quantity, si.total_price
                FROM sale_items si
                JOIN products p ON si.product_id = p.product_id
                WHERE si.sale_id = ?
                ORDER BY p.product_name
            ''', (sale_id,))
            
            for item in cursor.fetchall():
                self.sale_details_tree.insert("", "end", values=item)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить детали продажи: {str(e)}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = StoreApp(root)
    app.run()