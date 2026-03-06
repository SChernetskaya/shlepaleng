# screens/games.py
import customtkinter as ctk
from tkinter import messagebox
import random


class GamesScreen:
    def __init__(self, parent, db, colors, user_id):
        self.parent = parent
        self.db = db
        self.colors = colors
        self.user_id = user_id
        self.frame = None
        self.game_frame = None
        self.game_score = 0
        self.current_word_index = 0
        self.game_words = []

    def create(self, container):
        """Создание экрана игр"""
        self.frame = ctk.CTkFrame(container, fg_color="transparent")

        title_label = ctk.CTkLabel(
            self.frame,
            text="🎮 Мини-игры",
            font=("Arial", 24, "bold")
        )
        title_label.pack(anchor="w", pady=(0, 20))

        # Описание
        desc_label = ctk.CTkLabel(
            self.frame,
            text="Выберите игру для закрепления материала:",
            font=("Arial", 14)
        )
        desc_label.pack(anchor="w", pady=(0, 30))

        # Игры
        games_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        games_frame.pack(fill="both", expand=True)

        games = [
            ("🎯 Угадай слово", "Угадай перевод английского слова", self.play_word_game),
            ("🔤 Составь предложение", "Собери предложение из слов", self.play_sentence_game)
        ]

        for i, (name, desc, command) in enumerate(games):
            self.create_game_card(games_frame, name, desc, command, i)

        return self.frame

    def create_game_card(self, parent, name, desc, command, index):
        """Создание карточки игры"""
        game_frame = ctk.CTkFrame(parent, fg_color=self.colors['card'])
        game_frame.grid(row=index // 2, column=index % 2, padx=10, pady=10, sticky="nsew")
        parent.grid_columnconfigure(index % 2, weight=1)
        parent.grid_rowconfigure(index // 2, weight=1)

        display_name = name
        if name.startswith("🔤 Собери предложение"):
            display_name = "Собери предложение"

        name_label = ctk.CTkLabel(
            game_frame,
            text=name,
            font=("Arial", 18, "bold")
        )
        name_label.pack(pady=(20, 10))

        desc_label = ctk.CTkLabel(
            game_frame,
            text=desc,
            font=("Arial", 12),
            wraplength=300,
            text_color="gray"
        )
        desc_label.pack(pady=(0, 20))

        play_button = ctk.CTkButton(
            game_frame,
            text="Играть",
            command=command,
            width=150,
            height=40
        )
        play_button.pack(pady=(0, 20))

    def play_word_game(self):
        """Игра 'Угадай слово'"""
        words = self.db.get_random_words(10)

        if not words:
            messagebox.showinfo("Нет слов", "Добавьте слова в словарь для игры")
            return

        # Очищаем контент
        for widget in self.frame.winfo_children():
            widget.destroy()

        # Заголовок игры
        title_label = ctk.CTkLabel(
            self.frame,
            text="🎯 Угадай слово",
            font=("Arial", 24, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Переменные игры
        self.game_score = 0
        self.current_word_index = 0
        self.game_words = words

        # Фрейм игры
        self.game_frame = ctk.CTkFrame(self.frame, fg_color=self.colors['card'])
        self.game_frame.pack(fill="both", expand=True, padx=50, pady=20)

        self.show_word_game_question()

    def play_sentence_game(self):
        """Игра 'Составь предложение' - новая игра"""
        self.parent.show_screen("Составь предложение")  # Убедитесь, что здесь "Составь предложение" (с пробелом)

    def show_word_game_question(self):
        """Показ вопроса в игре 'Угадай слово'"""
        for widget in self.game_frame.winfo_children():
            widget.destroy()

        if self.current_word_index >= len(self.game_words):
            self.end_word_game()
            return

        current_word = self.game_words[self.current_word_index]

        # Счет
        score_label = ctk.CTkLabel(
            self.game_frame,
            text=f"Счет: {self.game_score}/{len(self.game_words)}",
            font=("Arial", 16)
        )
        score_label.pack(pady=20)

        # Вопрос
        question_label = ctk.CTkLabel(
            self.game_frame,
            text=f"Как переводится слово:\n{current_word[0]}",
            font=("Arial", 20, "bold")
        )
        question_label.pack(pady=30)

        # Получаем варианты ответов
        wrong_answers = self.db.get_wrong_answers(current_word[1], 3)

        # Создаем список вариантов
        answers = wrong_answers + [current_word[1]]
        random.shuffle(answers)

        # Кнопки с вариантами ответов
        for answer in answers:
            answer_btn = ctk.CTkButton(
                self.game_frame,
                text=answer,
                command=lambda a=answer, c=current_word[1]: self.check_word_game_answer(a, c),
                height=50,
                font=("Arial", 14)
            )
            answer_btn.pack(pady=10, padx=100)

    def check_word_game_answer(self, answer, correct_answer):
        """Проверка ответа в игре 'Угадай слово'"""
        if answer == correct_answer:
            self.game_score += 1
            messagebox.showinfo("Правильно!", "🎉 Верно!")
        else:
            messagebox.showerror("Неправильно", f"❌ Правильный ответ: {correct_answer}")

        self.current_word_index += 1
        self.show_word_game_question()

    def end_word_game(self):
        """Завершение игры 'Угадай слово'"""
        for widget in self.game_frame.winfo_children():
            widget.destroy()

        result_label = ctk.CTkLabel(
            self.game_frame,
            text=f"Игра окончена!\nВаш счет: {self.game_score}/{len(self.game_words)}",
            font=("Arial", 24, "bold")
        )
        result_label.pack(pady=50)

        if self.user_id:
            # Сохранение результата
            self.db.save_game_result(self.user_id, 'word_game', self.game_score)

            # Начисление опыта
            experience_gained = self.game_score * 5
            self.db.add_experience(self.user_id, experience_gained)

        # Кнопка новой игры
        new_game_btn = ctk.CTkButton(
            self.game_frame,
            text="Играть снова",
            command=self.play_word_game,
            height=50,
            font=("Arial", 14)
        )
        new_game_btn.pack(pady=20)

        # Кнопка возврата
        back_btn = ctk.CTkButton(
            self.game_frame,
            text="Вернуться к играм",
            command=self.parent.show_games,
            height=40
        )
        back_btn.pack(pady=10)


    def destroy(self):
        """Уничтожение экрана"""
        if self.frame:
            self.frame.destroy()