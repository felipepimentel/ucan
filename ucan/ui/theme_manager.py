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

from ucan.config.constants import RESOURCES_DIR


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

    theme_changed = Signal()

    def __init__(self):
        """Initialize the theme manager."""
        super().__init__()
        self._themes: Dict[str, Theme] = {}
        self._current_theme: Optional[Theme] = None
        self._themes_dir = RESOURCES_DIR / "themes"
        self._styles_dir = RESOURCES_DIR / "styles"

        # Garantir que os diretórios existam
        self._themes_dir.mkdir(parents=True, exist_ok=True)
        self._styles_dir.mkdir(parents=True, exist_ok=True)

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
        css_files = [
            self._styles_dir / "main.css",
            self._styles_dir / "chat.css",
            self._styles_dir / "knowledge.qss",
        ]

        for css_file in css_files:
            if css_file.exists():
                absolute_path = str(css_file.absolute())
                print(f"Watching CSS file: {absolute_path}")
                self._file_watcher.addPath(absolute_path)

    def _on_css_file_changed(self, path):
        """Chamado quando um arquivo CSS é modificado."""
        print(f"CSS file changed: {path}")
        # Re-adiciona o arquivo ao watcher (necessário em alguns sistemas)
        if os.path.exists(path):
            if path in self._file_watcher.files():
                self._file_watcher.removePath(path)
            self._file_watcher.addPath(path)

        # Usa um timer para evitar múltiplas atualizações
        self._reload_timer.start(100)  # 100ms debounce

    def _reload_current_theme(self):
        """Recarrega o tema atual."""
        if self._current_theme:
            current_theme_id = self._current_theme.id
            self._load_builtin_themes()
            if current_theme_id in self._themes:
                self._current_theme = self._themes[current_theme_id]
                self.theme_changed.emit()

    def _load_builtin_themes(self):
        """Carrega os temas embutidos."""
        # Garante que os diretórios existam
        self._themes_dir.mkdir(parents=True, exist_ok=True)
        self._styles_dir.mkdir(parents=True, exist_ok=True)

        # Copia os arquivos CSS do pacote se necessário
        package_styles = Path(__file__).parent.parent / "ui" / "styles"
        if package_styles.exists():
            import shutil

            # Corrige o padrão de glob que pode não funcionar em alguns sistemas
            for style_file in list(package_styles.glob("*.css")) + list(
                package_styles.glob("*.qss")
            ):
                target = self._styles_dir / style_file.name
                if not target.exists():
                    try:
                        shutil.copy2(style_file, target)
                        print(f"Copiado arquivo de estilo: {style_file} -> {target}")
                    except Exception as e:
                        print(f"Erro ao copiar arquivo de estilo {style_file}: {e}")

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
            metadata={
                "author": "UCAN Team",
                "version": "1.0",
                "description": "Tema escuro padrão do UCAN",
            },
        )

        # Carrega os arquivos CSS adicionais
        css_files = [
            self._styles_dir / "main.css",
            self._styles_dir / "chat.css",
            self._styles_dir / "knowledge.qss",
        ]

        # Combina todos os arquivos CSS em um único stylesheet
        combined_css = []
        
        # Primeiro adiciona o CSS base do tema
        combined_css.append(dark_theme.generate_stylesheet())
        
        # Depois adiciona os arquivos CSS personalizados
        for css_file in css_files:
            if css_file.exists():
                try:
                    with open(css_file, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:  # Só adiciona se não estiver vazio
                            if css_file.suffix == '.qss':
                                # Wrap QSS files to ensure they're properly applied
                                content = f"/* Begin {css_file.name} */\n{content}\n/* End {css_file.name} */"
                            combined_css.append(content)
                            print(f"Carregado arquivo de estilo: {css_file} ({len(content)} bytes)")
                except Exception as e:
                    print(f"Erro ao carregar arquivo CSS {css_file}: {e}")

        # Cria um arquivo temporário com o CSS combinado
        temp_css_path = self._styles_dir / "dark_combined.css"
        temp_css_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(temp_css_path, "w", encoding="utf-8") as f:
                f.write("\n\n".join(combined_css))
            print(f"CSS combinado salvo em: {temp_css_path}")
        except Exception as e:
            print(f"Erro ao salvar CSS combinado: {e}")

        # Atualiza o caminho do CSS no tema
        dark_theme.css_path = str(temp_css_path)

        self._themes["dark"] = dark_theme
        self._current_theme = dark_theme

        # Configura o watcher para os arquivos CSS
        for css_file in css_files:
            if css_file.exists():
                absolute_path = str(css_file.absolute())
                print(f"Watching CSS file: {absolute_path}")
                if absolute_path not in self._file_watcher.files():
                    self._file_watcher.addPath(absolute_path)

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
            self.theme_changed.emit()
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
