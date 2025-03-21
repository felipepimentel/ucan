"""
Theme manager for UCAN application.

This module handles theme management, including loading, saving, and applying themes.
"""

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional

from PySide6.QtCore import QFileSystemWatcher, QObject, QTimer, Signal


@dataclass
class Theme:
    """Represents a theme with all its color and style properties."""

    id: str
    name: str
    colors: Dict[str, str]
    is_dark: bool
    is_high_contrast: bool = False
    metadata: Dict[str, str] = None
    css_path: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert theme to dictionary format."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Theme":
        """Create a theme from dictionary data."""
        return cls(**data)

    def get_color(self, key: str, default: str = "#000000") -> str:
        """Get a color value from the theme."""
        return self.colors.get(key, default)

    def generate_stylesheet(self) -> str:
        """Gera um stylesheet do Qt baseado nas cores do tema."""
        # Se tiver um arquivo CSS, carregue-o
        if self.css_path and os.path.exists(self.css_path):
            with open(self.css_path, "r", encoding="utf-8") as file:
                return file.read()

        # Caso contrário, gere o CSS básico
        return f"""
            /* Cores básicas */
            QWidget {{
                background-color: {self.get_color("background")};
                color: {self.get_color("foreground")};
            }}

            /* Estilo dos controles */
            QPushButton {{
                background-color: {self.get_color("button_background")};
                color: {self.get_color("button_foreground")};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: {self.get_color("button_hover_background")};
            }}
            
            QPushButton:pressed {{
                background-color: {self.get_color("button_active_background")};
            }}

            /* QTextEdit e QLineEdit compartilham o mesmo estilo */
            QTextEdit, QLineEdit {{
                background-color: {self.get_color("input_background")};
                color: {self.get_color("input_foreground")};
                border: 1px solid {self.get_color("border")};
                border-radius: 6px;
                padding: 8px;
                selection-background-color: {self.get_color("selection_background")};
                selection-color: {self.get_color("selection_foreground")};
            }}
            
            QTextEdit:focus, QLineEdit:focus {{
                border: 1px solid {self.get_color("accent")};
            }}

            /* Estilo para placeholder */
            QTextEdit::placeholder {{
                color: rgba(225, 226, 230, 0.5);
            }}
            
            QLineEdit::placeholder {{
                color: rgba(225, 226, 230, 0.5);
            }}

            /* QListWidget (para listas e conversas) */
            QListWidget {{
                background-color: {self.get_color("background")};
                border: none;
            }}
            
            QListWidget::item {{
                background-color: {self.get_color("secondary_background")};
                color: {self.get_color("foreground")};
                border-radius: 6px;
                padding: 10px;
                margin: 3px;
            }}
            
            QListWidget::item:hover {{
                background-color: {self.get_color("hover_background")};
            }}
            
            QListWidget::item:selected {{
                background-color: {self.get_color("selection_background")};
                color: {self.get_color("selection_foreground")};
            }}

            /* Contenedores de mensagem */
            #message_user {{
                background-color: rgba(123, 104, 238, 0.15);
                color: {self.get_color("foreground")};
                border-radius: 16px 16px 2px 16px;
                padding: 15px;
                margin: 5px 25px 5px 5px;
            }}
            
            #message_assistant {{
                background-color: {self.get_color("secondary_background")};
                color: {self.get_color("foreground")};
                border-radius: 16px 16px 16px 2px;
                padding: 15px;
                margin: 5px 5px 5px 25px;
            }}
        """


