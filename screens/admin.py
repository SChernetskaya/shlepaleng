# screens/admin.py
import customtkinter as ctk
from tkinter import messagebox


class AdminScreen:
    def __init__(self, parent, db, colors, user_id):
        self.parent = parent
        self.db = db
        self.colors = colors
        self.user_id = user_id
        self.frame = None

    def create(self, container):
        """Создание админ-панели"""
        self.frame = ctk.CTkFrame(container, fg_color="transparent")

        title_label = ctk.CTkLabel(
            self.frame,
            text="⚙️ Админ-панель",
            font=("Arial", 24, "bold")
        )
        title_label.pack(anchor="w", pady=(0, 20))

        # Статистика системы
        self.create_system_stats()

        # Управление контентом
        self.create_content_management()

        return self.frame

    def create_system_stats(self):
        """Создание статистики системы"""
        stats_label = ctk.CTkLabel(
            self.frame,
            text="Статистика системы:",
            font=("Arial", 18, "bold")
        )
        stats_label.pack(anchor="w", pady=(20, 10))

        stats = self.db.get_system_stats()

        stats_frame = ctk.CTkFrame(self.frame, fg_color=self.colors['card'])
        stats_frame.pack(fill="x", pady=10)

        stats_data = [
            ("👥 Пользователей", stats['users']),
            ("👑 Администраторов", stats['admins']),
            ("📚 Слов в словаре", stats['words']),
            ("🎓 Лекций", stats['lectures']),
            ("📝 Тестов", stats['tests']),
        ]

        for i, (label, value) in enumerate(stats_data):
            stat_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
            stat_frame.grid(row=i // 3, column=i % 3, padx=20, pady=20, sticky="nsew")

            value_label = ctk.CTkLabel(stat_frame, text=str(value), font=("Arial", 24, "bold"))
            value_label.pack()

            label_label = ctk.CTkLabel(stat_frame, text=label, font=("Arial", 12), text_color="gray")
            label_label.pack()

    def create_content_management(self):
        """Создание панели управления контентом"""
        manage_label = ctk.CTkLabel(
            self.frame,
            text="Управление контентом:",
            font=("Arial", 18, "bold")
        )
        manage_label.pack(anchor="w", pady=(30, 10))

        manage_frame = ctk.CTkFrame(self.frame, fg_color=self.colors['card'])
        manage_frame.pack(fill="x", pady=10)

        # Кнопки управления
        manage_buttons = [
            ("➕ Добавить слово", self.parent.show_add_word_dialog),
            ("📖 Добавить лекцию", self.parent.show_add_lecture_dialog),
            ("📝 Добавить тест", self.parent.show_add_test_dialog),
            ("👥 Управление пользователями", self.show_user_management),
            ("📊 Подробная статистика", self.show_detailed_stats),
        ]

        for i, (text, command) in enumerate(manage_buttons):
            btn = ctk.CTkButton(
                manage_frame,
                text=text,
                command=command,
                height=50,
                fg_color=self.colors['primary'],
                hover_color=self.colors['secondary']
            )
            btn.grid(row=i // 2, column=i % 2, padx=20, pady=20, sticky="nsew")
            manage_frame.grid_columnconfigure(i % 2, weight=1)

    def show_user_management(self):
        """Управление пользователями (заглушка)"""
        messagebox.showinfo("Скоро", "Управление пользователями будет доступно в следующем обновлении!")

    def show_detailed_stats(self):
        """Подробная статистика (заглушка)"""
        messagebox.showinfo("Скоро", "Подробная статистика будет доступна в следующем обновлении!")

    def destroy(self):
        """Уничтожение экрана"""
        if self.frame:
            self.frame.destroy()