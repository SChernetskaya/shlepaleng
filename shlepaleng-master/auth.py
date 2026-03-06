# auth.py
import customtkinter as ctk
from tkinter import messagebox
import sqlite3


class AuthScreen:
    def __init__(self, parent, db, on_login_success):
        self.parent = parent
        self.db = db
        self.on_login_success = on_login_success
        self.current_frame = None

        # Получаем цвета из родительского окна
        self.colors = parent.colors if hasattr(parent, 'colors') else {
            "primary": "#4B8BBE",
            "secondary": "#306998",
            "accent": "#FFD43B",
            "card": "#3C3F41"
        }

    def show_login(self, container):
        """Отображение экрана входа"""
        self.clear_container(container)

        frame = ctk.CTkFrame(container, fg_color=self.colors['card'])
        frame.place(relx=0.5, rely=0.5, anchor="center")

        # Заголовок
        title_label = ctk.CTkLabel(
            frame,
            text="ShlepaLang",
            font=("Arial", 32, "bold"),
            text_color=self.colors['accent']
        )
        title_label.pack(pady=(40, 20), padx=40)

        subtitle_label = ctk.CTkLabel(
            frame,
            text="Изучение английского языка",
            font=("Arial", 16),
            text_color="gray"
        )
        subtitle_label.pack(pady=(0, 30))

        # Поля для ввода
        self.login_username = ctk.CTkEntry(
            frame,
            placeholder_text="Имя пользователя",
            width=250,
            height=40
        )
        self.login_username.pack(pady=10, padx=40)

        self.login_password = ctk.CTkEntry(
            frame,
            placeholder_text="Пароль",
            show="*",
            width=250,
            height=40
        )
        self.login_password.pack(pady=10, padx=40)

        # Кнопки
        login_button = ctk.CTkButton(
            frame,
            text="Войти",
            command=self.login,
            width=250,
            height=40,
            fg_color=self.colors['primary'],
            hover_color=self.colors['secondary']
        )
        login_button.pack(pady=10, padx=40)

        register_button = ctk.CTkButton(
            frame,
            text="Зарегистрироваться",
            command=lambda: self.show_register(container),
            width=250,
            height=40,
            fg_color="transparent",
            border_color=self.colors['primary'],
            border_width=2,
            text_color=self.colors['primary']
        )
        register_button.pack(pady=(10, 30), padx=40)

        # Кнопка гостя
        guest_button = ctk.CTkButton(
            frame,
            text="Войти как гость",
            command=self.login_as_guest,
            width=250,
            height=30,
            fg_color="transparent",
            text_color="gray"
        )
        guest_button.pack(pady=(0, 20), padx=40)

        self.current_frame = frame

    def show_register(self, container):
        """Отображение экрана регистрации (БЕЗ EMAIL)"""
        self.clear_container(container)

        frame = ctk.CTkFrame(container, fg_color=self.colors['card'])
        frame.place(relx=0.5, rely=0.5, anchor="center")

        title_label = ctk.CTkLabel(
            frame,
            text="Регистрация",
            font=("Arial", 24, "bold")
        )
        title_label.pack(pady=(30, 20), padx=40)

        # Поля для регистрации (БЕЗ EMAIL)
        self.reg_username = ctk.CTkEntry(
            frame,
            placeholder_text="Имя пользователя",
            width=250,
            height=40
        )
        self.reg_username.pack(pady=10, padx=40)

        # ПОЛЕ EMAIL УДАЛЕНО

        self.reg_password = ctk.CTkEntry(
            frame,
            placeholder_text="Пароль",
            show="*",
            width=250,
            height=40
        )
        self.reg_password.pack(pady=10, padx=40)

        self.reg_confirm_password = ctk.CTkEntry(
            frame,
            placeholder_text="Подтвердите пароль",
            show="*",
            width=250,
            height=40
        )
        self.reg_confirm_password.pack(pady=10, padx=40)

        # Кнопки
        register_button = ctk.CTkButton(
            frame,
            text="Зарегистрироваться",
            command=self.register,
            width=250,
            height=40,
            fg_color=self.colors['primary']
        )
        register_button.pack(pady=10, padx=40)

        back_button = ctk.CTkButton(
            frame,
            text="Назад",
            command=lambda: self.show_login(container),
            width=250,
            height=40,
            fg_color="transparent",
            border_color=self.colors['primary'],
            border_width=2,
            text_color=self.colors['primary']
        )
        back_button.pack(pady=(10, 30), padx=40)

        self.current_frame = frame

    def login(self):
        """Вход пользователя"""
        username = self.login_username.get()
        password = self.login_password.get()

        if not username or not password:
            messagebox.showerror("Ошибка", "Заполните все поля")
            return

        password_hash = self.db.hash_password(password)
        user = self.db.get_user(username, password_hash)

        if user:
            user_id, username, role = user
            self.db.update_last_login(user_id)

            messagebox.showinfo("Успех", f"Добро пожаловать, {username}!")
            self.on_login_success(user_id, role)
        else:
            messagebox.showerror("Ошибка", "Неверное имя пользователя или пароль")

    def login_as_guest(self):
        """Вход как гость"""
        messagebox.showinfo("Гость", "Вы вошли как гость. Прогресс не будет сохраняться.")
        self.on_login_success(None, 'guest')

    def register(self):
        """Регистрация нового пользователя (БЕЗ EMAIL)"""
        username = self.reg_username.get()
        password = self.reg_password.get()
        confirm_password = self.reg_confirm_password.get()

        if not all([username, password, confirm_password]):
            messagebox.showerror("Ошибка", "Заполните все поля")
            return

        if password != confirm_password:
            messagebox.showerror("Ошибка", "Пароли не совпадают")
            return

        if len(password) < 6:
            messagebox.showerror("Ошибка", "Пароль должен содержать минимум 6 символов")
            return

        password_hash = self.db.hash_password(password)

        try:
            # Используем username как email (временное решение)
            # Или можно сделать email необязательным полем
            email = f"{username}@shlepalang.local"  # Генерируем временный email
            user_id = self.db.create_user(username, email, password_hash)
            messagebox.showinfo("Успех", "Регистрация успешна! Теперь вы можете войти.")
            self.show_login(self.parent.main_container)
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Пользователь с таким именем уже существует")

    def clear_container(self, container):
        """Очистка контейнера"""
        for widget in container.winfo_children():
            widget.destroy()
        self.current_frame = None