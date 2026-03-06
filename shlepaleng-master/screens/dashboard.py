# screens/dashboard.py
import customtkinter as ctk
import json
from datetime import *


class DashboardScreen:
    def __init__(self, parent, db, colors, user_id):
        self.parent = parent
        self.db = db
        self.colors = colors
        self.user_id = user_id
        self.frame = None

    def create(self, container):
        """Создание экрана главной страницы"""
        self.frame = ctk.CTkFrame(container, fg_color="transparent")

        if self.user_id:
            # Для авторизованного пользователя показываем последнюю активность
            self.create_last_activity()
        else:
            # Для гостя показываем приветствие
            self.create_guest_welcome()

        # Быстрый доступ для всех
        self.create_quick_access()

        return self.frame

    def create_last_activity(self):
        """Создание блока с последней активностью"""
        # Заголовок
        last_activity_label = ctk.CTkLabel(
            self.frame,
            text="⏱️ Последняя активность",
            font=("Arial", 24, "bold")
        )
        last_activity_label.pack(anchor="w", pady=(0, 20))

        # Контейнер для последней активности
        activity_frame = ctk.CTkFrame(self.frame, fg_color=self.colors['card'])
        activity_frame.pack(fill="x", pady=10)

        # Получаем самый последний тест пользователя
        self.db.cursor.execute("""
            SELECT 
                'test' as type,
                t.title as name,
                tr.score,
                tr.max_score,
                tr.completed_date,
                CAST(tr.score * 100.0 / tr.max_score as INTEGER) as percentage
            FROM test_results tr
            JOIN tests t ON tr.test_id = t.id
            WHERE tr.user_id = ?

            UNION ALL

            SELECT 
                'game' as type,
                gr.game_type as name,  -- теперь здесь будет русское название
                gr.score,
                NULL as max_score,
                gr.completed_date,
                NULL as percentage
            FROM game_results gr
            WHERE gr.user_id = ?

            ORDER BY completed_date DESC
            LIMIT 1
        """, (self.user_id, self.user_id))

        last_activity = self.db.cursor.fetchone()


        if last_activity:
            activity_type, name, score, max_score, date, percentage = last_activity

            # Определяем иконку в зависимости от типа активности
            if activity_type == 'test':
                icon = "📝"
                type_text = "Тест"
            else:  # game
                icon = "🎮"
                type_text = "Игра"
                # Для игр имя уже русское, ничего не меняем

            # Элемент последней активности
            activity_item = ctk.CTkFrame(activity_frame, fg_color="transparent")
            activity_item.pack(fill="x", padx=30, pady=25)

            # Заголовок с типом и иконкой
            header_frame = ctk.CTkFrame(activity_item, fg_color="transparent")
            header_frame.pack(fill="x", pady=(0, 10))

            type_label = ctk.CTkLabel(
                header_frame,
                text=f"{icon} {type_text}",
                font=("Arial", 18, "bold"),
                text_color=self.colors['primary']
            )
            type_label.pack(side="left")

            # Дата
            try:
                date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                date_obj_russion = date_obj + timedelta(hours=3)
                date_formatted = date_obj_russion.strftime("%d.%m.%Y %H:%M")
            except:
                date_formatted = date[:10] if date else "Неизвестно"

            date_label = ctk.CTkLabel(
                header_frame,
                text=f"📅 {date_formatted}",
                font=("Arial", 14),
                text_color="gray"
            )
            date_label.pack(side="right")

            # Название (теперь отображается русское название)
            name_label = ctk.CTkLabel(
                activity_item,
                text=name,
                font=("Arial", 22, "bold"),
                wraplength=700,
                justify="left"
            )
            name_label.pack(anchor="w", pady=(5, 10))

            # Результат (если есть)
            if score is not None:
                result_frame = ctk.CTkFrame(activity_item, fg_color="transparent")
                result_frame.pack(anchor="w", pady=(5, 0))

                if max_score:
                    # Для тестов
                    percentage_value = score / max_score * 100
                    result_text = f"Результат: {score}/{max_score} ({percentage_value:.1f}%)"

                    # Выбираем цвет в зависимости от результата
                    if percentage_value >= 80:
                        result_color = "#4CAF50"  # зеленый
                        emoji = "🌟"
                    elif percentage_value >= 60:
                        result_color = "#FF9800"  # оранжевый
                        emoji = "👍"
                    else:
                        result_color = "#F44336"  # красный
                        emoji = "💪"
                else:
                    # Для игр
                    result_text = f"Счет: {score}"
                    result_color = self.colors['primary']
                    emoji = "🎯"

                result_label = ctk.CTkLabel(
                    result_frame,
                    text=result_text,
                    font=("Arial", 18, "bold"),
                    text_color=result_color
                )
                result_label.pack(side="left")

                emoji_label = ctk.CTkLabel(
                    result_frame,
                    text=emoji,
                    font=("Arial", 24)
                )
                emoji_label.pack(side="left", padx=(10, 0))
        else:
            # Если активности нет
            empty_frame = ctk.CTkFrame(activity_frame, fg_color="transparent")
            empty_frame.pack(fill="x", padx=30, pady=40)

            empty_icon = ctk.CTkLabel(
                empty_frame,
                text="✨",
                font=("Arial", 48)
            )
            empty_icon.pack()

            empty_label = ctk.CTkLabel(
                empty_frame,
                text="У вас пока нет активности",
                font=("Arial", 18, "bold"),
                text_color="gray"
            )
            empty_label.pack(pady=(10, 5))

            empty_sub = ctk.CTkLabel(
                empty_frame,
                text="Пройдите тест или сыграйте в игру!",
                font=("Arial", 14),
                text_color="gray"
            )
            empty_sub.pack()

    def create_guest_welcome(self):
        """Приветствие для гостя"""
        # Приветственный блок
        guest_frame = ctk.CTkFrame(self.frame, fg_color=self.colors['card'])
        guest_frame.pack(fill="x", pady=10)

        # Заголовок
        welcome_label = ctk.CTkLabel(
            guest_frame,
            text="👋 Добро пожаловать в ShlepaLang!",
            font=("Arial", 28, "bold")
        )
        welcome_label.pack(pady=30)

        # Описание
        info_label = ctk.CTkLabel(
            guest_frame,
            text="Зарегистрируйтесь или войдите, чтобы сохранять свой прогресс и получать достижения!",
            font=("Arial", 15),
            wraplength=600
        )
        info_label.pack(pady=(0, 30))

        # Кнопки для гостя
        button_frame = ctk.CTkFrame(guest_frame, fg_color="transparent")
        button_frame.pack(pady=(0, 30))

        login_btn = ctk.CTkButton(
            button_frame,
            text="🔐 Войти",
            command=self.parent.show_login,
            width=160,
            height=45,
            fg_color=self.colors['primary'],
            font=("Arial", 14, "bold")
        )
        login_btn.pack(side="left", padx=10)

        register_btn = ctk.CTkButton(
            button_frame,
            text="📝 Регистрация",
            command=lambda: self.parent.auth_screen.show_register(self.parent.main_container),
            width=160,
            height=45,
            fg_color="transparent",
            border_color=self.colors['primary'],
            border_width=2,
            font=("Arial", 14, "bold")
        )
        register_btn.pack(side="left", padx=10)

    def create_quick_access(self):
        """Быстрый доступ к функциям"""
        # Заголовок
        quick_access_label = ctk.CTkLabel(
            self.frame,
            text="🚀 Быстрый доступ",
            font=("Arial", 24, "bold")
        )
        quick_access_label.pack(anchor="w", pady=(30, 20))

        # Контейнер для кнопок
        quick_access_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        quick_access_frame.pack(fill="x", pady=10)

        # Кнопки быстрого доступа
        quick_buttons = [
            ("📚 Словарь", "dictionary", "Изучить новые слова"),
            ("📝 Тесты", "tests", "Проверить знания"),
            ("🎮 Игры", "games", "Закрепить материал"),
            ("🎓 Лекции", "lectures", "Изучить теорию"),
        ]

        for i, (title, screen, desc) in enumerate(quick_buttons):
            # Карточка с кнопкой
            card = ctk.CTkFrame(quick_access_frame, fg_color=self.colors['card'])
            card.grid(row=i // 2, column=i % 2, padx=10, pady=10, sticky="nsew")
            quick_access_frame.grid_columnconfigure(i % 2, weight=1)

            # Кнопка
            btn = ctk.CTkButton(
                card,
                text=title,
                command=lambda s=screen: self.parent.show_screen(s),
                height=90,
                fg_color="transparent",
                hover_color=self.colors['primary_hover'],
                font=("Arial", 18, "bold")
            )
            btn.pack(pady=(20, 5))

            # Описание
            desc_label = ctk.CTkLabel(
                card,
                text=desc,
                font=("Arial", 12),
                text_color="gray"
            )
            desc_label.pack(pady=(0, 20))

    def destroy(self):
        """Уничтожение экрана"""
        if self.frame:
            self.frame.destroy()