import sqlite3

# Создаем соединение с базой данных 
conn = sqlite3.connect('students_db.sqlite')
cursor = conn.cursor()

# Удаляем существующие таблицы перед созданием новых
cursor.executescript('''
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS level_of_training;
DROP TABLE IF EXISTS direction;
DROP TABLE IF EXISTS type_of_education;
''')

# Создаем таблицы заново
cursor.executescript('''
CREATE TABLE level_of_training (
    id_level INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE
);

CREATE TABLE direction (
    id_direction INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE
);

CREATE TABLE type_of_education (
    id_type INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE
);

CREATE TABLE students (
    id_student INTEGER PRIMARY KEY AUTOINCREMENT,
    id_level INTEGER NOT NULL,
    id_direction INTEGER NOT NULL,
    id_type_of_training INTEGER NOT NULL,
    student_id_number INTEGER NOT NULL UNIQUE,
    surname TEXT NOT NULL,
    name TEXT NOT NULL,
    patronymic TEXT NOT NULL,
    average_score REAL NOT NULL,
    FOREIGN KEY (id_level) REFERENCES level_of_training(id_level),
    FOREIGN KEY (id_direction) REFERENCES direction(id_direction),
    FOREIGN KEY (id_type_of_training) REFERENCES type_of_education(id_type),
    UNIQUE(surname, name, patronymic)  -- предотвращаем полных тезок
);
''')

# Заполняем таблицу 
levels = [
    ('Бакалавриат',),
    ('Магистратура',),
    ('Аспирантура',),
    ('Специалитет',)
]
cursor.executemany('INSERT OR IGNORE INTO level_of_training (title) VALUES (?)', levels)

# Заполняем таблицу direction
directions = [
    ('Информатика и вычислительная техника',),
    ('Математика',),
    ('Физика',),
    ('Экономика',),
    ('Лингвистика',)
]
cursor.executemany('INSERT OR IGNORE INTO direction (title) VALUES (?)', directions)

# Заполняем таблицу type_of_education
education_types = [
    ('Очная',),
    ('Заочная',),
    ('Очно-заочная',),
    ('Дистанционная',)
]
cursor.executemany('INSERT OR IGNORE INTO type_of_education (title) VALUES (?)', education_types)

# Заполняем таблицу students 
students_data = [
    (1, 1, 1, 101, 'Иванов', 'Иван', 'Иванович', 4.5),
    (1, 2, 2, 102, 'Петров', 'Петр', 'Петрович', 4.2),
    (2, 3, 3, 103, 'Сидорова', 'Мария', 'Сергеевна', 4.8),
    (3, 4, 4, 104, 'Кузнецов', 'Алексей', 'Дмитриевич', 3.9),
    (2, 1, 1, 105, 'Смирнова', 'Елена', 'Андреевна', 4.7),
    (3, 2, 2, 106, 'Федоров', 'Дмитрий', 'Олегович', 4.1),
    (4, 3, 3, 107, 'Николаева', 'Ольга', 'Игоревна', 4.3),
    (1, 4, 4, 108, 'Васильев', 'Артем', 'Владимирович', 3.7),
    (2, 1, 1, 109, 'Павлова', 'Анна', 'Михайловна', 4.9),
    (3, 2, 2, 110, 'Алексеев', 'Сергей', 'Павлович', 4.0)
]

