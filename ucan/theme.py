import json
import logging
import os

import customtkinter as ctk

logger = logging.getLogger("UCAN")

# Definir algumas cores e estilos consistentes para a aplicação
COLORS = {
    "light": {
        "primary": "#7aa2f7",  # bright blue
        "secondary": "#bb9af7",  # purple
        "background": "#f8fafc",  # very light gray
        "surface": "#ffffff",  # white
        "surface_light": "#f1f5f9",  # light gray
        "text": "#1e293b",  # dark slate
        "text_primary": "#1e293b",  # dark slate
        "text_secondary": "#64748b",  # slate
        "text_light": "#f8fafc",  # very light gray
        "error": "#f7768e",  # red
        "border": "#e2e8f0",  # gray
        "primary_hover": "#3d59a1",  # darker blue
        "secondary_hover": "#9d7af7",  # darker purple
    },
    "dark": {
        "primary": "#7aa2f7",  # bright blue
        "secondary": "#bb9af7",  # purple
        "background": "#1a1b26",  # very dark blue
        "surface": "#24283b",  # dark blue gray
        "surface_light": "#2f3549",  # slate
        "text": "#c0caf5",  # very light gray
        "text_primary": "#c0caf5",  # very light gray
        "text_secondary": "#565f89",  # light slate
        "text_light": "#f8fafc",  # very light gray
        "error": "#f7768e",  # red
        "border": "#29394f",  # slate
        "primary_hover": "#3d59a1",  # darker blue
        "secondary_hover": "#9d7af7",  # darker purple
    },
}

# Constantes de estilo
TEXT_STYLES = {
    "h1": {"size": 32, "weight": "bold", "family": "Segoe UI"},
    "h2": {"size": 24, "weight": "bold", "family": "Segoe UI"},
    "subtitle": {"size": 18, "weight": "bold", "family": "Segoe UI"},
    "body": {"size": 16, "weight": "normal", "family": "Segoe UI"},
    "small": {"size": 14, "weight": "normal", "family": "Segoe UI"},
    "caption": {"size": 12, "weight": "normal", "family": "Segoe UI"},
}

LAYOUT = {
    "padding": {
        "small": 5,
        "medium": 10,
        "large": 20,
    },
    "border_radius": {
        "small": 6,
        "medium": 10,
        "large": 15,
        "circle": 20,
    },
    "button": {
        "width": 36,
        "height": 36,
        "corner_radius": 8,
        "border_width": 1,
        "hover_color": "#f1f5f9",  # light gray
    },
    "input": {
        "height": 36,
        "corner_radius": 8,
        "border_width": 1,
        "hover_color": "#f1f5f9",  # light gray
    },
    "message": {
        "max_width": 600,
        "corner_radius": 8,
        "border_width": 1,
        "hover_color": "#f1f5f9",  # light gray
    },
}

BUTTON_STYLES = {
    "default": {
        "font": ("Segoe UI", 16),
        "corner_radius": LAYOUT["border_radius"]["small"],
        "fg_color": "#7aa2f7",  # bright blue
        "text_color": "#f8fafc",  # very light gray
        "hover_color": "#3d59a1",  # darker blue
    },
    "outline": {
        "font": ("Segoe UI", 16),
        "corner_radius": LAYOUT["border_radius"]["small"],
        "fg_color": "#f1f5f9",  # light gray
        "text_color": "#f8fafc",  # very light gray
        "hover_color": "#f1f5f9",  # light gray
        "border_width": 1,
        "border_color": "#e2e8f0",  # gray
    },
    "accent": {
        "font": ("Segoe UI", 16),
        "corner_radius": LAYOUT["border_radius"]["small"],
        "fg_color": "#7aa2f7",  # bright blue
        "text_color": "#f8fafc",  # very light gray
        "hover_color": "#3d59a1",  # darker blue
    },
    "icon": {
        "font": ("Segoe UI", 20),
        "corner_radius": LAYOUT["border_radius"]["circle"],
        "fg_color": "#ffffff",  # white
        "text_color": "#1e293b",  # dark slate
        "hover_color": "#f1f5f9",  # light gray
        "width": 46,
        "height": 46,
    },
}


class ThemeManager:
    def __init__(self):
        self.current_theme = "dark"
        self.colors = COLORS[self.current_theme]

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.colors = COLORS[self.current_theme]
        ctk.set_appearance_mode(self.current_theme)
        return self.current_theme

    def get_colors(self):
        """Get current theme colors"""
        return self.colors

    def apply_theme(self):
        """Apply current theme to the application"""
        ctk.set_appearance_mode(self.current_theme)
        return self.colors

    def load_theme(self):
        """Carrega o tema salvo"""
        try:
            if os.path.exists("theme.json"):
                with open("theme.json", "r") as f:
                    data = json.load(f)
                    self.current_theme = data.get("theme", "dark")
        except Exception as e:
            logger.error(f"Erro ao carregar tema: {str(e)}")

    def save_theme(self):
        """Salva o tema atual"""
        try:
            with open("theme.json", "w") as f:
                json.dump({"theme": self.current_theme}, f)
        except Exception as e:
            logger.error(f"Erro ao salvar tema: {str(e)}")

    def get_theme(self):
        """Retorna o tema atual"""
        return self.colors

    def set_theme(self, theme_name):
        """Define o tema atual"""
        if theme_name in COLORS:
            self.current_theme = theme_name
            self.colors = COLORS[theme_name]
            self.save_theme()
            return True
        return False
