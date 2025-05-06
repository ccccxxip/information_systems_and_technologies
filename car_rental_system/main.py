from database.connection import init_db
from database.seed import fill_test_data

def main():
    print("Инициализация базы данных автопроката...")
    
    # 1. Создаем таблицы
    init_db()
    
    # 2. Заполняем тестовыми данными
    print("\nЗаполнение базы данных тестовыми данными...")
    fill_test_data()
    
    print("\nСистема готова к работе!")

if __name__ == "__main__":
    main()
