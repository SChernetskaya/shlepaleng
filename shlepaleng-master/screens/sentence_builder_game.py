# screens/sentence_builder_game.py
import customtkinter as ctk
from tkinter import messagebox
import random
import json


class SentenceBuilderGame:
    def __init__(self, parent, db, colors, user_id):
        self.parent = parent
        self.db = db
        self.colors = colors
        self.user_id = user_id
        self.frame = None
        self.game_frame = None
        self.score = 0
        self.rounds_played = 0
        self.max_rounds = 10

        # База предложений (можно расширить или загружать из БД)
        self.sentences = [
            {
                "ru": "Я люблю читать книги",
                "en": ["I", "love", "reading", "books"]
            },
            {
                "ru": "Она ходит в школу каждый день",
                "en": ["She", "goes", "to", "school", "every", "day"]
            },
            {
                "ru": "Мы вчера смотрели фильм",
                "en": ["We", "watched", "a", "movie", "yesterday"]
            },
            {
                "ru": "Они будут путешествовать летом",
                "en": ["They", "will", "travel", "in", "summer"]
            },
            {
                "ru": "Это очень вкусный торт",
                "en": ["This", "is", "a", "very", "delicious", "cake"]
            },
            {
                "ru": "Мой брат играет на гитаре",
                "en": ["My", "brother", "plays", "the", "guitar"]
            },
            {
                "ru": "Где находится библиотека?",
                "en": ["Where", "is", "the", "library", "?"]
            },
            {
                "ru": "Я хочу пить",
                "en": ["I", "want", "to", "drink"]
            },
            {
                "ru": "Сегодня хорошая погода",
                "en": ["The", "weather", "is", "nice", "today"]
            },
            {
                "ru": "Как дела?",
                "en": ["How", "are", "you", "?"]
            }
        ]

        self.current_sentence = None
        self.scrambled_words = []
        self.user_sentence = []

    def create(self, container):
        """Создание экрана игры"""
        self.frame = ctk.CTkFrame(container, fg_color="transparent")

        # Верхняя панель с заголовком и счетом
        top_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        top_frame.pack(fill="x", pady=(0, 20))

        # Заголовок
        title_label = ctk.CTkLabel(
            top_frame,
            text="🔤 Составь предложение",
            font=("Arial", 24, "bold"),
            text_color=self.colors['primary']
        )
        title_label.pack(side="left")

        # Счет
        self.score_label = ctk.CTkLabel(
            top_frame,
            text=f"🏆 Счет: {self.score}",
            font=("Arial", 16, "bold")
        )
        self.score_label.pack(side="right")

        # Русское предложение (крупно)
        ru_frame = ctk.CTkFrame(
            self.frame,
            fg_color=self.colors['card'],
            corner_radius=10
        )
        ru_frame.pack(fill="x", pady=10)

        self.ru_label = ctk.CTkLabel(
            ru_frame,
            text="",
            font=("Arial", 22, "bold"),
            wraplength=800,
            justify="center",
            fg_color="transparent"
        )
        self.ru_label.pack(pady=30)

        # Область для составления предложения
        build_frame = ctk.CTkFrame(
            self.frame,
            fg_color=self.colors['card'],
            corner_radius=10
        )
        build_frame.pack(fill="x", pady=10)

        self.build_label = ctk.CTkLabel(
            build_frame,
            text="👆 Нажимай на слова ниже, чтобы составить предложение",
            font=("Arial", 16),
            wraplength=800,
            justify="center",
            height=100,
            fg_color="transparent"
        )
        self.build_label.pack(pady=30)

        # Панель управления
        control_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        control_frame.pack(fill="x", pady=10)

        # Кнопки действий
        self.undo_button = ctk.CTkButton(
            control_frame,
            text="⌫ Удалить последнее",
            command=self.undo_word,
            fg_color=self.colors['danger'],
            hover_color="#B71C1C",
            width=150,
            height=40,
            state="disabled"
        )
        self.undo_button.pack(side="left", padx=5)

        self.clear_button = ctk.CTkButton(
            control_frame,
            text="✕ Очистить всё",
            command=self.clear_sentence,
            fg_color=self.colors['text_muted'],
            hover_color="#555555",
            width=150,
            height=40,
            state="disabled"
        )
        self.clear_button.pack(side="left", padx=5)

        self.check_button = ctk.CTkButton(
            control_frame,
            text="✓ Проверить",
            command=self.check_sentence,
            fg_color=self.colors['success'],
            hover_color="#2E7D32",
            width=150,
            height=40,
            state="disabled"
        )
        self.check_button.pack(side="left", padx=5)

        self.new_round_button = ctk.CTkButton(
            control_frame,
            text="Следующее предложение →",
            command=self.new_round,
            fg_color=self.colors['primary'],
            hover_color=self.colors['primary_hover'],
            width=180,
            height=40
        )
        self.new_round_button.pack(side="right", padx=5)

        # Панель со словами
        words_container = ctk.CTkFrame(self.frame, fg_color="transparent")
        words_container.pack(fill="both", expand=True, pady=10)

        self.words_frame = ctk.CTkScrollableFrame(
            words_container,
            fg_color=self.colors['card'],
            corner_radius=10
        )
        self.words_frame.pack(fill="both", expand=True)

        # Начинаем игру
        self.new_round()

        return self.frame

    def scramble_words(self, words):
        """Перемешивает слова"""
        scrambled = words.copy()
        random.shuffle(scrambled)
        return scrambled

    def update_build_display(self):
        """Обновляет отображение собираемого предложения"""
        if self.user_sentence:
            display_text = " ".join(self.user_sentence)
            self.build_label.configure(text=display_text, text_color=self.colors['text'])
            self.undo_button.configure(state="normal")
            self.clear_button.configure(state="normal")
            self.check_button.configure(state="normal")
        else:
            self.build_label.configure(
                text="👆 Нажимай на слова ниже, чтобы составить предложение",
                text_color=self.colors['text_muted']
            )
            self.undo_button.configure(state="disabled")
            self.clear_button.configure(state="disabled")
            self.check_button.configure(state="disabled")

    def create_word_buttons(self):
        """Создает кнопки для перемешанных слов"""
        # Очищаем фрейм
        for widget in self.words_frame.winfo_children():
            widget.destroy()

        if not self.scrambled_words:
            return

        # Создаем кнопки в сетке
        row = 0
        col = 0
        max_cols = 4  # Максимум кнопок в ряду

        for word in self.scrambled_words:
            btn = ctk.CTkButton(
                self.words_frame,
                text=word,
                font=("Arial", 14, "bold"),
                fg_color=self.colors['primary'],
                hover_color=self.colors['primary_hover'],
                command=lambda w=word: self.add_word(w),
                width=180,
                height=50
            )
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        # Настраиваем веса колонок
        for i in range(max_cols):
            self.words_frame.grid_columnconfigure(i, weight=1)

    def add_word(self, word):
        """Добавляет слово в собираемое предложение"""
        self.user_sentence.append(word)
        self.scrambled_words.remove(word)
        self.update_build_display()
        self.create_word_buttons()

    def undo_word(self):
        """Удаляет последнее добавленное слово"""
        if self.user_sentence:
            word = self.user_sentence.pop()
            self.scrambled_words.append(word)
            random.shuffle(self.scrambled_words)
            self.update_build_display()
            self.create_word_buttons()

    def clear_sentence(self):
        """Очищает всё собираемое предложение"""
        self.scrambled_words.extend(self.user_sentence)
        self.user_sentence = []
        random.shuffle(self.scrambled_words)
        self.update_build_display()
        self.create_word_buttons()

    def check_sentence(self):
        """Проверяет правильность составленного предложения"""
        correct = self.current_sentence["en"]

        if self.user_sentence == correct:
            self.score += 10
            self.score_label.configure(text=f"🏆 Счет: {self.score}")
            self.rounds_played += 1

            messagebox.showinfo(
                "Правильно!",
                f"✅ Отлично! Предложение составлено верно!\n\n+10 очков"
            )

            if self.rounds_played >= self.max_rounds:
                self.end_game()
            else:
                self.new_round()
        else:
            correct_text = " ".join(correct)
            messagebox.showerror(
                "Ошибка",
                f"❌ Неправильно.\n\nПравильный порядок:\n{correct_text}"
            )

    def new_round(self):
        """Начинает новый раунд с новым предложением"""
        if not self.sentences:
            messagebox.showerror("Ошибка", "Нет доступных предложений")
            return

        self.current_sentence = random.choice(self.sentences)
        self.scrambled_words = self.scramble_words(self.current_sentence["en"])
        self.user_sentence = []

        self.ru_label.configure(text=f"🇷🇺 {self.current_sentence['ru']}")
        self.update_build_display()
        self.create_word_buttons()

    def end_game(self):
        """Завершение игры"""
        # Сохраняем результат - ИСПРАВЛЕНО!!!
        if self.user_id:
            # Сохраняем результат с русским названием
            game_name = "Составь предложение"
            print(f"Сохраняем результат: {game_name}, счет: {self.score}")  # Отладка
            self.db.save_game_result(self.user_id, game_name, self.score)

            # Начисляем опыт
            experience_gained = self.score
            level_up = self.db.add_experience(self.user_id, experience_gained)

        # Очищаем игровой фрейм
        for widget in self.frame.winfo_children():
            widget.destroy()

        # Экран результатов
        result_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        result_frame.pack(expand=True, fill="both")

        # Результат
        result_label = ctk.CTkLabel(
            result_frame,
            text="🎉 Игра завершена!",
            font=("Arial", 32, "bold"),
            text_color=self.colors['primary']
        )
        result_label.pack(pady=(100, 20))

        score_label = ctk.CTkLabel(
            result_frame,
            text=f"Ваш счет: {self.score}",
            font=("Arial", 24, "bold")
        )
        score_label.pack(pady=10)

        if self.user_id:
            exp_label = ctk.CTkLabel(
                result_frame,
                text=f"Получено опыта: {self.score}",
                font=("Arial", 18),
                text_color=self.colors['text_muted']
            )
            exp_label.pack(pady=5)

            if 'level_up' in locals() and level_up:
                level_up_label = ctk.CTkLabel(
                    result_frame,
                    text="🌟 Новый уровень!",
                    font=("Arial", 18, "bold"),
                    text_color=self.colors['success']
                )
                level_up_label.pack(pady=5)

        # Кнопки
        button_frame = ctk.CTkFrame(result_frame, fg_color="transparent")
        button_frame.pack(pady=50)

        play_again_btn = ctk.CTkButton(
            button_frame,
            text="🔄 Играть снова",
            command=lambda: self.restart_game(),
            fg_color=self.colors['success'],
            hover_color="#2E7D32",
            width=200,
            height=50,
            font=("Arial", 14, "bold")
        )
        play_again_btn.pack(side="left", padx=10)

        back_btn = ctk.CTkButton(
            button_frame,
            text="← К играм",
            command=self.parent.show_games,
            fg_color=self.colors['primary'],
            hover_color=self.colors['primary_hover'],
            width=200,
            height=50,
            font=("Arial", 14, "bold")
        )
        back_btn.pack(side="left", padx=10)

    def restart_game(self):
        """Перезапуск игры"""
        self.score = 0
        self.rounds_played = 0
        self.parent.show_screen("Составь предложение")

    def destroy(self):
        """Уничтожение экрана"""
        if self.frame:
            self.frame.destroy()