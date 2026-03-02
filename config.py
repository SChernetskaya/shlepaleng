import customtkinter as ctk

# Настройки приложения
APP_TITLE = "ShlepaLang - Изучение английского языка"
APP_GEOMETRY = "1200x700"

# Настройки темы
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Цветовая схема
COLORS = {
    "primary": "#4B8BBE",
    "secondary": "#306998",
    "accent": "#FFD43B",
    "background": "#2B2B2B",
    "card": "#3C3F41",
    "success": "#28a745",
    "danger": "#dc3545",
    "warning": "#ffc107"
}

# Пути к файлам
DB_PATH = 'shlepalang.db'