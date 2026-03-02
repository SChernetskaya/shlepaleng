# screens/dashboard.py
import customtkinter as ctk


class DashboardScreen:
    def __init__(self, parent, db, colors, user_id):
        self.parent = parent
        self.db = db
        self.colors = colors
        self.user_id = user_id
        self.frame = None

    def create(self, container):
        """Создание экрана главной страницы"""
        self.frame = ctk.CTkFrame(container, fg_color="transparent")

        # Заголовок
        title_label = ctk.CTkLabel(
            self.frame,
            text="Главная страница",
            font=("Arial", 24, "bold")
        )
        title_label.pack(anchor="w", pady=(0, 20))

        if self.user_id:
            self.create_user_stats()
        else:
            self.create_guest_welcome()

        # Быстрый доступ
        self.create_quick_access()

        return self.frame

    def create_user_stats(self):
        """Создание статистики пользователя"""
        stats = self.db.get_user_stats(self.user_id)

        if not stats:
            return

        (level, experience, streak_days, completed_lectures_json,
         completed_tests_json, words_learned_json, total_time,
         tests_completed, avg_test_score) = stats

        completed_lectures = len(json.loads(completed_lectures_json)) if completed_lectures_json else 0
        words_learned = len(json.loads(words_learned_json)) if words_learned_json else 0

        stats_frame = ctk.CTkFrame(self.frame, fg_color=self.colors['card'])
        stats_frame.pack(fill="x", pady=10)

        stats_data = [
            ("Уровень", level, "🎯"),
            ("Опыт", f"{experience}/{level * 100}", "⭐"),
            ("Дней подряд", streak_days, "🔥"),
            ("Слов выучено", words_learned, "📖"),
            ("Тестов пройдено", tests_completed, "📝"),
            ("Средний балл", f"{avg_test_score:.1f}%" if avg_test_score else "0%", "📊"),
            ("Лекций пройдено", completed_lectures, "🎓"),
            ("Время обучения", f"{total_time} мин", "⏱️"),
        ]

        for i, (label, value, icon) in enumerate(stats_data):
            stat_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
            stat_frame.grid(row=i // 3, column=i % 3, padx=20, pady=20, sticky="nsew")

            icon_label = ctk.CTkLabel(stat_frame, text=icon, font=("Arial", 24))
            icon_label.pack()

            value_label = ctk.CTkLabel(stat_frame, text=str(value), font=("Arial", 28, "bold"))
            value_label.pack()

            label_label = ctk.CTkLabel(stat_frame, text=label, font=("Arial", 12), text_color="gray")
            label_label.pack()

    def create_guest_welcome(self):
        """Приветствие для гостя"""
        guest_frame = ctk.CTkFrame(self.frame, fg_color=self.colors['card'])
        guest_frame.pack(fill="x", pady=10)

        welcome_label = ctk.CTkLabel(
            guest_frame,
            text="Добро пожаловать в ShlepaLang!",
            font=("Arial", 20, "bold")
        )
        welcome_label.pack(pady=30)

        info_label = ctk.CTkLabel(
            guest_frame,
            text="Зарегистрируйтесь, чтобы сохранять свой прогресс и получать достижения!",
            font=("Arial", 14),
            wraplength=600
        )
        info_label.pack(pady=(0, 30))

    def create_quick_access(self):
        """Быстрый доступ к функциям"""
        quick_access_label = ctk.CTkLabel(
            self.frame,
            text="Быстрый доступ",
            font=("Arial", 20, "bold")
        )
        quick_access_label.pack(anchor="w", pady=(30, 10))

        quick_access_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        quick_access_frame.pack(fill="x", pady=10)

        # Определяем команды (будут связаны с родительским окном)
        quick_buttons = [
            ("Изучить новые слова", "dictionary", "📚"),
            ("Пройти тест", "tests", "📝"),
            ("Поиграть в игру", "games", "🎮"),
            ("Читать лекции", "lectures", "🎓"),
        ]

        for i, (text, screen, icon) in enumerate(quick_buttons):
            btn = ctk.CTkButton(
                quick_access_frame,
                text=f"{icon} {text}",
                command=lambda s=screen: self.parent.show_screen(s),
                height=60,
                fg_color=self.colors['card'],
                hover_color=self.colors['primary']
            )
            btn.grid(row=i // 2, column=i % 2, padx=10, pady=10, sticky="nsew")
            quick_access_frame.grid_columnconfigure(i % 2, weight=1)

    def destroy(self):
        """Уничтожение экрана"""
        if self.frame:
            self.frame.destroy()