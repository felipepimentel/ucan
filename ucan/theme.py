import json
import logging
import os

logger = logging.getLogger("UCAN")

# Definir algumas cores e estilos consistentes para a aplicação
COLORS = {
    "primary": "#2563eb",
    "primary_hover": "#1d4ed8",
    "secondary": "#4f46e5",
    "secondary_hover": "#4338ca",
    "background": "#0f172a",
    "surface": "#1e293b",
    "surface_light": "#334155",
    "text_primary": "#f8fafc",
    "text_secondary": "#94a3b8",
    "text_light": "#ffffff",
    "border": "#334155",
    "error": "#ef4444",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "info": "#3b82f6",
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
        "small": 4,
        "medium": 8,
        "large": 16,
    },
    "border_radius": {
        "small": 4,
        "medium": 8,
        "large": 12,
        "circle": 18,
    },
    "button": {
        "width": 36,
        "height": 36,
        "corner_radius": 8,
        "border_width": 1,
        "hover_color": COLORS["surface_light"],
    },
    "input": {
        "height": 36,
        "corner_radius": 8,
        "border_width": 1,
        "hover_color": COLORS["surface_light"],
    },
    "message": {
        "max_width": 600,
        "corner_radius": 8,
        "border_width": 1,
        "hover_color": COLORS["surface_light"],
    },
}

BUTTON_STYLES = {
    "default": {
        "font": ("Segoe UI", 16),
        "corner_radius": LAYOUT["border_radius"]["small"],
        "fg_color": COLORS["primary"],
        "text_color": COLORS["text_light"],
        "hover_color": COLORS["primary_hover"],
    },
    "outline": {
        "font": ("Segoe UI", 16),
        "corner_radius": LAYOUT["border_radius"]["small"],
        "fg_color": COLORS["surface_light"],
        "text_color": COLORS["text_light"],
        "hover_color": COLORS["surface_light"],
        "border_width": 1,
        "border_color": COLORS["border"],
    },
    "accent": {
        "font": ("Segoe UI", 16),
        "corner_radius": LAYOUT["border_radius"]["small"],
        "fg_color": COLORS["primary"],
        "text_color": COLORS["text_light"],
        "hover_color": COLORS["primary_hover"],
    },
    "icon": {
        "font": ("Segoe UI", 20),
        "corner_radius": LAYOUT["border_radius"]["circle"],
        "fg_color": COLORS["surface"],
        "text_color": COLORS["text_primary"],
        "hover_color": COLORS["surface_light"],
        "width": 46,
        "height": 46,
    },
}


class ThemeManager:
    def __init__(self):
        self.themes = {
            "dark": {
                "primary": "#1E88E5",
                "primary_hover": "#1976D2",
                "secondary": "#78909C",
                "success": "#43A047",
                "danger": "#E53935",
                "warning": "#FFB300",
                "background": "#2D2D2D",
                "surface": "#3D3D3D",
                "text": "#EEEEEE",
                "text_secondary": "#BDBDBD",
            },
            "light": {
                "primary": "#2196F3",
                "primary_hover": "#1976D2",
                "secondary": "#78909C",
                "success": "#4CAF50",
                "danger": "#F44336",
                "warning": "#FFC107",
                "background": "#F5F5F5",
                "surface": "#FFFFFF",
                "text": "#212121",
                "text_secondary": "#757575",
            },
            "blue": {
                "primary": "#1976D2",
                "primary_hover": "#1565C0",
                "secondary": "#78909C",
                "success": "#43A047",
                "danger": "#E53935",
                "warning": "#FFB300",
                "background": "#1A237E",
                "surface": "#283593",
                "text": "#FFFFFF",
                "text_secondary": "#B3E5FC",
            },
        }
        self.current_theme = "dark"
        self.load_theme()

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
        return self.themes[self.current_theme]

    def set_theme(self, theme_name):
        """Define o tema atual"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            self.save_theme()
            return True
        return False
