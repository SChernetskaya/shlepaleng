# database.py
import sqlite3
import json
import hashlib
from datetime import datetime
from config import DB_PATH


class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        """Подключение к базе данных"""
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.add_sample_data()

    def create_tables(self):
        """Создание таблиц базы данных"""
        # Таблица пользователей
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                role TEXT DEFAULT 'user',
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                level INTEGER DEFAULT 1,
                experience INTEGER DEFAULT 0,
                streak_days INTEGER DEFAULT 0,
                last_login TIMESTAMP
            )
        ''')

        # Таблица слов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                english TEXT NOT NULL,
                russian TEXT NOT NULL,
                transcription TEXT,
                category TEXT,
                difficulty_level INTEGER DEFAULT 1,
                added_by INTEGER,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (added_by) REFERENCES users(id)
            )
        ''')

        # Таблица лекций
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS lectures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT,
                difficulty_level INTEGER DEFAULT 1,
                created_by INTEGER,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        ''')

        # Таблица тестов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                lecture_id INTEGER,
                questions TEXT NOT NULL,
                created_by INTEGER,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lecture_id) REFERENCES lectures(id),
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        ''')

        # Таблица результатов тестов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                test_id INTEGER,
                score INTEGER,
                max_score INTEGER,
                completed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (test_id) REFERENCES tests(id)
            )
        ''')

        # Таблица прогресса пользователя
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                completed_lectures TEXT DEFAULT '[]',
                completed_tests TEXT DEFAULT '[]',
                words_learned TEXT DEFAULT '[]',
                total_time INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Таблица игровых результатов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                game_type TEXT,
                score INTEGER,
                completed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        self.conn.commit()

    def add_sample_data(self):
        """Добавление тестовых данных"""
        # Проверяем есть ли администратор
        self.cursor.execute("SELECT * FROM users WHERE username='admin'")
        if not self.cursor.fetchone():
            admin_hash = hashlib.sha256('admin123'.encode()).hexdigest()
            self.cursor.execute(
                "INSERT INTO users (username, password_hash, email, role) VALUES (?, ?, ?, ?)",
                ('admin', admin_hash, 'admin@shlepalang.ru', 'admin')
            )

        # Проверяем есть ли слова в словаре
        self.cursor.execute("SELECT COUNT(*) FROM words")
        if self.cursor.fetchone()[0] == 0:
            sample_words = [
                ('hello', 'привет', 'həˈləʊ', 'Основные'),
                ('goodbye', 'до свидания', 'ɡʊdˈbaɪ', 'Основные'),
                ('thank you', 'спасибо', 'θæŋk juː', 'Основные'),
                ('please', 'пожалуйста', 'pliːz', 'Основные'),
                ('cat', 'кот', 'kæt', 'Животные'),
                ('dog', 'собака', 'dɒɡ', 'Животные'),
                ('book', 'книга', 'bʊk', 'Образование'),
                ('pen', 'ручка', 'pen', 'Образование'),
            ]

            for word in sample_words:
                self.cursor.execute(
                    "INSERT INTO words (english, russian, transcription, category) VALUES (?, ?, ?, ?)",
                    word
                )

        # Проверяем есть ли лекции
        self.cursor.execute("SELECT COUNT(*) FROM lectures")
        if self.cursor.fetchone()[0] == 0:
            sample_lectures = [
                ('Введение в английский язык',
                 'Английский язык является одним из самых распространенных языков в мире...',
                 'Основы'),
                ('Приветствия и прощания',
                 'В английском языке есть различные способы приветствия и прощания...',
                 'Основные фразы'),
            ]

            for lecture in sample_lectures:
                self.cursor.execute(
                    "INSERT INTO lectures (title, content, category) VALUES (?, ?, ?)",
                    lecture
                )

        self.conn.commit()

    def close(self):
        """Закрытие соединения с БД"""
        if self.conn:
            self.conn.close()

    # Методы для работы с пользователями
    def get_user(self, username, password_hash):
        """Получение пользователя по логину и паролю"""
        self.cursor.execute(
            "SELECT id, username, role FROM users WHERE username=? AND password_hash=?",
            (username, password_hash)
        )
        return self.cursor.fetchone()

    def get_user_by_id(self, user_id):
        """Получение пользователя по ID"""
        self.cursor.execute("SELECT username, level, experience FROM users WHERE id=?", (user_id,))
        return self.cursor.fetchone()

    def create_user(self, username, email, password_hash):
        """Создание нового пользователя"""
        self.cursor.execute(
            "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
            (username, password_hash, email)
        )
        user_id = self.cursor.lastrowid
        self.cursor.execute(
            "INSERT INTO user_progress (user_id) VALUES (?)",
            (user_id,)
        )
        self.conn.commit()
        return user_id

    def update_last_login(self, user_id):
        """Обновление времени последнего входа"""
        self.cursor.execute(
            "UPDATE users SET last_login=? WHERE id=?",
            (datetime.now(), user_id)
        )
        self.conn.commit()

    def add_experience(self, user_id, exp_amount):
        """Добавление опыта пользователю"""
        self.cursor.execute(
            "UPDATE users SET experience = experience + ? WHERE id=?",
            (exp_amount, user_id)
        )

        # Проверка повышения уровня
        self.cursor.execute("SELECT experience, level FROM users WHERE id=?", (user_id,))
        user_data = self.cursor.fetchone()

        required_exp = user_data[1] * 100
        if user_data[0] >= required_exp:
            self.cursor.execute(
                "UPDATE users SET level = level + 1 WHERE id=?",
                (user_id,)
            )
            self.conn.commit()
            return True
        self.conn.commit()
        return False

    # Методы для работы со словами
    def get_words(self, category=None, search=None):
        """Получение списка слов"""
        query = "SELECT english, russian, transcription, category FROM words WHERE 1=1"
        params = []

        if category and category != "Все категории":
            query += " AND category = ?"
            params.append(category)

        if search:
            query += " AND (english LIKE ? OR russian LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])

        query += " ORDER BY english"

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def get_categories(self):
        """Получение списка категорий"""
        self.cursor.execute("SELECT DISTINCT category FROM words WHERE category IS NOT NULL ORDER BY category")
        return [row[0] for row in self.cursor.fetchall()]

    def add_word(self, english, russian, transcription, category, added_by):
        """Добавление нового слова"""
        self.cursor.execute(
            "INSERT INTO words (english, russian, transcription, category, added_by) VALUES (?, ?, ?, ?, ?)",
            (english, russian, transcription, category if category else None, added_by)
        )
        self.conn.commit()

    def get_random_words(self, limit=10):
        """Получение случайных слов"""
        self.cursor.execute("SELECT english, russian FROM words ORDER BY RANDOM() LIMIT ?", (limit,))
        return self.cursor.fetchall()

    def get_wrong_answers(self, correct_answer, limit=3):
        """Получение неправильных вариантов ответов"""
        self.cursor.execute(
            "SELECT russian FROM words WHERE russian != ? ORDER BY RANDOM() LIMIT ?",
            (correct_answer, limit)
        )
        return [row[0] for row in self.cursor.fetchall()]

    # Методы для работы с лекциями
    def get_lectures(self):
        """Получение списка лекций"""
        self.cursor.execute("SELECT id, title, category, difficulty_level FROM lectures ORDER BY category, title")
        return self.cursor.fetchall()

    def get_lecture(self, lecture_id):
        """Получение конкретной лекции"""
        self.cursor.execute("SELECT title, content FROM lectures WHERE id=?", (lecture_id,))
        return self.cursor.fetchone()

    def add_lecture(self, title, content, category, difficulty, created_by):
        """Добавление новой лекции"""
        self.cursor.execute(
            "INSERT INTO lectures (title, content, category, difficulty_level, created_by) VALUES (?, ?, ?, ?, ?)",
            (title, content, category if category else None, int(difficulty), created_by)
        )
        self.conn.commit()

    def get_lectures_count(self):
        """Получение общего количества лекций"""
        self.cursor.execute("SELECT COUNT(*) FROM lectures")
        return self.cursor.fetchone()[0]

    # Методы для работы с тестами
    def get_tests(self, user_id=None):
        """Получение списка тестов"""
        if user_id:
            self.cursor.execute("""
                SELECT t.id, t.title, l.title, COUNT(tr.id) as attempts
                FROM tests t
                LEFT JOIN lectures l ON t.lecture_id = l.id
                LEFT JOIN test_results tr ON t.id = tr.test_id AND tr.user_id = ?
                GROUP BY t.id
            """, (user_id,))
        else:
            self.cursor.execute("""
                SELECT t.id, t.title, l.title, 0 as attempts
                FROM tests t
                LEFT JOIN lectures l ON t.lecture_id = l.id
            """)
        return self.cursor.fetchall()

    def get_test(self, test_id):
        """Получение конкретного теста"""
        self.cursor.execute("SELECT title, questions FROM tests WHERE id=?", (test_id,))
        return self.cursor.fetchone()

    def add_test(self, title, lecture_id, questions, created_by):
        """Добавление нового теста"""
        self.cursor.execute(
            "INSERT INTO tests (title, lecture_id, questions, created_by) VALUES (?, ?, ?, ?)",
            (title, lecture_id, json.dumps(questions), created_by)
        )
        self.conn.commit()

    def save_test_result(self, user_id, test_id, score, max_score):
        """Сохранение результата теста"""
        self.cursor.execute(
            "INSERT INTO test_results (user_id, test_id, score, max_score) VALUES (?, ?, ?, ?)",
            (user_id, test_id, score, max_score)
        )
        self.conn.commit()

    # Методы для работы с прогрессом
    def get_user_stats(self, user_id):
        """Получение статистики пользователя"""
        self.cursor.execute('''
            SELECT 
                u.level,
                u.experience,
                u.streak_days,
                up.completed_lectures,
                up.completed_tests,
                up.words_learned,
                up.total_time,
                (SELECT COUNT(*) FROM test_results WHERE user_id=u.id) as tests_completed,
                (SELECT AVG(score*100.0/max_score) FROM test_results WHERE user_id=u.id) as avg_test_score
            FROM users u
            LEFT JOIN user_progress up ON u.id = up.user_id
            WHERE u.id = ?
        ''', (user_id,))
        return self.cursor.fetchone()

    def mark_lecture_completed(self, user_id, lecture_id):
        """Отметить лекцию как завершенную"""
        self.cursor.execute(
            "SELECT completed_lectures FROM user_progress WHERE user_id=?",
            (user_id,)
        )
        result = self.cursor.fetchone()

        if result:
            completed_lectures = json.loads(result[0])
            if lecture_id not in completed_lectures:
                completed_lectures.append(lecture_id)
                self.cursor.execute(
                    "UPDATE user_progress SET completed_lectures=? WHERE user_id=?",
                    (json.dumps(completed_lectures), user_id)
                )
                self.conn.commit()

    # Методы для работы с играми
    def save_game_result(self, user_id, game_type, score):
        """Сохранение результата игры"""
        self.cursor.execute(
            "INSERT INTO game_results (user_id, game_type, score) VALUES (?, ?, ?)",
            (user_id, game_type, score)
        )
        self.conn.commit()

    # Административные методы
    def get_system_stats(self):
        """Получение статистики системы"""
        self.cursor.execute("SELECT COUNT(*) FROM users WHERE role='user'")
        users_count = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
        admins_count = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM words")
        words_count = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM lectures")
        lectures_count = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM tests")
        tests_count = self.cursor.fetchone()[0]

        return {
            'users': users_count,
            'admins': admins_count,
            'words': words_count,
            'lectures': lectures_count,
            'tests': tests_count
        }

    # Вспомогательные методы
    @staticmethod
    def hash_password(password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()

    def commit(self):
        """Подтверждение изменений"""
        self.conn.commit()