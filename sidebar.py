# sidebar.py
import customtkinter as ctk


class Sidebar:
    def __init__(self, parent, db, colors, on_menu_click, on_logout):
        self.parent = parent
        self.db = db
        self.colors = colors
        self.on_menu_click = on_menu_click
        self.on_logout = on_logout
        self.frame = None
        self.current_user = None

    def create(self, container, user_id, user_role):
        """Создание бокового меню"""
        self.current_user = user_id
        self.current_user_role = user_role

        self.frame = ctk.CTkFrame(container, width=250, fg_color=self.colors['card'])
        self.frame.pack(side="left", fill="y", padx=10, pady=10)

        # Заголовок
        title_label = ctk.CTkLabel(
            self.frame,
            text="ShlepaLang",
            font=("Arial", 20, "bold"),
            text_color=self.colors['accent']
        )
        title_label.pack(pady=(20, 10))

        # Информация о пользователе
        self.user_info_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.user_info_frame.pack(pady=10, padx=10)

        self.update_user_info()

        # Разделитель
        ctk.CTkLabel(self.frame, text="").pack(pady=5)

        # Кнопки меню
        self.create_menu_buttons()

        # Кнопка выхода
        logout_btn = ctk.CTkButton(
            self.frame,
            text="🚪 Выход",
            command=self.on_logout,
            fg_color="transparent",
            anchor="w",
            height=40,
            text_color="red"
        )
        logout_btn.pack(side="bottom", fill="x", padx=10, pady=20)

    def update_user_info(self):
        """Обновление информации о пользователе"""
        # Очищаем старую информацию
        for widget in self.user_info_frame.winfo_children():
            widget.destroy()

        if self.current_user:
            user_data = self.db.get_user_by_id(self.current_user)
            if user_data:
                username, level, experience = user_data

                username_label = ctk.CTkLabel(
                    self.user_info_frame,
                    text=f"👤 {username}",
                    font=("Arial", 14)
                )
                username_label.pack()

                level_label = ctk.CTkLabel(
                    self.user_info_frame,
                    text=f"Уровень: {level}",
                    font=("Arial", 12),
                    text_color="gray"
                )
                level_label.pack()
        else:
            guest_label = ctk.CTkLabel(
                self.user_info_frame,
                text="👤 Гость",
                font=("Arial", 14)
            )
            guest_label.pack()

    def create_menu_buttons(self):
        """Создание кнопок меню"""
        menu_buttons = [
            ("📊 Дашборд", "dashboard"),
            ("📚 Словарь", "dictionary"),
            ("🎓 Лекции", "lectures"),
            ("📝 Тесты", "tests"),
            ("🎮 Игры", "games"),
            ("📈 Прогресс", "progress"),
        ]

        if self.current_user_role == 'admin':
            menu_buttons.append(("⚙️ Админ-панель", "admin"))

        for text, command_key in menu_buttons:
            btn = ctk.CTkButton(
                self.frame,
                text=text,
                command=lambda k=command_key: self.on_menu_click(k),
                fg_color="transparent",
                anchor="w",
                height=40
            )
            btn.pack(fill="x", padx=10, pady=2)

    def destroy(self):
        """Уничтожение бокового меню"""
        if self.frame:
            self.frame.destroy()