
import customtkinter as ctk
from tkinter import messagebox, ttk
import json


class DictionaryScreen:
    def __init__(self, parent, db, colors, user_id, user_role):
        self.parent = parent
        self.db = db
        self.colors = colors
        self.user_id = user_id
        self.user_role = user_role
        self.frame = None
        self.words_tree = None
        self.search_entry = None
        self.category_var = None

    def create(self, container):
        """Создание экрана словаря"""
        self.frame = ctk.CTkFrame(container, fg_color="transparent")

        # Заголовок и поиск
        self.create_header()

        # Фильтры
        self.create_filters()

        # Таблица/список слов
        self.create_words_table()

        # Загрузка слов
        self.load_words()

        return self.frame

    def create_header(self):
        """Создание заголовка и поиска"""
        header_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        title_label = ctk.CTkLabel(
            header_frame,
            text="📚 Словарь",
            font=("Arial", 24, "bold")
        )
        title_label.pack(side="left", anchor="w")

        # Поиск
        search_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        search_frame.pack(side="right", anchor="e")

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Поиск слова...",
            width=200
        )
        self.search_entry.pack(side="left", padx=(0, 10))

        search_button = ctk.CTkButton(
            search_frame,
            text="Найти",
            command=self.search_word,
            width=80
        )
        search_button.pack(side="left")

    def create_filters(self):
        """Создание фильтров"""
        filter_frame = ctk.CTkFrame(self.frame, fg_color=self.colors['card'])
        filter_frame.pack(fill="x", pady=(0, 20))

        categories = self.db.get_categories()
        self.category_var = ctk.StringVar(value="Все категории")

        category_label = ctk.CTkLabel(filter_frame, text="Категория:", font=("Arial", 12))
        category_label.pack(side="left", padx=(20, 10), pady=10)

        category_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=["Все категории"] + categories,
            variable=self.category_var,
            command=self.filter_words
        )
        category_menu.pack(side="left", padx=(0, 20), pady=10)

        # Кнопка добавления слова (только для админа)
        if self.user_role == 'admin':
            add_word_btn = ctk.CTkButton(
                filter_frame,
                text="+ Добавить слово",
                command=self.show_add_word_dialog,
                fg_color="green",
                hover_color="darkgreen"
            )
            add_word_btn.pack(side="right", padx=20, pady=10)

    def create_words_table(self):
        """Создание таблицы слов"""
        # Создаем фрейм для таблицы с прокруткой
        table_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True)

        # Таблица
        self.words_tree = ttk.Treeview(
            table_frame,
            columns=("english", "russian", "transcription", "category"),
            show="headings",
            height=15
        )

        # Настройка колонок
        self.words_tree.heading("english", text="Английский")
        self.words_tree.heading("russian", text="Русский")
        self.words_tree.heading("transcription", text="Транскрипция")
        self.words_tree.heading("category", text="Категория")

        self.words_tree.column("english", width=200)
        self.words_tree.column("russian", width=200)
        self.words_tree.column("transcription", width=150)
        self.words_tree.column("category", width=150)

        # Стилизация
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background=self.colors['card'],
                        fieldbackground=self.colors['card'],
                        foreground="white")
        style.configure("Treeview.Heading",
                        background=self.colors['primary'],
                        foreground="white")

        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.words_tree.yview)
        self.words_tree.configure(yscrollcommand=scrollbar.set)

        self.words_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_words(self, category=None, search=None):
        """Загрузка слов из базы данных"""
        # Очищаем текущий список
        for item in self.words_tree.get_children():
            self.words_tree.delete(item)

        # Получаем слова
        words = self.db.get_words(category, search)

        # Добавляем слова в таблицу
        for word in words:
            self.words_tree.insert("", "end", values=word)

    def search_word(self):
        """Поиск слова"""
        search_term = self.search_entry.get()
        category = self.category_var.get()
        self.load_words(category, search_term)

    def filter_words(self, category):
        """Фильтрация слов по категории"""
        search_term = self.search_entry.get()
        self.load_words(category, search_term)

    def show_add_word_dialog(self):
        """Диалог добавления слова"""
        dialog = ctk.CTkToplevel(self.parent.app)
        dialog.title("Добавить слово")
        dialog.geometry("400x400")
        dialog.grab_set()

        # Поля ввода
        ctk.CTkLabel(dialog, text="Английское слово:", font=("Arial", 12)).pack(pady=(20, 5))
        english_entry = ctk.CTkEntry(dialog, width=300)
        english_entry.pack(pady=(0, 10))

        ctk.CTkLabel(dialog, text="Русский перевод:", font=("Arial", 12)).pack(pady=(10, 5))
        russian_entry = ctk.CTkEntry(dialog, width=300)
        russian_entry.pack(pady=(0, 10))

        ctk.CTkLabel(dialog, text="Транскрипция:", font=("Arial", 12)).pack(pady=(10, 5))
        transcription_entry = ctk.CTkEntry(dialog, width=300)
        transcription_entry.pack(pady=(0, 10))

        ctk.CTkLabel(dialog, text="Категория:", font=("Arial", 12)).pack(pady=(10, 5))
        category_entry = ctk.CTkEntry(dialog, width=300, placeholder_text="Основные, Животные и т.д.")
        category_entry.pack(pady=(0, 20))

        # Кнопки
        def add_word():
            english = english_entry.get()
            russian = russian_entry.get()
            transcription = transcription_entry.get()
            category = category_entry.get()

            if not english or not russian:
                messagebox.showerror("Ошибка", "Заполните обязательные поля")
                return

            try:
                self.db.add_word(english, russian, transcription, category, self.user_id)
                messagebox.showinfo("Успех", "Слово успешно добавлено!")
                dialog.destroy()
                self.load_words()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Такое слово уже существует или ошибка БД: {str(e)}")

        add_button = ctk.CTkButton(
            dialog,
            text="Добавить",
            command=add_word,
            fg_color="green",
            width=300,
            height=40
        )
        add_button.pack(pady=10)

        cancel_button = ctk.CTkButton(
            dialog,
            text="Отмена",
            command=dialog.destroy,
            width=300,
            height=40,
            fg_color="gray"
        )
        cancel_button.pack(pady=(0, 20))

    def destroy(self):
        """Уничтожение экрана"""
        if self.frame:
            self.frame.destroy()