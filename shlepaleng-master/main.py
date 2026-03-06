import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import os
import sys

# Добавляем текущую директорию в путь для импортов
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import APP_TITLE, APP_GEOMETRY, COLORS
from database import Database
from auth import AuthScreen
from sidebar import Sidebar

# Импортируем экраны напрямую
from screens.dashboard import DashboardScreen
from screens.dictionary import DictionaryScreen
from screens.lectures import LecturesScreen
from screens.tests import TestsScreen
from screens.games import GamesScreen
from screens.progress import ProgressScreen
from screens.admin import AdminScreen
from screens.sentence_builder_game import SentenceBuilderGame


class ShlepaLang:
    def __init__(self):
        self.app = ctk.CTk()
        self.app.title(APP_TITLE)
        self.app.geometry(APP_GEOMETRY)

        # Инициализация базы данных
        self.db = Database()

        # Текущий пользователь
        self.current_user = None
        self.current_user_role = None

        # Цветовая схема
        self.colors = COLORS

        # Создаем главный контейнер
        self.main_container = ctk.CTkFrame(self.app, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        # Инициализация экранов
        self.auth_screen = AuthScreen(self, self.db, self.on_login_success)
        self.sidebar = Sidebar(self, self.db, self.colors, self.show_screen, self.logout)

        # Текущий активный экран
        self.current_screen = None

        # Показываем экран входа
        self.show_login()

    def show_login(self):
        """Отображение экрана входа"""
        self.auth_screen.show_login(self.main_container)

    def on_login_success(self, user_id, role):
        """Обработчик успешного входа"""
        self.current_user = user_id
        self.current_user_role = role

        # Показываем главное меню
        self.show_main_menu()

        # Для админа сразу показываем админ-панель
        if role == 'admin':
            self.show_admin_panel()

    def show_main_menu(self):
        """Отображение главного меню"""
        # Очищаем контейнер
        for widget in self.main_container.winfo_children():
            widget.destroy()

        # Создаем боковое меню
        self.sidebar.create(self.main_container, self.current_user, self.current_user_role)

        # Основная область контента
        self.content_area = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_area.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        # Показываем главную страницу
        self.show_dashboard()

    def show_screen(self, screen_name):
        """Отображение выбранного экрана"""
        # Очищаем область контента
        for widget in self.content_area.winfo_children():
            widget.destroy()

        # Уничтожаем текущий экран если есть
        if self.current_screen:
            self.current_screen.destroy()

        # Создаем новый экран
        try:
            if screen_name == "dashboard":
                self.current_screen = DashboardScreen(self, self.db, self.colors, self.current_user)
            elif screen_name == "dictionary":
                self.current_screen = DictionaryScreen(self, self.db, self.colors, self.current_user,
                                                    self.current_user_role)
            elif screen_name == "lectures":
                self.current_screen = LecturesScreen(self, self.db, self.colors, self.current_user,
                                                    self.current_user_role)
            elif screen_name == "tests":
                self.current_screen = TestsScreen(self, self.db, self.colors, self.current_user, self.current_user_role)
            elif screen_name == "games":
                self.current_screen = GamesScreen(self, self.db, self.colors, self.current_user)
            elif screen_name == "progress":
                self.current_screen = ProgressScreen(self, self.db, self.colors, self.current_user)
            elif screen_name == "admin":
                self.current_screen = AdminScreen(self, self.db, self.colors, self.current_user)
            elif screen_name == "sentence_builder" or screen_name == "Составь предложение":  # ИСПРАВЛЕНО: принимаем оба названия
                self.current_screen = SentenceBuilderGame(self, self.db, self.colors, self.current_user)
            else:
                return

            # Отображаем экран
            frame = self.current_screen.create(self.content_area)
            if frame:
                frame.pack(fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить экран: {str(e)}")
            import traceback
            traceback.print_exc()

    def show_dashboard(self):
        """Отображение главной страницы"""
        self.show_screen("dashboard")

    def show_dictionary(self):
        """Отображение словаря"""
        self.show_screen("dictionary")

    def show_lectures(self):
        """Отображение лекций"""
        self.show_screen("lectures")

    def show_tests(self):
        """Отображение тестов"""
        self.show_screen("tests")

    def show_games(self):
        """Отображение игр"""
        self.show_screen("games")

    def show_progress(self):
        """Отображение прогресса"""
        self.show_screen("progress")

    def show_admin_panel(self):
        """Отображение админ-панели"""
        self.show_screen("admin")

    # Методы для вызова диалогов из других экранов
    def show_add_word_dialog(self):
        """Показать диалог добавления слова"""
        if hasattr(self.current_screen, 'show_add_word_dialog'):
            self.current_screen.show_add_word_dialog()

    def show_add_lecture_dialog(self):
        """Показать диалог добавления лекции"""
        if hasattr(self.current_screen, 'show_add_lecture_dialog'):
            self.current_screen.show_add_lecture_dialog()

    def show_add_test_dialog(self):
        """Показать диалог добавления теста"""
        if hasattr(self.current_screen, 'show_add_test_dialog'):
            self.current_screen.show_add_test_dialog()

    def logout(self):
        """Выход из системы"""
        self.current_user = None
        self.current_user_role = None

        # Уничтожаем боковое меню
        self.sidebar.destroy()

        # Очищаем контейнер
        for widget in self.main_container.winfo_children():
            widget.destroy()

        # Показываем экран входа
        self.show_login()

    def run(self):
        """Запуск приложения"""
        try:
            self.app.mainloop()
        finally:
            self.db.close()

    def show_sentence_builder(self):
        """Отображение игры 'Составь предложение'"""
        self.show_screen("sentence_builder")  # ИСПРАВЛЕНО: теперь используем английское название для вызова

if __name__ == "__main__":
    app = ShlepaLang()
    app.run()