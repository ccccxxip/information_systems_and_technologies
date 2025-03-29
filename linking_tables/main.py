import pandas as pd
from datetime import datetime

def load_data(file_path):
    # Загрузка данных 
    try:
        trade_df = pd.read_excel(file_path, sheet_name='Торговля')
        trade_df = trade_df.rename(columns={'ID операции': 'ID_операции'})
        
        product_df = pd.read_excel(file_path, sheet_name='Товар')
        
        shop_df = pd.read_excel(file_path, sheet_name='Магазин')
        # Создаем колонку "Магазин" из "ID_магазина" для соединения
        shop_df['Магазин'] = shop_df['ID_магазина']
        
        return trade_df, product_df, shop_df
    except Exception as e:
        raise ValueError(f"Ошибка загрузки данных: {str(e)}")

def calculate_revenue(file_path):
    try:
        # Загрузка данных
        trade_df, product_df, shop_df = load_data(file_path)
        
        # Проверка наличия всех необходимых столбцов
        required_trade_columns = ['Дата', 'Магазин', 'Артикул', 'Операция', 'Количество_упаковок,шт', 'Цена_руб/шт']
        required_product_columns = ['Артикул', 'Отдел']
        required_shop_columns = ['Магазин', 'Район']
        
        missing_trade = set(required_trade_columns) - set(trade_df.columns)
        if missing_trade:
            raise ValueError(f"В таблице 'Торговля' отсутствуют столбцы: {missing_trade}")
        
        missing_product = set(required_product_columns) - set(product_df.columns)
        if missing_product:
            raise ValueError(f"В таблице 'Товар' отсутствуют столбцы: {missing_product}")
        
        missing_shop = set(required_shop_columns) - set(shop_df.columns)
        if missing_shop:
            raise ValueError(f"В таблице 'Магазин' отсутствуют столбцы: {missing_shop}")
        
        trade_df['Дата'] = pd.to_datetime(trade_df['Дата'], errors='coerce')
        trade_df = trade_df.dropna(subset=['Дата'])
        
        # Период для фильтрации (14-20 июня 2021)
        start_date = pd.to_datetime('2021-06-14')
        end_date = pd.to_datetime('2021-06-20')
        
        # Фильтрация по дате и операции
        filtered = trade_df[
            (trade_df['Дата'] >= start_date) & 
            (trade_df['Дата'] <= end_date) & 
            (trade_df['Операция'] == 'Продажа')
        ].copy()
        
        if filtered.empty:
            raise ValueError("Нет данных о продажах за указанный период (14-20 июня 2021)")
        
        # Объединение с товарами для фильтрации по отделу "Бакалея"
        merged = pd.merge(
            filtered, 
            product_df[['Артикул', 'Отдел']], 
            on='Артикул', 
            how='left'
        )
        
        merged = merged[merged['Отдел'] == 'Бакалея']
        
        if merged.empty:
            raise ValueError("Нет данных о продажах товаров отдела 'Бакалея'")
        
        # Объединение с магазинами для фильтрации по району
        result = pd.merge(
            merged, 
            shop_df[['Магазин', 'Район']], 
            on='Магазин', 
            how='left'
        )
        
        result = result[result['Район'] == 'Первомайский']
        
        if result.empty:
            raise ValueError("Нет данных о продажах в Первомайском районе")
        
        # Расчет выручки
        result['Выручка'] = result['Количество_упаковок,шт'] * result['Цена_руб/шт']
        total = result['Выручка'].sum()
        
        return total  # Добавлен возврат значения
        
    except Exception as e:
        print(f"\nОшибка при расчетах: {str(e)}")
        return None

if __name__ == '__main__':
    file_path = "linking_tables/example.xlsx"  # Исправлен путь (используйте / вместо \)
    print("Расчет выручки от продаж 'Бакалеи' в Первомайском районе (14-20 июня 2021)")
    print("="*70)
    
    revenue = calculate_revenue(file_path)
    
    if revenue is not None:
        print("\n" + "="*70)
        print(f"Итоговая выручка: {revenue:.2f} руб.")
    else:
        print("\nНе удалось рассчитать выручку. Проверьте данные.")