import customtkinter as ctk
from tkinter import messagebox, ttk
import json


class AdminScreen:
    def __init__(self, parent, db, colors, user_id):
        self.parent = parent
        self.db = db
        self.colors = colors
        self.user_id = user_id
        self.frame = None
        self.current_tab = "lectures"  # По умолчанию показываем лекции

    def create(self, container):
        """Создание админ-панели"""
        self.frame = ctk.CTkFrame(container, fg_color="transparent")

        # Заголовок
        title_label = ctk.CTkLabel(
            self.frame,
            text="⚙️ Админ-панель",
            font=("Arial", 28, "bold")
        )
        title_label.pack(anchor="w", pady=(0, 20))

        # Статистика системы
        self.create_system_stats()

        # Вкладки управления
        self.create_tabs()

        return self.frame

    def create_system_stats(self):
        """Создание статистики системы"""
        stats_label = ctk.CTkLabel(
            self.frame,
            text="📊 Статистика системы:",
            font=("Arial", 22, "bold")
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

        # Создаем сетку 2x3 (2 строки, 3 колонки)
        for i, (label, value) in enumerate(stats_data):
            row = i // 3
            col = i % 3

            stat_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
            stat_frame.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")
            stats_frame.grid_columnconfigure(col, weight=1)
            stats_frame.grid_rowconfigure(row, weight=1)

            value_label = ctk.CTkLabel(
                stat_frame,
                text=str(value),
                font=("Arial", 28, "bold")
            )
            value_label.pack()

            label_label = ctk.CTkLabel(
                stat_frame,
                text=label,
                font=("Arial", 14),
                text_color="gray"
            )
            label_label.pack()

    def create_tabs(self):
        """Создание вкладок для управления контентом"""
        # Создаем вкладки
        self.tab_view = ctk.CTkTabview(self.frame, fg_color="transparent")
        self.tab_view.pack(fill="both", expand=True, pady=(20, 0))

        # Добавляем вкладки
        self.tab_lectures = self.tab_view.add("🎓 Лекции")
        self.tab_tests = self.tab_view.add("📝 Тесты")
        self.tab_words = self.tab_view.add("📚 Слова")

        # Наполняем вкладки
        self.create_lectures_tab()
        self.create_tests_tab()
        self.create_words_tab()

    # ==================== ВКЛАДКА ЛЕКЦИЙ ====================

    def create_lectures_tab(self):
        """Создание вкладки управления лекциями"""

        # ВЕРХНЯЯ ПАНЕЛЬ С КНОПКАМИ
        top_panel = ctk.CTkFrame(self.tab_lectures, fg_color="transparent")
        top_panel.pack(fill="x", pady=(20, 10))

        # Заголовок и кнопка добавления
        header_frame = ctk.CTkFrame(top_panel, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            header_frame,
            text="📋 Управление лекциями",
            font=("Arial", 18, "bold")
        ).pack(side="left")

        add_btn = ctk.CTkButton(
            header_frame,
            text="➕ Добавить лекцию",
            command=self.parent.show_add_lecture_dialog,
            fg_color="green",
            hover_color="darkgreen",
            height=40,
            width=200
        )
        add_btn.pack(side="right")

        # ПАНЕЛЬ ДЕЙСТВИЙ (кнопки редактирования/удаления)
        action_frame = ctk.CTkFrame(top_panel, fg_color=self.colors['card'], height=60)
        action_frame.pack(fill="x", pady=5)
        action_frame.pack_propagate(False)

        # Кнопки действий
        edit_btn = ctk.CTkButton(
            action_frame,
            text="✏️ Редактировать",
            command=self.edit_selected_lecture,
            width=150,
            height=35
        )
        edit_btn.pack(side="left", padx=10, pady=12)

        delete_btn = ctk.CTkButton(
            action_frame,
            text="🗑️ Удалить",
            command=self.delete_selected_lecture,
            width=150,
            height=35,
            fg_color="#D32F2F",
            hover_color="#B71C1C"
        )
        delete_btn.pack(side="left", padx=10, pady=12)

        refresh_btn = ctk.CTkButton(
            action_frame,
            text="🔄 Обновить",
            command=self.load_lectures,
            width=150,
            height=35,
            fg_color="#1976D2",
            hover_color="#0D47A1"
        )
        refresh_btn.pack(side="left", padx=10, pady=12)

        # Информация о выбранном элементе
        self.lecture_selected_info = ctk.CTkLabel(
            action_frame,
            text="Выберите лекцию из списка",
            font=("Arial", 12),
            text_color="gray"
        )
        self.lecture_selected_info.pack(side="right", padx=20, pady=12)

        # ТАБЛИЦА
        table_container = ctk.CTkFrame(self.tab_lectures, fg_color="transparent")
        table_container.pack(fill="both", expand=True, pady=(0, 10))

        # Создаем фрейм для таблицы с прокруткой
        table_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        table_frame.pack(fill="both", expand=True)

        # Таблица лекций
        columns = ("id", "Название", "Категория", "Сложность", "Дата создания")
        self.lectures_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=12
        )

        # Настройка колонок
        self.lectures_tree.heading("id", text="ID")
        self.lectures_tree.heading("Название", text="Название")
        self.lectures_tree.heading("Категория", text="Категория")
        self.lectures_tree.heading("Сложность", text="Сложность")
        self.lectures_tree.heading("Дата создания", text="Дата создания")

        self.lectures_tree.column("id", width=50, anchor="center")
        self.lectures_tree.column("Название", width=350)
        self.lectures_tree.column("Категория", width=150, anchor="center")
        self.lectures_tree.column("Сложность", width=80, anchor="center")
        self.lectures_tree.column("Дата создания", width=150, anchor="center")

        # Стилизация
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background=self.colors['card'],
                        fieldbackground=self.colors['card'],
                        foreground="white",
                        rowheight=30)
        style.configure("Treeview.Heading",
                        background=self.colors['primary'],
                        foreground="white",
                        font=("Arial", 11, "bold"))
        style.map("Treeview",
                  background=[('selected', self.colors['primary'])])

        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.lectures_tree.yview)
        self.lectures_tree.configure(yscrollcommand=scrollbar.set)

        self.lectures_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Привязываем событие выбора
        self.lectures_tree.bind('<<TreeviewSelect>>', self.on_lecture_select)

        # Загружаем лекции
        self.load_lectures()

    def on_lecture_select(self, event):
        """Обработчик выбора лекции"""
        selected = self.lectures_tree.selection()
        if selected:
            values = self.lectures_tree.item(selected[0])['values']
            if values:
                self.lecture_selected_info.configure(
                    text=f"✓ Выбрано: {values[1]} (ID: {values[0]})",
                    text_color="#4CAF50"
                )
        else:
            self.lecture_selected_info.configure(
                text="Выберите лекцию из списка",
                text_color="gray"
            )

    def load_lectures(self):
        """Загрузка лекций в таблицу"""
        # Очищаем текущий список
        for item in self.lectures_tree.get_children():
            self.lectures_tree.delete(item)

        # Получаем лекции из БД
        self.db.cursor.execute("""
            SELECT id, title, category, difficulty_level, created_date 
            FROM lectures 
            ORDER BY created_date DESC
        """)
        lectures = self.db.cursor.fetchall()

        # Добавляем в таблицу
        for lecture in lectures:
            self.lectures_tree.insert("", "end", values=lecture)

    def edit_selected_lecture(self):
        """Редактирование выбранной лекции"""
        selected = self.lectures_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите лекцию для редактирования")
            return

        # Получаем ID лекции
        lecture_id = self.lectures_tree.item(selected[0])['values'][0]

        # Получаем данные лекции
        self.db.cursor.execute("SELECT * FROM lectures WHERE id=?", (lecture_id,))
        lecture = self.db.cursor.fetchone()

        if lecture:
            self.show_edit_lecture_dialog(lecture)

    def show_edit_lecture_dialog(self, lecture):
        """Диалог редактирования лекции """
        dialog = ctk.CTkToplevel(self.parent.app)
        dialog.title("Редактировать лекцию")
        dialog.geometry("700x700")  # Увеличил размер
        dialog.minsize(600, 600)  # Минимальный размер
        dialog.grab_set()

        # Создаем прокручиваемую область для всего содержимого
        main_frame = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Поля ввода
        ctk.CTkLabel(main_frame, text="Название лекции:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
        title_entry = ctk.CTkEntry(main_frame, width=600, height=35)
        title_entry.insert(0, lecture[1])
        title_entry.pack(pady=(0, 15), fill="x")

        ctk.CTkLabel(main_frame, text="Категория:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(5, 5))
        category_entry = ctk.CTkEntry(main_frame, width=600, height=35,
                                      placeholder_text="Например: Основы, Грамматика, Лексика")
        if lecture[3]:
            category_entry.insert(0, lecture[3])
        category_entry.pack(pady=(0, 15), fill="x")

        # Сложность
        difficulty_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        difficulty_frame.pack(fill="x", pady=(5, 15))

        ctk.CTkLabel(difficulty_frame, text="Уровень сложности (1-5):", font=("Arial", 12, "bold")).pack(anchor="w")

        difficulty_var = ctk.StringVar(value=str(lecture[4]))

        # Создаем слайдер для выбора сложности
        difficulty_slider = ctk.CTkSlider(
            difficulty_frame,
            from_=1,
            to=5,
            number_of_steps=4,
            command=lambda v: difficulty_var.set(str(int(v)))
        )
        difficulty_slider.set(int(lecture[4]))
        difficulty_slider.pack(pady=(5, 5), fill="x")

        # Индикатор сложности
        difficulty_indicator = ctk.CTkLabel(
            difficulty_frame,
            textvariable=difficulty_var,
            font=("Arial", 14, "bold")
        )
        difficulty_indicator.pack()

        ctk.CTkLabel(main_frame, text="Содержание лекции:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))

        # Текстовое поле с прокруткой
        content_text = ctk.CTkTextbox(main_frame, width=600, height=300)
        content_text.insert("1.0", lecture[2])
        content_text.pack(pady=(0, 20), fill="both", expand=True)



        # Фрейм для кнопок (всегда видимый)
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))

        def save_changes():
            title = title_entry.get()
            category = category_entry.get()
            difficulty = difficulty_var.get()
            content = content_text.get("1.0", "end").strip()

            if not title or not content:
                messagebox.showerror("Ошибка", "Заполните обязательные поля")
                return

            try:
                self.db.cursor.execute("""
                    UPDATE lectures 
                    SET title=?, content=?, category=?, difficulty_level=? 
                    WHERE id=?
                """, (title, content, category if category else None, int(difficulty), lecture[0]))
                self.db.commit()
                messagebox.showinfo("Успех", "Лекция успешно обновлена!")
                dialog.destroy()
                self.load_lectures()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при обновлении: {str(e)}")

        save_button = ctk.CTkButton(
            button_frame,
            text="💾 Сохранить изменения",
            command=save_changes,
            fg_color="green",
            hover_color="darkgreen",
            width=250,
            height=45,
            font=("Arial", 14, "bold")
        )
        save_button.pack(side="left", padx=(0, 10))

        cancel_button = ctk.CTkButton(
            button_frame,
            text="✖ Отмена",
            command=dialog.destroy,
            width=250,
            height=45,
            fg_color="gray",
            hover_color="#555555",
            font=("Arial", 14)
        )
        cancel_button.pack(side="left")

    def delete_selected_lecture(self):
        """Удаление выбранной лекции"""
        selected = self.lectures_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите лекцию для удаления")
            return

        # Подтверждение удаления
        if not messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту лекцию?"):
            return

        # Получаем ID лекции
        lecture_id = self.lectures_tree.item(selected[0])['values'][0]

        try:
            # Удаляем связанные тесты (опционально - можно оставить)
            self.db.cursor.execute("UPDATE tests SET lecture_id=NULL WHERE lecture_id=?", (lecture_id,))
            # Удаляем лекцию
            self.db.cursor.execute("DELETE FROM lectures WHERE id=?", (lecture_id,))
            self.db.commit()
            messagebox.showinfo("Успех", "Лекция успешно удалена!")
            self.load_lectures()
            # Сбрасываем выделение
            self.lecture_selected_info.configure(
                text="Выберите лекцию из списка",
                text_color="gray"
            )
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении: {str(e)}")

    # ==================== ВКЛАДКА ТЕСТОВ ====================

    def create_tests_tab(self):
        """Создание вкладки управления тестами"""

        # ВЕРХНЯЯ ПАНЕЛЬ С КНОПКАМИ
        top_panel = ctk.CTkFrame(self.tab_tests, fg_color="transparent")
        top_panel.pack(fill="x", pady=(20, 10))

        # Заголовок и кнопка добавления
        header_frame = ctk.CTkFrame(top_panel, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            header_frame,
            text="📋 Управление тестами",
            font=("Arial", 18, "bold")
        ).pack(side="left")

        add_btn = ctk.CTkButton(
            header_frame,
            text="➕ Добавить тест",
            command=self.parent.show_add_test_dialog,
            fg_color="green",
            hover_color="darkgreen",
            height=40,
            width=200
        )
        add_btn.pack(side="right")

        # ПАНЕЛЬ ДЕЙСТВИЙ
        action_frame = ctk.CTkFrame(top_panel, fg_color=self.colors['card'], height=60)
        action_frame.pack(fill="x", pady=5)
        action_frame.pack_propagate(False)

        edit_btn = ctk.CTkButton(
            action_frame,
            text="✏️ Редактировать",
            command=self.edit_selected_test,
            width=150,
            height=35
        )
        edit_btn.pack(side="left", padx=10, pady=12)

        delete_btn = ctk.CTkButton(
            action_frame,
            text="🗑️ Удалить",
            command=self.delete_selected_test,
            width=150,
            height=35,
            fg_color="#D32F2F",
            hover_color="#B71C1C"
        )
        delete_btn.pack(side="left", padx=10, pady=12)

        refresh_btn = ctk.CTkButton(
            action_frame,
            text="🔄 Обновить",
            command=self.load_tests,
            width=150,
            height=35,
            fg_color="#1976D2",
            hover_color="#0D47A1"
        )
        refresh_btn.pack(side="left", padx=10, pady=12)

        self.test_selected_info = ctk.CTkLabel(
            action_frame,
            text="Выберите тест из списка",
            font=("Arial", 12),
            text_color="gray"
        )
        self.test_selected_info.pack(side="right", padx=20, pady=12)

        # ТАБЛИЦА
        table_container = ctk.CTkFrame(self.tab_tests, fg_color="transparent")
        table_container.pack(fill="both", expand=True, pady=(0, 10))

        table_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        table_frame.pack(fill="both", expand=True)

        # Таблица тестов
        columns = ("id", "Название", "Связанная лекция", "Вопросов", "Дата создания")
        self.tests_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=12
        )

        # Настройка колонок
        self.tests_tree.heading("id", text="ID")
        self.tests_tree.heading("Название", text="Название")
        self.tests_tree.heading("Связанная лекция", text="Связанная лекция")
        self.tests_tree.heading("Вопросов", text="Вопросов")
        self.tests_tree.heading("Дата создания", text="Дата создания")

        self.tests_tree.column("id", width=50, anchor="center")
        self.tests_tree.column("Название", width=300)
        self.tests_tree.column("Связанная лекция", width=200)
        self.tests_tree.column("Вопросов", width=80, anchor="center")
        self.tests_tree.column("Дата создания", width=150, anchor="center")

        # Стилизация
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background=self.colors['card'],
                        fieldbackground=self.colors['card'],
                        foreground="white",
                        rowheight=30)
        style.configure("Treeview.Heading",
                        background=self.colors['primary'],
                        foreground="white",
                        font=("Arial", 11, "bold"))
        style.map("Treeview",
                  background=[('selected', self.colors['primary'])])

        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tests_tree.yview)
        self.tests_tree.configure(yscrollcommand=scrollbar.set)

        self.tests_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Привязываем событие выбора
        self.tests_tree.bind('<<TreeviewSelect>>', self.on_test_select)

        # Загружаем тесты
        self.load_tests()

    def on_test_select(self, event):
        """Обработчик выбора теста"""
        selected = self.tests_tree.selection()
        if selected:
            values = self.tests_tree.item(selected[0])['values']
            if values:
                self.test_selected_info.configure(
                    text=f"✓ Выбрано: {values[1]} (ID: {values[0]})",
                    text_color="#4CAF50"
                )
        else:
            self.test_selected_info.configure(
                text="Выберите тест из списка",
                text_color="gray"
            )

    def load_tests(self):
        """Загрузка тестов в таблицу"""
        # Очищаем текущий список
        for item in self.tests_tree.get_children():
            self.tests_tree.delete(item)

        # Получаем тесты из БД
        self.db.cursor.execute("""
            SELECT t.id, t.title, 
                   COALESCE(l.title, '—') as lecture_title,
                   CASE 
                       WHEN json_valid(t.questions) THEN json_array_length(t.questions)
                       ELSE 0
                   END as questions_count,
                   t.created_date
            FROM tests t
            LEFT JOIN lectures l ON t.lecture_id = l.id
            ORDER BY t.created_date DESC
        """)
        tests = self.db.cursor.fetchall()

        # Добавляем в таблицу
        for test in tests:
            self.tests_tree.insert("", "end", values=test)

    def edit_selected_test(self):
        """Редактирование выбранного теста"""
        selected = self.tests_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите тест для редактирования")
            return

        # Получаем ID теста
        test_id = self.tests_tree.item(selected[0])['values'][0]

        # Получаем данные теста
        self.db.cursor.execute("SELECT * FROM tests WHERE id=?", (test_id,))
        test = self.db.cursor.fetchone()

        if test:
            self.show_edit_test_dialog(test)

    def show_edit_test_dialog(self, test):
        """Диалог редактирования теста"""
        dialog = ctk.CTkToplevel(self.parent.app)
        dialog.title("Редактировать тест")
        dialog.geometry("600x650")
        dialog.grab_set()

        # Поля ввода
        ctk.CTkLabel(dialog, text="Название теста:", font=("Arial", 12)).pack(pady=(20, 5))
        title_entry = ctk.CTkEntry(dialog, width=500)
        title_entry.insert(0, test[1])
        title_entry.pack(pady=(0, 10))

        ctk.CTkLabel(dialog, text="Связанная лекция (опционально):", font=("Arial", 12)).pack(pady=(10, 5))

        lectures = self.db.get_lectures()
        lecture_options = ["Без лекции"] + [f"{lec[0]}: {lec[1]}" for lec in lectures]

        lecture_var = ctk.StringVar(value="Без лекции")

        # Если есть связанная лекция, выбираем её
        if test[2]:
            for opt in lecture_options:
                if opt.startswith(str(test[2])):
                    lecture_var.set(opt)
                    break

        lecture_menu = ctk.CTkOptionMenu(dialog, values=lecture_options, variable=lecture_var, width=500)
        lecture_menu.pack(pady=(0, 10))

        # Вопросы теста
        questions_label = ctk.CTkLabel(dialog, text="Вопросы теста:", font=("Arial", 12, "bold"))
        questions_label.pack(pady=(10, 5))

        # Контейнер для вопросов с прокруткой
        questions_container = ctk.CTkFrame(dialog, fg_color="transparent")
        questions_container.pack(fill="both", expand=True, pady=5)

        questions_frame = ctk.CTkScrollableFrame(questions_container, width=500, height=250)
        questions_frame.pack(fill="both", expand=True)

        # Загружаем существующие вопросы
        questions = json.loads(test[3])
        question_widgets = []

        for q_idx, q_data in enumerate(questions):
            self.create_question_widget(questions_frame, question_widgets, q_idx, q_data)

        # Кнопка добавления вопроса
        add_q_button = ctk.CTkButton(
            dialog,
            text="+ Добавить вопрос",
            command=lambda: self.create_question_widget(questions_frame, question_widgets, len(question_widgets)),
            width=500,
            height=30
        )
        add_q_button.pack(pady=10)

        def save_changes():
            title = title_entry.get()
            lecture_id = None

            if lecture_var.get() != "Без лекции":
                lecture_id = int(lecture_var.get().split(":")[0])

            new_questions = []
            for question_entry, answers_text in question_widgets:
                question_text = question_entry.get().strip()
                answers_lines = answers_text.get("1.0", "end").strip().split('\n')
                answers = [line.strip() for line in answers_lines if line.strip()]

                if question_text and len(answers) >= 2:
                    new_questions.append({
                        'question': question_text,
                        'answers': answers,
                        'correct': answers[0]
                    })

            if not title or not new_questions:
                messagebox.showerror("Ошибка", "Заполните название и хотя бы один вопрос")
                return

            try:
                self.db.cursor.execute("""
                    UPDATE tests 
                    SET title=?, lecture_id=?, questions=? 
                    WHERE id=?
                """, (title, lecture_id, json.dumps(new_questions), test[0]))
                self.db.commit()
                messagebox.showinfo("Успех", "Тест успешно обновлен!")
                dialog.destroy()
                self.load_tests()
                # Сбрасываем выделение
                self.test_selected_info.configure(
                    text="Выберите тест из списка",
                    text_color="gray"
                )
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при обновлении: {str(e)}")

        save_button = ctk.CTkButton(
            dialog,
            text="Сохранить изменения",
            command=save_changes,
            fg_color="green",
            width=500,
            height=40
        )
        save_button.pack(pady=10)

        cancel_button = ctk.CTkButton(
            dialog,
            text="Отмена",
            command=dialog.destroy,
            width=500,
            height=40,
            fg_color="gray"
        )
        cancel_button.pack(pady=(0, 20))

    def create_question_widget(self, parent, widget_list, index, data=None):
        """Создание виджета вопроса для редактирования"""
        question_frame = ctk.CTkFrame(parent, fg_color=self.colors['card'])
        question_frame.pack(fill="x", pady=5, padx=5)

        # Заголовок с номером вопроса
        header_frame = ctk.CTkFrame(question_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 0))

        header_label = ctk.CTkLabel(
            header_frame,
            text=f"Вопрос {index + 1}:",
            font=("Arial", 11, "bold")
        )
        header_label.pack(side="left")

        def remove_question():
            question_frame.destroy()
            # Удаляем из списка
            for i, (q_entry, a_text) in enumerate(widget_list):
                if q_entry == question_entry and a_text == answers_text:
                    widget_list.pop(i)
                    break

        remove_btn = ctk.CTkButton(
            header_frame,
            text="✖",
            width=30,
            height=30,
            fg_color="red",
            command=remove_question
        )
        remove_btn.pack(side="right")

        # Поле вопроса
        question_entry = ctk.CTkEntry(question_frame, width=450)
        question_entry.pack(padx=10, pady=(10, 5))

        if data:
            question_entry.insert(0, data['question'])

        # Поле ответов
        answers_label = ctk.CTkLabel(
            question_frame,
            text="Ответы (по одному в строке, первый - правильный):",
            font=("Arial", 10)
        )
        answers_label.pack(anchor="w", padx=10, pady=(5, 5))

        answers_text = ctk.CTkTextbox(question_frame, width=450, height=80)
        answers_text.pack(padx=10, pady=(0, 10))

        if data:
            answers_text.insert("1.0", "\n".join(data['answers']))

        widget_list.append((question_entry, answers_text))

    def delete_selected_test(self):
        """Удаление выбранного теста"""
        selected = self.tests_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите тест для удаления")
            return

        # Подтверждение удаления
        if not messagebox.askyesno("Подтверждение",
                                   "Вы уверены, что хотите удалить этот тест?\n\nВсе результаты теста также будут удалены."):
            return

        # Получаем ID теста
        test_id = self.tests_tree.item(selected[0])['values'][0]

        try:
            # Удаляем результаты теста
            self.db.cursor.execute("DELETE FROM test_results WHERE test_id=?", (test_id,))
            # Удаляем тест
            self.db.cursor.execute("DELETE FROM tests WHERE id=?", (test_id,))
            self.db.commit()
            messagebox.showinfo("Успех", "Тест успешно удален!")
            self.load_tests()
            # Сбрасываем выделение
            self.test_selected_info.configure(
                text="Выберите тест из списка",
                text_color="gray"
            )
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении: {str(e)}")

    # ==================== ВКЛАДКА СЛОВ ====================

    def create_words_tab(self):
        """Создание вкладки управления словами"""

        # ВЕРХНЯЯ ПАНЕЛЬ С КНОПКАМИ
        top_panel = ctk.CTkFrame(self.tab_words, fg_color="transparent")
        top_panel.pack(fill="x", pady=(20, 10))

        # Заголовок и кнопка добавления
        header_frame = ctk.CTkFrame(top_panel, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            header_frame,
            text="📋 Управление словами",
            font=("Arial", 18, "bold")
        ).pack(side="left")

        add_btn = ctk.CTkButton(
            header_frame,
            text="➕ Добавить слово",
            command=self.parent.show_add_word_dialog,
            fg_color="green",
            hover_color="darkgreen",
            height=40,
            width=200
        )
        add_btn.pack(side="right")

        # ПАНЕЛЬ ДЕЙСТВИЙ
        action_frame = ctk.CTkFrame(top_panel, fg_color=self.colors['card'], height=60)
        action_frame.pack(fill="x", pady=5)
        action_frame.pack_propagate(False)

        edit_btn = ctk.CTkButton(
            action_frame,
            text="✏️ Редактировать",
            command=self.edit_selected_word,
            width=150,
            height=35
        )
        edit_btn.pack(side="left", padx=10, pady=12)

        delete_btn = ctk.CTkButton(
            action_frame,
            text="🗑️ Удалить",
            command=self.delete_selected_word,
            width=150,
            height=35,
            fg_color="#D32F2F",
            hover_color="#B71C1C"
        )
        delete_btn.pack(side="left", padx=10, pady=12)

        refresh_btn = ctk.CTkButton(
            action_frame,
            text="🔄 Обновить",
            command=self.load_words,
            width=150,
            height=35,
            fg_color="#1976D2",
            hover_color="#0D47A1"
        )
        refresh_btn.pack(side="left", padx=10, pady=12)

        self.word_selected_info = ctk.CTkLabel(
            action_frame,
            text="Выберите слово из списка",
            font=("Arial", 12),
            text_color="gray"
        )
        self.word_selected_info.pack(side="right", padx=20, pady=12)

        # ТАБЛИЦА
        table_container = ctk.CTkFrame(self.tab_words, fg_color="transparent")
        table_container.pack(fill="both", expand=True, pady=(0, 10))

        table_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        table_frame.pack(fill="both", expand=True)

        # Таблица слов
        columns = ("id", "Английский", "Русский", "Транскрипция", "Категория")
        self.words_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=12
        )

        # Настройка колонок
        self.words_tree.heading("id", text="ID")
        self.words_tree.heading("Английский", text="Английский")
        self.words_tree.heading("Русский", text="Русский")
        self.words_tree.heading("Транскрипция", text="Транскрипция")
        self.words_tree.heading("Категория", text="Категория")

        self.words_tree.column("id", width=50, anchor="center")
        self.words_tree.column("Английский", width=150)
        self.words_tree.column("Русский", width=150)
        self.words_tree.column("Транскрипция", width=150)
        self.words_tree.column("Категория", width=150)

        # Стилизация
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background=self.colors['card'],
                        fieldbackground=self.colors['card'],
                        foreground="white",
                        rowheight=30)
        style.configure("Treeview.Heading",
                        background=self.colors['primary'],
                        foreground="white",
                        font=("Arial", 11, "bold"))
        style.map("Treeview",
                  background=[('selected', self.colors['primary'])])

        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.words_tree.yview)
        self.words_tree.configure(yscrollcommand=scrollbar.set)

        self.words_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Привязываем событие выбора
        self.words_tree.bind('<<TreeviewSelect>>', self.on_word_select)

        # Загружаем слова
        self.load_words()

    def on_word_select(self, event):
        """Обработчик выбора слова"""
        selected = self.words_tree.selection()
        if selected:
            values = self.words_tree.item(selected[0])['values']
            if values:
                self.word_selected_info.configure(
                    text=f"✓ Выбрано: {values[1]} → {values[2]} (ID: {values[0]})",
                    text_color="#4CAF50"
                )
        else:
            self.word_selected_info.configure(
                text="Выберите слово из списка",
                text_color="gray"
            )

    def load_words(self):
        """Загрузка слов в таблицу"""
        # Очищаем текущий список
        for item in self.words_tree.get_children():
            self.words_tree.delete(item)

        # Получаем слова из БД
        self.db.cursor.execute("""
            SELECT id, english, russian, transcription, category 
            FROM words 
            ORDER BY english
        """)
        words = self.db.cursor.fetchall()

        # Добавляем в таблицу
        for word in words:
            self.words_tree.insert("", "end", values=word)

    def edit_selected_word(self):
        """Редактирование выбранного слова"""
        selected = self.words_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите слово для редактирования")
            return

        # Получаем ID слова
        word_id = self.words_tree.item(selected[0])['values'][0]

        # Получаем данные слова
        self.db.cursor.execute("SELECT * FROM words WHERE id=?", (word_id,))
        word = self.db.cursor.fetchone()

        if word:
            self.show_edit_word_dialog(word)

    def show_edit_word_dialog(self, word):
        """Диалог редактирования слова"""
        dialog = ctk.CTkToplevel(self.parent.app)
        dialog.title("Редактировать слово")
        dialog.geometry("400x450")
        dialog.grab_set()

        # Поля ввода
        ctk.CTkLabel(dialog, text="Английское слово:", font=("Arial", 12)).pack(pady=(20, 5))
        english_entry = ctk.CTkEntry(dialog, width=300)
        english_entry.insert(0, word[1])
        english_entry.pack(pady=(0, 10))

        ctk.CTkLabel(dialog, text="Русский перевод:", font=("Arial", 12)).pack(pady=(10, 5))
        russian_entry = ctk.CTkEntry(dialog, width=300)
        russian_entry.insert(0, word[2])
        russian_entry.pack(pady=(0, 10))

        ctk.CTkLabel(dialog, text="Транскрипция:", font=("Arial", 12)).pack(pady=(10, 5))
        transcription_entry = ctk.CTkEntry(dialog, width=300)
        if word[3]:
            transcription_entry.insert(0, word[3])
        transcription_entry.pack(pady=(0, 10))

        ctk.CTkLabel(dialog, text="Категория:", font=("Arial", 12)).pack(pady=(10, 5))
        category_entry = ctk.CTkEntry(dialog, width=300, placeholder_text="Основные, Животные и т.д.")
        if word[4]:
            category_entry.insert(0, word[4])
        category_entry.pack(pady=(0, 20))

        def save_changes():
            english = english_entry.get()
            russian = russian_entry.get()
            transcription = transcription_entry.get()
            category = category_entry.get()

            if not english or not russian:
                messagebox.showerror("Ошибка", "Заполните обязательные поля")
                return

            try:
                self.db.cursor.execute("""
                    UPDATE words 
                    SET english=?, russian=?, transcription=?, category=? 
                    WHERE id=?
                """, (english, russian, transcription, category if category else None, word[0]))
                self.db.commit()
                messagebox.showinfo("Успех", "Слово успешно обновлено!")
                dialog.destroy()
                self.load_words()
                # Сбрасываем выделение
                self.word_selected_info.configure(
                    text="Выберите слово из списка",
                    text_color="gray"
                )
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при обновлении: {str(e)}")

        save_button = ctk.CTkButton(
            dialog,
            text="Сохранить",
            command=save_changes,
            fg_color="green",
            width=300,
            height=40
        )
        save_button.pack(pady=10)

        cancel_button = ctk.CTkButton(
            dialog,
            text="Отмена",
            command=dialog.destroy,
            width=300,
            height=40,
            fg_color="gray"
        )
        cancel_button.pack(pady=(0, 20))

    def delete_selected_word(self):
        """Удаление выбранного слова"""
        selected = self.words_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите слово для удаления")
            return

        # Подтверждение удаления
        if not messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить это слово?"):
            return

        # Получаем ID слова
        word_id = self.words_tree.item(selected[0])['values'][0]

        try:
            self.db.cursor.execute("DELETE FROM words WHERE id=?", (word_id,))
            self.db.commit()
            messagebox.showinfo("Успех", "Слово успешно удалено!")
            self.load_words()
            # Сбрасываем выделение
            self.word_selected_info.configure(
                text="Выберите слово из списка",
                text_color="gray"
            )
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении: {str(e)}")

    def destroy(self):
        """Уничтожение экрана"""
        if self.frame:
            self.frame.destroy()