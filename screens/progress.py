# screens/progress.py
import customtkinter as ctk
from tkinter import messagebox
import json


class ProgressScreen:
    def __init__(self, parent, db, colors, user_id):
        self.parent = parent
        self.db = db
        self.colors = colors
        self.user_id = user_id
        self.frame = None

    def create(self, container):
        """Создание экрана прогресса"""
        self.frame = ctk.CTkFrame(container, fg_color="transparent")

        title_label = ctk.CTkLabel(
            self.frame,
            text="📈 Ваш прогресс",
            font=("Arial", 24, "bold")
        )
        title_label.pack(anchor="w", pady=(0, 20))

        if not self.user_id:
            self.create_guest_message()
            return self.frame

        # Получение данных о прогрессе
        progress = self.db.get_user_stats(self.user_id)

        if not progress:
            empty_label = ctk.CTkLabel(self.frame, text="Нет данных о прогрессе", font=("Arial", 16))
            empty_label.pack(pady=50)
            return self.frame

        (level, experience, streak_days, completed_lectures_json,
         completed_tests_json, words_learned_json, total_time,
         tests_completed, avg_test_score) = progress

        # Основная статистика
        self.create_main_stats(level, experience, streak_days, total_time,
                               tests_completed, avg_test_score)

        # Детальная статистика
        self.create_detailed_stats(completed_lectures_json, words_learned_json)

        return self.frame

    def create_guest_message(self):
        """Сообщение для гостя"""
        guest_label = ctk.CTkLabel(
            self.frame,
            text="Для отслеживания прогресса необходимо войти в систему",
            font=("Arial", 16)
        )
        guest_label.pack(pady=50)

        login_button = ctk.CTkButton(
            self.frame,
            text="Войти",
            command=self.parent.show_login,
            width=200,
            height=40
        )
        login_button.pack(pady=10)

    def create_main_stats(self, level, experience, streak_days, total_time,
                          tests_completed, avg_test_score):
        """Создание основной статистики"""
        stats_frame = ctk.CTkFrame(self.frame, fg_color=self.colors['card'])
        stats_frame.pack(fill="x", pady=10)

        main_stats = [
            ("Уровень", level, "🎯"),
            ("Опыт", f"{experience}/{level * 100}", "⭐"),
            ("Дней подряд", streak_days, "🔥"),
            ("Время обучения", f"{total_time} мин", "⏱️"),
            ("Пройдено тестов", tests_completed, "📝"),
            ("Средний балл", f"{avg_test_score:.1f}%" if avg_test_score else "0%", "📊"),
        ]

        for i, (label, value, icon) in enumerate(main_stats):
            stat_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
            stat_frame.grid(row=i // 3, column=i % 3, padx=20, pady=20, sticky="nsew")

            icon_label = ctk.CTkLabel(stat_frame, text=icon, font=("Arial", 24))
            icon_label.pack()

            value_label = ctk.CTkLabel(stat_frame, text=str(value), font=("Arial", 20, "bold"))
            value_label.pack()

            label_label = ctk.CTkLabel(stat_frame, text=label, font=("Arial", 12), text_color="gray")
            label_label.pack()

    def create_detailed_stats(self, completed_lectures_json, words_learned_json):
        """Создание детальной статистики"""
        detail_label = ctk.CTkLabel(
            self.frame,
            text="Детальная статистика",
            font=("Arial", 20, "bold")
        )
        detail_label.pack(anchor="w", pady=(30, 10))

        detail_frame = ctk.CTkFrame(self.frame, fg_color=self.colors['card'])
        detail_frame.pack(fill="x", pady=10)

        # Пройденные лекции
        completed_lectures = json.loads(completed_lectures_json) if completed_lectures_json else []
        total_lectures = self.db.get_lectures_count()

        lectures_progress = ctk.CTkProgressBar(detail_frame)
        lectures_progress.pack(padx=20, pady=10, fill="x")
        lectures_progress.set(len(completed_lectures) / max(total_lectures, 1))

        lectures_label = ctk.CTkLabel(
            detail_frame,
            text=f"Лекции: {len(completed_lectures)}/{total_lectures}",
            font=("Arial", 12)
        )
        lectures_label.pack(padx=20, pady=(0, 10))

        # Выученные слова
        words_learned = json.loads(words_learned_json) if words_learned_json else []
        total_words = len(self.db.get_words())

        words_progress = ctk.CTkProgressBar(detail_frame)
        words_progress.pack(padx=20, pady=10, fill="x")
        words_progress.set(len(words_learned) / max(total_words, 1))

        words_label = ctk.CTkLabel(
            detail_frame,
            text=f"Слова: {len(words_learned)}/{total_words}",
            font=("Arial", 12)
        )
        words_label.pack(padx=20, pady=(0, 20))

    def destroy(self):
        """Уничтожение экрана"""
        if self.frame:
            self.frame.destroy()