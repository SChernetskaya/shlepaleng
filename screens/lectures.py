# screens/lectures.py
import customtkinter as ctk
from tkinter import messagebox


class LecturesScreen:
    def __init__(self, parent, db, colors, user_id, user_role):
        self.parent = parent
        self.db = db
        self.colors = colors
        self.user_id = user_id
        self.user_role = user_role
        self.frame = None

    def create(self, container):
        """Создание экрана лекций"""
        self.frame = ctk.CTkFrame(container, fg_color="transparent")

        title_label = ctk.CTkLabel(
            self.frame,
            text="🎓 Лекции",
            font=("Arial", 24, "bold")
        )
        title_label.pack(anchor="w", pady=(0, 20))

        # Загрузка лекций
        lectures = self.db.get_lectures()

        if not lectures:
            empty_label = ctk.CTkLabel(self.frame, text="Лекции пока не добавлены", font=("Arial", 16))
            empty_label.pack(pady=50)

            # Кнопка добавления лекции для админа
            if self.user_role == 'admin':
                self.create_admin_buttons()

            return self.frame

        # Группировка по категориям
        lectures_by_category = {}
        for lecture in lectures:
            category = lecture[2] or "Без категории"
            if category not in lectures_by_category:
                lectures_by_category[category] = []
            lectures_by_category[category].append(lecture)

        # Создаем фрейм для прокрутки
        scrollable_frame = ctk.CTkScrollableFrame(self.frame, fg_color="transparent")
        scrollable_frame.pack(fill="both", expand=True)

        for category, cat_lectures in lectures_by_category.items():
            # Заголовок категории
            cat_label = ctk.CTkLabel(
                scrollable_frame,
                text=f"📁 {category}",
                font=("Arial", 18, "bold")
            )
            cat_label.pack(anchor="w", pady=(20, 10))

            # Лекции в категории
            for lecture in cat_lectures:
                self.create_lecture_item(scrollable_frame, lecture)

        # Кнопка добавления лекции для админа
        if self.user_role == 'admin':
            self.create_admin_buttons()

        return self.frame

    def create_lecture_item(self, parent, lecture):
        """Создание элемента лекции"""
        lecture_frame = ctk.CTkFrame(parent, fg_color=self.colors['card'])
        lecture_frame.pack(fill="x", pady=5, padx=5)

        # Информация о лекции
        info_frame = ctk.CTkFrame(lecture_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        title_btn = ctk.CTkButton(
            info_frame,
            text=lecture[1],
            font=("Arial", 14, "bold"),
            command=lambda l=lecture: self.show_lecture_content(l[0]),
            fg_color="transparent",
            hover_color=self.colors['primary'],
            anchor="w"
        )
        title_btn.pack(anchor="w")

        difficulty_label = ctk.CTkLabel(
            info_frame,
            text=f"Сложность: {'★' * lecture[3]}",
            font=("Arial", 12),
            text_color="yellow"
        )
        difficulty_label.pack(anchor="w", pady=(5, 0))

        # Кнопка открытия
        open_button = ctk.CTkButton(
            lecture_frame,
            text="Читать →",
            command=lambda l=lecture: self.show_lecture_content(l[0]),
            width=100
        )
        open_button.pack(side="right", padx=10, pady=10)

    def create_admin_buttons(self):
        """Создание кнопок для администратора"""
        add_lecture_btn = ctk.CTkButton(
            self.frame,
            text="+ Добавить лекцию",
            command=self.show_add_lecture_dialog,
            fg_color="green",
            hover_color="darkgreen"
        )
        add_lecture_btn.pack(pady=20)

    def show_lecture_content(self, lecture_id):
        """Отображение содержания лекции"""
        lecture = self.db.get_lecture(lecture_id)

        if not lecture:
            messagebox.showerror("Ошибка", "Лекция не найдена")
            return

        # Очищаем текущий фрейм
        for widget in self.frame.winfo_children():
            widget.destroy()

        # Заголовок
        title_label = ctk.CTkLabel(
            self.frame,
            text=lecture[0],
            font=("Arial", 24, "bold")
        )
        title_label.pack(anchor="w", pady=(0, 20))

        # Кнопка назад
        back_button = ctk.CTkButton(
            self.frame,
            text="← Назад к лекциям",
            command=self.parent.show_lectures,
            width=150
        )
        back_button.pack(anchor="w", pady=(0, 20))

        # Содержание лекции
        content_frame = ctk.CTkScrollableFrame(self.frame, fg_color=self.colors['card'])
        content_frame.pack(fill="both", expand=True)

        content_label = ctk.CTkLabel(
            content_frame,
            text=lecture[1],
            font=("Arial", 14),
            wraplength=800,
            justify="left"
        )
        content_label.pack(padx=20, pady=20, anchor="w")

        # Отмечаем как прочитанную если пользователь авторизован
        if self.user_id:
            self.db.mark_lecture_completed(self.user_id, lecture_id)

    def show_add_lecture_dialog(self):
        """Диалог добавления лекции"""
        dialog = ctk.CTkToplevel(self.parent.app)
        dialog.title("Добавить лекцию")
        dialog.geometry("600x500")
        dialog.grab_set()

        # Поля ввода
        ctk.CTkLabel(dialog, text="Название лекции:", font=("Arial", 12)).pack(pady=(20, 5))
        title_entry = ctk.CTkEntry(dialog, width=500)
        title_entry.pack(pady=(0, 10))

        ctk.CTkLabel(dialog, text="Категория:", font=("Arial", 12)).pack(pady=(10, 5))
        category_entry = ctk.CTkEntry(dialog, width=500)
        category_entry.pack(pady=(0, 10))

        ctk.CTkLabel(dialog, text="Уровень сложности (1-5):", font=("Arial", 12)).pack(pady=(10, 5))
        difficulty_var = ctk.StringVar(value="1")
        difficulty_menu = ctk.CTkOptionMenu(
            dialog,
            values=["1", "2", "3", "4", "5"],
            variable=difficulty_var,
            width=500
        )
        difficulty_menu.pack(pady=(0, 10))

        ctk.CTkLabel(dialog, text="Содержание:", font=("Arial", 12)).pack(pady=(10, 5))
        content_text = ctk.CTkTextbox(dialog, width=500, height=200)
        content_text.pack(pady=(0, 20))

        # Кнопки
        def add_lecture():
            title = title_entry.get()
            category = category_entry.get()
            difficulty = difficulty_var.get()
            content = content_text.get("1.0", "end").strip()

            if not title or not content:
                messagebox.showerror("Ошибка", "Заполните обязательные поля")
                return

            try:
                self.db.add_lecture(title, content, category, difficulty, self.user_id)
                messagebox.showinfo("Успех", "Лекция успешно добавлена!")
                dialog.destroy()
                self.parent.show_lectures()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при добавлении: {str(e)}")

        add_button = ctk.CTkButton(
            dialog,
            text="Добавить",
            command=add_lecture,
            fg_color="green",
            width=500,
            height=40
        )
        add_button.pack(pady=10)

        cancel_button = ctk.CTkButton(
            dialog,
            text="Отмена",
            command=dialog.destroy,
            width=500,
            height=40,
            fg_color="gray"
        )
        cancel_button.pack(pady=(0, 20))

    def destroy(self):
        """Уничтожение экрана"""
        if self.frame:
            self.frame.destroy()