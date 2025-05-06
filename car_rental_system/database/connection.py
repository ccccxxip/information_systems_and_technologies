import sqlite3
from pathlib import Path

def get_db_connection():
    """Создает и возвращает соединение с базой данных"""
    db_path = Path(__file__).parent / "car_rental.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Для доступа к полям по имени
    return conn

def init_db():
    """Инициализирует базу данных (создает таблицы)"""
    conn = get_db_connection()
    try:
        # Импортируем здесь, чтобы избежать циклических зависимостей
        from database.models import create_tables
        create_tables(conn)
        print("Таблицы базы данных успешно созданы")
    finally:
        conn.close()
