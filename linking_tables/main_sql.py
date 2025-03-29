import sqlite3
import pandas as pd
from datetime import datetime

def create_database(file_path):
    try:
        trade_df = pd.read_excel(file_path, sheet_name='Торговля')
        product_df = pd.read_excel(file_path, sheet_name='Товар')
        shop_df = pd.read_excel(file_path, sheet_name='Магазин')
        
        required_trade = ['Дата', 'Магазин', 'Артикул', 'Операция', 'Количество_упаковок,шт', 'Цена_руб/шт']
        required_product = ['Артикул', 'Отдел']
        required_shop = ['ID_магазина', 'Район']
        
        for col in required_trade:
            if col not in trade_df.columns:
                raise ValueError(f"В таблице Торговля отсутствует столбец: {col}")
        
        for col in required_product:
            if col not in product_df.columns:
                raise ValueError(f"В таблице Товар отсутствует столбец: {col}")
                
        for col in required_shop:
            if col not in shop_df.columns:
                raise ValueError(f"В таблице Магазин отсутствует столбец: {col}")
        
        # Преобразование дат
        trade_df['Дата'] = pd.to_datetime(trade_df['Дата']).dt.strftime('%Y-%m-%d')
        
        # Создание БД
        conn = sqlite3.connect(':memory:')
        trade_df.to_sql('trade', conn, index=False)
        product_df.to_sql('product', conn, index=False)
        shop_df.to_sql('shop', conn, index=False)
        
        return conn
    except Exception as e:
        raise ValueError(f"Ошибка при создании БД: {str(e)}")

def calculate_revenue_sql(file_path):
    """Вычисляем выручку"""
    try:
        conn = create_database(file_path)
        cursor = conn.cursor()
        
        # Проверочные запросы
        cursor.execute("SELECT COUNT(*) FROM trade WHERE Операция = 'Продажа'")
        total_sales = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT Артикул) FROM product WHERE Отдел = 'Бакалея'")
        bakery_items = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT ID_магазина) FROM shop WHERE Район = 'Первомайский'")
        shops_count = cursor.fetchone()[0]
        
        query = """
        SELECT 
            t.Дата,
            t.Магазин,
            t.Артикул,
            t."Количество_упаковок,шт",
            t."Цена_руб/шт",
            (t."Количество_упаковок,шт" * t."Цена_руб/шт") AS revenue
        FROM trade t
        JOIN product p ON t.Артикул = p.Артикул
        JOIN shop s ON t.Магазин = s.ID_магазина
        WHERE 
            t.Операция = 'Продажа'
            AND t.Дата BETWEEN '2021-06-14' AND '2021-06-20'
            AND p.Отдел = 'Бакалея'
            AND s.Район = 'Первомайский'
        ORDER BY t.Дата
        """
        
        cursor.execute(query)
        detailed_results = cursor.fetchall()
        
        # Итоговый расчёт
        query_total = """
        SELECT SUM(t."Количество_упаковок,шт" * t."Цена_руб/шт")
        FROM trade t
        JOIN product p ON t.Артикул = p.Артикул
        JOIN shop s ON t.Магазин = s.ID_магазина
        WHERE 
            t.Операция = 'Продажа'
            AND t.Дата BETWEEN '2021-06-14' AND '2021-06-20'
            AND p.Отдел = 'Бакалея'
            AND s.Район = 'Первомайский'
        """
        
        cursor.execute(query_total)
        total_revenue = cursor.fetchone()[0] or 0
    
        conn.close()
        return total_revenue
        
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return None

if __name__ == '__main__':
    file_path = "linking_tables\example.xlsx" 
    
    print("Расчёт выручки от продаж 'Бакалеи' в Первомайском районе (14-20 июня 2021)")
    
    revenue = calculate_revenue_sql(file_path)
    
    if revenue is not None:
        print(f"Итоговая выручка: {revenue:.2f} руб.")
    else:
        print("\nНе удалось рассчитать выручку. Проверьте данные.")