cursor.executemany('''
INSERT OR IGNORE INTO students 
(id_level, id_direction, id_type_of_training, student_id_number, 
 surname, name, patronymic, average_score) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', students_data)

# Сохраняем изменения 
conn.commit()

print("База данных успешно создана и заполнена данными!")

# Функция для вывода содержимого таблицы
def print_table(table_name):
    print(f"\n=== Содержимое таблицы {table_name} ===")
    cursor.execute(f"SELECT * FROM {table_name}")
    columns = [description[0] for description in cursor.description]
    print(" | ".join(columns))
    print("-" * 50)
    for row in cursor.fetchall():
        print(" | ".join(str(item) for item in row))

# Выводим все таблицы
print_table("level_of_training")
print_table("direction")
print_table("type_of_education")
print_table("students")

def execute_queries():
    print("\n=== Результаты запросов ===\n")
    
    # 1. Количество всех студентов
    cursor.execute("SELECT COUNT(*) FROM students")
    print(f"1. Общее количество студентов: {cursor.fetchone()[0]}")
    
    # 2. Количество студентов по направлениям
    print("\n2. Количество студентов по направлениям:")
    cursor.execute('''
    SELECT d.title, COUNT(*) 
    FROM students s
    JOIN direction d ON s.id_direction = d.id_direction
    GROUP BY d.title
    ''')
    for direction, count in cursor.fetchall():
        print(f"{direction}: {count} студентов")
    
    # 3. Количество студентов по формам обучения
    print("\n3. Количество студентов по формам обучения:")
    cursor.execute('''
    SELECT t.title, COUNT(*) 
    FROM students s
    JOIN type_of_education t ON s.id_type_of_training = t.id_type
    GROUP BY t.title
    ''')
    for form, count in cursor.fetchall():
        print(f"{form}: {count} студентов")
    
    # 4. Максимальный, минимальный, средний баллы по направлениям
    print("\n4. Статистика баллов по направлениям:")
    cursor.execute('''
    SELECT d.title, 
           MAX(s.average_score), 
           MIN(s.average_score), 
           AVG(s.average_score)
    FROM students s
    JOIN direction d ON s.id_direction = d.id_direction
    GROUP BY d.title
    ''')
    print("{:<30} {:<10} {:<10} {:<10}".format("Направление", "Макс", "Мин", "Средний"))
    for row in cursor.fetchall():
        print("{:<30} {:<10.2f} {:<10.2f} {:<10.2f}".format(*row))
    
    # 5. Средний балл по направлениям, уровням и формам обучения
    print("\n5. Средний балл по направлениям, уровням и формам обучения:")
    cursor.execute('''
    SELECT d.title, l.title, t.title, AVG(s.average_score)
    FROM students s
    JOIN direction d ON s.id_direction = d.id_direction
    JOIN level_of_training l ON s.id_level = l.id_level
    JOIN type_of_education t ON s.id_type_of_training = t.id_type
    GROUP BY d.title, l.title, t.title
    ''')
    print("{:<25} {:<15} {:<15} {:<10}".format("Направление", "Уровень", "Форма", "Ср. балл"))
    for row in cursor.fetchall():
        print("{:<25} {:<15} {:<15} {:<10.2f}".format(*row))
    
    # 6. Топ-5 студентов "Информатика и вычислительная техника" на очной форме
    print("\n6. Топ-5 студентов 'Информатика и вычислительная техника' (очная форма):")
    cursor.execute('''
    SELECT s.surname, s.name, s.patronymic, s.average_score
    FROM students s
    JOIN direction d ON s.id_direction = d.id_direction
    JOIN type_of_education t ON s.id_type_of_training = t.id_type
    WHERE d.title = 'Информатика и вычислительная техника' AND t.title = 'Очная'
    ORDER BY s.average_score DESC
    LIMIT 5
    ''')
    print("{:<15} {:<15} {:<15} {:<10}".format("Фамилия", "Имя", "Отчество", "Балл"))
    for row in cursor.fetchall():
        print("{:<15} {:<15} {:<15} {:<10.2f}".format(*row))
    
    # 7. Количество однофамильцев
    print("\n7. Количество однофамильцев:")
    cursor.execute('''
    SELECT surname, COUNT(*) as count
    FROM students
    GROUP BY surname
    HAVING COUNT(*) > 1
    ''')
    namesakes = cursor.fetchall()
    print(f"Всего групп однофамильцев: {len(namesakes)}")
    for surname, count in namesakes:
        print(f"Фамилия {surname}: {count} человек")
    
    # 8. Наличие полных тезок 
    print("\n8. Наличие полных тезок:")
    cursor.execute('''
    SELECT surname, name, patronymic, COUNT(*) as count
    FROM students
    GROUP BY surname, name, patronymic
    HAVING COUNT(*) > 1
    ''')
    full_namesakes = cursor.fetchall()
    if full_namesakes:
        print("Найдены полные тезки:")
        for row in full_namesakes:
            print(f"{row[0]} {row[1]} {row[2]}: {row[3]} человека")
    else:
        print("Полных тезок не найдено")

execute_queries()
conn.close()