class ThemeManager(QObject):
    """Manages themes for the application."""

    theme_changed = Signal(Theme)
    css_file_changed = Signal()

    def __init__(self):
        """Initialize the theme manager."""
        super().__init__()
        self._themes: Dict[str, Theme] = {}
        self._current_theme: Optional[Theme] = None
        self._themes_dir = Path("ucan/data/themes")
        self._styles_dir = Path("ucan/ui/styles")

        # Configurar watcher para arquivos CSS
        self._file_watcher = QFileSystemWatcher(self)
        self._watch_css_files()
        self._file_watcher.fileChanged.connect(self._on_css_file_changed)

        # Timer para debounce de atualizações
        self._reload_timer = QTimer(self)
        self._reload_timer.setSingleShot(True)
        self._reload_timer.timeout.connect(self._reload_current_theme)

        # Carregar temas
        self._load_builtin_themes()
        self._load_custom_themes()

        # Definir tema padrão
        if not self._current_theme and "dark" in self._themes:
            self.set_theme("dark")

    @property
    def current_theme(self) -> Optional[Theme]:
        """Get the current theme."""
        return self._current_theme

    def _watch_css_files(self):
        """Adiciona arquivos CSS ao watcher."""
        css_files = list(self._styles_dir.glob("**/*.css"))
        for css_file in css_files:
            absolute_path = str(css_file.absolute())
            print(f"Watching CSS file: {absolute_path}")
            self._file_watcher.addPath(absolute_path)

    def _on_css_file_changed(self, path):
        """Chamado quando um arquivo CSS é modificado."""
        print(f"CSS file changed: {path}")
        # Re-adiciona o arquivo ao watcher (necessário em alguns sistemas)
        if os.path.exists(path):  # Verifica se o arquivo ainda existe
            if self._file_watcher.files():
                self._file_watcher.removePath(path)
            self._file_watcher.addPath(path)

        # Usa um timer para evitar múltiplas atualizações
        self._reload_timer.start(100)  # 100ms debounce

    def _reload_current_theme(self):
        """Recarrega o tema atual após alterações no CSS."""
        if self._current_theme and self._current_theme.css_path:
            print(
                f"Reloading current theme: {self._current_theme.name} with CSS file: {self._current_theme.css_path}"
            )

            # Forçar a leitura do arquivo CSS novamente
            if os.path.exists(self._current_theme.css_path):
                with open(self._current_theme.css_path, "r", encoding="utf-8") as file:
                    css_content = file.read()
                    print(f"Successfully read {len(css_content)} bytes from CSS file")

            # Emitir os sinais para atualizar a UI
            self.theme_changed.emit(self._current_theme)
            self.css_file_changed.emit()

    def _load_builtin_themes(self):
        """Carrega os temas embutidos."""
        dark_theme = Theme(
            id="dark",
            name="Dark",
            is_dark=True,
            colors={
                "background": "#1A1A1A",
                "foreground": "#E1E1E1",
                "secondary_background": "#2A2A2A",
                "border": "#3A3A3A",
                "accent": "#7B68EE",
                "error": "#FF6B6B",
                "success": "#4CAF50",
                "warning": "#FFB86C",
                "button_background": "#7B68EE",
                "button_foreground": "#FFFFFF",
                "button_hover_background": "#8F7EF2",
                "button_active_background": "#6A57EA",
                "input_background": "#2A2A2A",
                "input_foreground": "#E1E1E1",
                "selection_background": "#7B68EE",
                "selection_foreground": "#FFFFFF",
                "hover_background": "#3A3A3A",
            },
            css_path=str(RESOURCES_DIR / "themes/dark.qss"),
            metadata={
                "author": "UCAN Team",
                "version": "1.0",
                "description": "Tema escuro padrão do UCAN",
            },
        )

        # Carrega os arquivos CSS adicionais
        css_files = [
            RESOURCES_DIR / "themes/dark.qss",
            RESOURCES_DIR / "styles/knowledge.qss",  # Novo arquivo de estilo
        ]

        # Combina todos os arquivos CSS em um único stylesheet
        combined_css = ""
        for css_file in css_files:
            if css_file.exists():
                with open(css_file, "r", encoding="utf-8") as f:
                    combined_css += f.read() + "\n"

        # Cria um arquivo temporário com o CSS combinado
        temp_css_path = RESOURCES_DIR / "themes/dark_combined.qss"
        with open(temp_css_path, "w", encoding="utf-8") as f:
            f.write(combined_css)

        # Atualiza o caminho do CSS no tema
        dark_theme.css_path = str(temp_css_path)

        self._themes["dark"] = dark_theme
        self._current_theme = dark_theme

        light_theme = Theme(
            id="light",
            name="Light Theme",
            colors={
                "background": "#ffffff",
                "foreground": "#000000",
                "secondary_background": "#f0f0f0",
                "accent": "#7B68EE",
                "button_background": "#7B68EE",
                "button_foreground": "#ffffff",
                "button_hover_background": "#9370DB",
                "button_active_background": "#6A5ACD",
                "input_background": "#ffffff",
                "input_foreground": "#000000",
                "hover_background": "rgba(123, 104, 238, 0.12)",
                "selection_background": "rgba(123, 104, 238, 0.20)",
                "selection_foreground": "#000000",
                "border": "#cccccc",
            },
            is_dark=False,
        )

        high_contrast = Theme(
            id="high_contrast",
            name="High Contrast",
            colors={
                "background": "#000000",
                "foreground": "#ffffff",
                "secondary_background": "#0a0a0a",
                "accent": "#ffffff",
                "button_background": "#000000",
                "button_foreground": "#ffffff",
                "button_hover_background": "#333333",
                "button_active_background": "#555555",
                "input_background": "#000000",
                "input_foreground": "#ffffff",
                "hover_background": "#333333",
                "selection_background": "#ffffff",
                "selection_foreground": "#000000",
                "border": "#ffffff",
            },
            is_dark=True,
            is_high_contrast=True,
        )

        self._themes.update({
            "dark": dark_theme,
            "light": light_theme,
            "high_contrast": high_contrast,
        })

    def _load_custom_themes(self):
        """Load custom themes from disk."""
        if not self._themes_dir.exists():
            return

        for theme_file in self._themes_dir.glob("*.json"):
            try:
                with open(theme_file, "r", encoding="utf-8") as f:
                    theme_data = json.load(f)
                theme = Theme.from_dict(theme_data)
                self._themes[theme.id] = theme
            except Exception as e:
                print(f"Error loading theme {theme_file}: {e}")

    def get_theme(self, theme_id: str) -> Optional[Theme]:
        """Get a theme by its ID."""
        return self._themes.get(theme_id)

    def get_themes(self) -> List[Theme]:
        """Get all available themes."""
        return list(self._themes.values())

    def set_theme(self, theme_id: str) -> bool:
        """Set the current theme."""
        theme = self.get_theme(theme_id)
        if theme:
            self._current_theme = theme
            self.theme_changed.emit(theme)
            return True
        return False

    def add_custom_theme(self, theme: Theme) -> bool:
        """Add a new custom theme."""
        if theme.id in self._themes:
            return False

        self._themes[theme.id] = theme
        theme_path = self._themes_dir / f"{theme.id}.json"

        try:
            self._themes_dir.mkdir(parents=True, exist_ok=True)
            with open(theme_path, "w", encoding="utf-8") as f:
                json.dump(theme.to_dict(), f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving theme {theme.id}: {e}")
            return False

    def remove_custom_theme(self, theme_id: str) -> bool:
        """Remove a custom theme."""
        if theme_id not in self._themes or theme_id in [
            "dark",
            "light",
            "high_contrast",
        ]:
            return False

        theme_path = self._themes_dir / f"{theme_id}.json"
        try:
            theme_path.unlink(missing_ok=True)
            del self._themes[theme_id]
            return True
        except Exception as e:
            print(f"Error removing theme {theme_id}: {e}")
            return False


# Create a global instance
theme_manager = ThemeManager()
