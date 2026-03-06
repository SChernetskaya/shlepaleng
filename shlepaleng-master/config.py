import customtkinter as ctk

APP_TITLE = "ShlepaLang - Изучение английского языка"
APP_GEOMETRY = "1200x700"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLORS = {
    # ----- ФОНОВЫЕ ЦВЕТА -----
    "background": "#1A1A1A",
    "card": "#2D2D2D",
    "card_hover": "#3D3D3D",
    "sidebar": "#252525",
    
    # ----- АКЦЕНТНЫЕ ЦВЕТА -----
    "primary": "#BB86FC",
    "primary_hover": "#A370F0",
    "secondary": "#FFB347",
    "accent": "#9759F3",
    
    # ----- ТЕКСТОВЫЕ ЦВЕТА -----
    "text": "#FFFFFF",
    "text_secondary": "#E0E0E0",
    "text_muted": "#A0A0A0",
    
    # ----- СТАТУСНЫЕ ЦВЕТА -----
    "success": "#4CAF50",
    "danger": "#F44336",
    "warning": "#FFC107",
    "info": "#2196F3",
    
    # ----- ГРАНИЦЫ И РАЗДЕЛИТЕЛИ -----
    "border": "#404040",
    "divider": "#383838",
    
    # ----- ДОПОЛНИТЕЛЬНЫЕ -----
    "highlight": "#3700B3",
    "overlay": "rgba(0,0,0,0.5)",
}

DB_PATH = 'shlepalang.db'