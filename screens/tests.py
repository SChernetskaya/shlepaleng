# screens/tests.py
import customtkinter as ctk
from tkinter import messagebox
import json


class TestsScreen:
    def __init__(self, parent, db, colors, user_id, user_role):
        self.parent = parent
        self.db = db
        self.colors = colors
        self.user_id = user_id
        self.user_role = user_role
        self.frame = None
        self.test_questions_frame = None
        self.test_answers = []
        self.current_test_id = None

    def create(self, container):
        """Создание экрана тестов"""
        self.frame = ctk.CTkFrame(container, fg_color="transparent")

        title_label = ctk.CTkLabel(
            self.frame,
            text="📝 Тесты",
            font=("Arial", 24, "bold")
        )
        title_label.pack(anchor="w", pady=(0, 20))

        # Загрузка тестов
        tests = self.db.get_tests(self.user_id if self.user_id else 0)

        if not tests:
            empty_label = ctk.CTkLabel(self.frame, text="Тесты пока не добавлены", font=("Arial", 16))
            empty_label.pack(pady=50)

            if self.user_role == 'admin':
                self.create_admin_buttons()

            return self.frame

        # Создаем фрейм для прокрутки
        scrollable_frame = ctk.CTkScrollableFrame(self.frame, fg_color="transparent")
        scrollable_frame.pack(fill="both", expand=True)

        for test in tests:
            self.create_test_item(scrollable_frame, test)

        if self.user_role == 'admin':
            self.create_admin_buttons()

        return self.frame

    def create_test_item(self, parent, test):
        """Создание элемента теста"""
        test_frame = ctk.CTkFrame(parent, fg_color=self.colors['card'])
        test_frame.pack(fill="x", pady=5, padx=5)

        # Информация о тесте
        info_frame = ctk.CTkFrame(test_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        title_label = ctk.CTkLabel(
            info_frame,
            text=test[1],
            font=("Arial", 16, "bold")
        )
        title_label.pack(anchor="w")

        if test[2]:
            lecture_label = ctk.CTkLabel(
                info_frame,
                text=f"Лекция: {test[2]}",
                font=("Arial", 12),
                text_color="gray"
            )
            lecture_label.pack(anchor="w", pady=(5, 0))

        attempts_label = ctk.CTkLabel(
            info_frame,
            text=f"Попыток: {test[3]}",
            font=("Arial", 12),
            text_color="gray"
        )
        attempts_label.pack(anchor="w", pady=(5, 0))

        # Кнопка начала теста
        start_button = ctk.CTkButton(
            test_frame,
            text="Начать тест →",
            command=lambda t=test: self.start_test(t[0]),
            width=120
        )
        start_button.pack(side="right", padx=10, pady=10)

    def create_admin_buttons(self):
        """Создание кнопок для администратора"""
        add_test_btn = ctk.CTkButton(
            self.frame,
            text="+ Добавить тест",
            command=self.show_add_test_dialog,
            fg_color="green",
            hover_color="darkgreen"
        )
        add_test_btn.pack(pady=20)

    def start_test(self, test_id):
        """Начало теста"""
        test = self.db.get_test(test_id)

        if not test:
            messagebox.showerror("Ошибка", "Тест не найден")
            return

        questions = json.loads(test[1])

        if not questions:
            messagebox.showerror("Ошибка", "Тест не содержит вопросов")
            return

        # Очищаем текущий фрейм
        for widget in self.frame.winfo_children():
            widget.destroy()

        # Заголовок теста
        title_label = ctk.CTkLabel(
            self.frame,
            text=f"Тест: {test[0]}",
            font=("Arial", 24, "bold")
        )
        title_label.pack(anchor="w", pady=(0, 20))

        # Фрейм для вопросов
        self.test_questions_frame = ctk.CTkScrollableFrame(self.frame, fg_color="transparent")
        self.test_questions_frame.pack(fill="both", expand=True)

        # Переменные для ответов
        self.test_answers = []
        self.current_test_id = test_id

        # Отображение вопросов
        for i, question_data in enumerate(questions):
            self.create_question_item(i, question_data)

        # Кнопка завершения теста
        submit_button = ctk.CTkButton(
            self.frame,
            text="Завершить тест",
            command=lambda: self.submit_test(test_id, questions),
            height=50,
            fg_color="green",
            font=("Arial", 14, "bold")
        )
        submit_button.pack(pady=20)

    def create_question_item(self, index, question_data):
        """Создание элемента вопроса"""
        question_frame = ctk.CTkFrame(self.test_questions_frame, fg_color=self.colors['card'])
        question_frame.pack(fill="x", pady=10, padx=5)

        # Вопрос
        question_label = ctk.CTkLabel(
            question_frame,
            text=f"{index + 1}. {question_data['question']}",
            font=("Arial", 14, "bold"),
            wraplength=800,
            justify="left"
        )
        question_label.pack(anchor="w", padx=20, pady=(15, 10))

        # Варианты ответов
        answer_var = ctk.StringVar(value="")

        for answer in question_data['answers']:
            answer_btn = ctk.CTkRadioButton(
                question_frame,
                text=answer,
                variable=answer_var,
                value=answer,
                font=("Arial", 12)
            )
            answer_btn.pack(anchor="w", padx=40, pady=2)

        self.test_answers.append(answer_var)

    def submit_test(self, test_id, questions):
        """Отправка результатов теста"""
        score = 0
        total = len(questions)

        # Проверка ответов
        for i, (question, answer_var) in enumerate(zip(questions, self.test_answers)):
            if answer_var.get() == question['correct']:
                score += 1

        # Вывод результата
        result_text = f"Ваш результат: {score}/{total} ({score / total * 100:.1f}%)"

        if score == total:
            result_text += "\n🎉 Отличный результат!"
        elif score >= total * 0.7:
            result_text += "\n👍 Хороший результат!"
        else:
            result_text += "\n📚 Есть над чем поработать!"

        messagebox.showinfo("Результат теста", result_text)

        # Сохранение результата для авторизованных пользователей
        if self.user_id:
            self.db.save_test_result(self.user_id, test_id, score, total)

            # Начисление опыта
            experience_gained = score * 10
            level_up = self.db.add_experience(self.user_id, experience_gained)

            if level_up:
                messagebox.showinfo("Поздравляем!", f"Вы достигли нового уровня!")

        # Возврат к списку тестов
        self.parent.show_tests()

    def show_add_test_dialog(self):
        """Диалог добавления теста"""
        dialog = ctk.CTkToplevel(self.parent.app)
        dialog.title("Добавить тест")
        dialog.geometry("600x600")
        dialog.grab_set()

        # Поля ввода
        ctk.CTkLabel(dialog, text="Название теста:", font=("Arial", 12)).pack(pady=(20, 5))
        title_entry = ctk.CTkEntry(dialog, width=500)
        title_entry.pack(pady=(0, 10))

        ctk.CTkLabel(dialog, text="Связанная лекция (опционально):", font=("Arial", 12)).pack(pady=(10, 5))

        lectures = self.db.get_lectures()
        lecture_options = ["Без лекции"] + [f"{lec[0]}: {lec[1]}" for lec in lectures]

        lecture_var = ctk.StringVar(value="Без лекции")
        lecture_menu = ctk.CTkOptionMenu(dialog, values=lecture_options, variable=lecture_var, width=500)
        lecture_menu.pack(pady=(0, 10))

        # Вопросы теста
        self.test_questions = []

        questions_frame = ctk.CTkScrollableFrame(dialog, width=500, height=300)
        questions_frame.pack(pady=10)

        def add_question():
            question_frame = ctk.CTkFrame(questions_frame, fg_color=self.colors['card'])
            question_frame.pack(fill="x", pady=5, padx=5)

            ctk.CTkLabel(question_frame, text="Вопрос:", font=("Arial", 11)).pack(anchor="w", padx=10, pady=(10, 5))
            question_entry = ctk.CTkEntry(question_frame, width=450)
            question_entry.pack(padx=10, pady=(0, 5))

            ctk.CTkLabel(question_frame, text="Ответы (по одному в строке, первый - правильный):",
                         font=("Arial", 11)).pack(anchor="w", padx=10, pady=(5, 5))
            answers_text = ctk.CTkTextbox(question_frame, width=450, height=80)
            answers_text.pack(padx=10, pady=(0, 10))

            self.test_questions.append((question_entry, answers_text))

        # Кнопка добавления вопроса
        add_q_button = ctk.CTkButton(
            dialog,
            text="+ Добавить вопрос",
            command=add_question,
            width=500,
            height=30
        )
        add_q_button.pack(pady=10)

        # Добавляем один вопрос по умолчанию
        add_question()

        # Кнопки сохранения/отмены
        def save_test():
            title = title_entry.get()
            lecture_id = None

            if lecture_var.get() != "Без лекции":
                lecture_id = int(lecture_var.get().split(":")[0])

            questions = []
            for question_entry, answers_text in self.test_questions:
                question_text = question_entry.get().strip()
                answers_lines = answers_text.get("1.0", "end").strip().split('\n')
                answers = [line.strip() for line in answers_lines if line.strip()]

                if question_text and len(answers) >= 2:
                    questions.append({
                        'question': question_text,
                        'answers': answers,
                        'correct': answers[0]
                    })

            if not title or not questions:
                messagebox.showerror("Ошибка", "Заполните название и хотя бы один вопрос")
                return

            try:
                self.db.add_test(title, lecture_id, questions, self.user_id)
                messagebox.showinfo("Успех", "Тест успешно добавлен!")
                dialog.destroy()
                self.parent.show_tests()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при добавлении: {str(e)}")

        save_button = ctk.CTkButton(
            dialog,
            text="Сохранить тест",
            command=save_test,
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

    def destroy(self):
        """Уничтожение экрана"""
        if self.frame:
            self.frame.destroy()