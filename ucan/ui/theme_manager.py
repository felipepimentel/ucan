"""
Theme manager for the UCAN application.
"""

import json
import logging
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor

from ucan.config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class Theme:
    """Theme configuration."""

    name: str
    id: str
    colors: Dict[str, str]
    is_dark: bool = True
    is_high_contrast: bool = False
    metadata: Dict[str, str] = None

    def to_dict(self) -> dict:
        """Convert theme to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Theme":
        """Create theme from dictionary."""
        return cls(**data)

    def get_color(self, key: str) -> QColor:
        """Obtém uma cor do tema."""
        return QColor(self.colors.get(key, "#000000"))

    def get_stylesheet(self) -> str:
        """Generate stylesheet from theme colors."""
        return f"""
            /* Main Window */
            QMainWindow {{
                background-color: {self.colors["background"]};
                color: {self.colors["foreground"]};
            }}

            /* Toolbar */
            QToolBar {{
                background-color: {self.colors["toolbar_background"]};
                border: none;
                spacing: 8px;
                padding: 4px;
            }}

            QToolButton {{
                background-color: {self.colors["button_background"]};
                color: {self.colors["button_text"]};
                border: 1px solid {self.colors["button_border"]};
                border-radius: 4px;
                padding: 4px;
            }}

            QToolButton:hover {{
                background-color: {self.colors["button_hover_background"]};
                border-color: {self.colors["button_hover_border"]};
            }}

            /* Conversation List */
            QListWidget {{
                background-color: {self.colors["sidebar_background"]};
                border: none;
                padding: 4px;
            }}

            QListWidget::item {{
                background-color: {self.colors["item_background"]};
                border: 1px solid {self.colors["item_border"]};
                border-radius: 4px;
                padding: 8px;
                margin: 2px 4px;
            }}

            QListWidget::item:hover {{
                background-color: {self.colors["item_hover_background"]};
                border-color: {self.colors["item_hover_border"]};
            }}

            QListWidget::item:selected {{
                background-color: {self.colors["item_selected_background"]};
                border-color: {self.colors["item_selected_border"]};
            }}

            /* Chat Area */
            QScrollArea {{
                background-color: {self.colors["chat_background"]};
                border: none;
            }}

            QWidget#messageContainer {{
                background-color: {self.colors["message_background"]};
                border: 1px solid {self.colors["message_border"]};
                border-radius: 4px;
                padding: 12px;
                margin: 4px 8px;
            }}

            QWidget#userMessageContainer {{
                background-color: {self.colors["user_message_background"]};
                border-color: {self.colors["user_message_border"]};
            }}

            QWidget#assistantMessageContainer {{
                background-color: {self.colors["assistant_message_background"]};
                border-color: {self.colors["assistant_message_border"]};
            }}

            /* Input Area */
            QWidget#inputArea {{
                background-color: {self.colors["input_background"]};
                border: none;
                padding: 8px;
            }}

            QTextEdit#inputText {{
                background-color: {self.colors["input_field_background"]};
                color: {self.colors["input_text"]};
                border: 1px solid {self.colors["input_border"]};
                border-radius: 4px;
                padding: 8px;
            }}

            /* Scrollbar */
            QScrollBar:vertical {{
                background-color: {self.colors["scrollbar_background"]};
                width: 12px;
                margin: 0;
            }}

            QScrollBar::handle:vertical {{
                background-color: {self.colors["scrollbar_handle"]};
                min-height: 40px;
                border-radius: 6px;
            }}

            QScrollBar::handle:vertical:hover {{
                background-color: {self.colors["scrollbar_handle_hover"]};
            }}

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0;
            }}

            QScrollBar:horizontal {{
                background-color: {self.colors["scrollbar_background"]};
                height: 12px;
                margin: 0;
            }}

            QScrollBar::handle:horizontal {{
                background-color: {self.colors["scrollbar_handle"]};
                min-width: 40px;
                border-radius: 6px;
            }}

            QScrollBar::handle:horizontal:hover {{
                background-color: {self.colors["scrollbar_handle_hover"]};
            }}

            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {{
                width: 0;
            }}
        """


class ThemeManager(QObject):
    """Theme manager."""

    theme_changed = Signal(Theme)
    themes_updated = Signal(list)

    def __init__(self):
        super().__init__()
        self.themes_dir = settings.ROOT_DIR / "themes"
        self.themes_dir.mkdir(parents=True, exist_ok=True)
        self._themes: Dict[str, Theme] = {}
        self._current_theme: Optional[Theme] = None
        self._load_builtin_themes()
        self._load_custom_themes()

    def _load_builtin_themes(self):
        """Load built-in themes."""
        dark_theme = Theme(
            name="Dark Theme",
            id="dark",
            colors={
                # Base colors
                "background": "#1a1b26",
                "foreground": "#a9b1d6",
                "toolbar_background": "#24283b",
                "border": "#32344a",
                "accent": "#7aa2f7",
                "accent_hover": "#3d59a1",
                # Button colors
                "button_background": "#24283b",
                "button_text": "#a9b1d6",
                "button_border": "#32344a",
                "button_hover_background": "#32344a",
                "button_hover_border": "#7aa2f7",
                # List colors
                "sidebar_background": "#24283b",
                "item_background": "#1a1b26",
                "item_border": "#32344a",
                "item_hover_background": "#32344a",
                "item_hover_border": "#7aa2f7",
                "item_selected_background": "#32344a",
                "item_selected_border": "#7aa2f7",
                # Message colors
                "chat_background": "#1a1b26",
                "message_background": "#24283b",
                "message_border": "#32344a",
                "user_message_background": "#32344a",
                "user_message_border": "#7aa2f7",
                "assistant_message_background": "#24283b",
                "assistant_message_border": "#32344a",
                # Input colors
                "input_background": "#24283b",
                "input_field_background": "#1a1b26",
                "input_text": "#a9b1d6",
                "input_border": "#32344a",
                # Scrollbar colors
                "scrollbar_background": "#1a1b26",
                "scrollbar_handle": "#32344a",
                "scrollbar_handle_hover": "#7aa2f7",
            },
            is_dark=True,
            is_high_contrast=False,
        )

        light_theme = Theme(
            name="Light Theme",
            id="light",
            colors={
                # Base colors
                "background": "#ffffff",
                "foreground": "#24283b",
                "toolbar_background": "#f0f0f0",
                "border": "#d0d0d0",
                "accent": "#2f7ed8",
                "accent_hover": "#1a4a94",
                # Button colors
                "button_background": "#f0f0f0",
                "button_text": "#24283b",
                "button_border": "#d0d0d0",
                "button_hover_background": "#e0e0e0",
                "button_hover_border": "#2f7ed8",
                # List colors
                "sidebar_background": "#f0f0f0",
                "item_background": "#ffffff",
                "item_border": "#d0d0d0",
                "item_hover_background": "#e0e0e0",
                "item_hover_border": "#2f7ed8",
                "item_selected_background": "#e0e0e0",
                "item_selected_border": "#2f7ed8",
                # Message colors
                "chat_background": "#ffffff",
                "message_background": "#f0f0f0",
                "message_border": "#d0d0d0",
                "user_message_background": "#e0e0e0",
                "user_message_border": "#2f7ed8",
                "assistant_message_background": "#f0f0f0",
                "assistant_message_border": "#d0d0d0",
                # Input colors
                "input_background": "#f0f0f0",
                "input_field_background": "#ffffff",
                "input_text": "#24283b",
                "input_border": "#d0d0d0",
                # Scrollbar colors
                "scrollbar_background": "#ffffff",
                "scrollbar_handle": "#d0d0d0",
                "scrollbar_handle_hover": "#2f7ed8",
            },
            is_dark=False,
            is_high_contrast=False,
        )

        high_contrast_theme = Theme(
            name="High Contrast",
            id="high_contrast",
            colors={
                # Base colors
                "background": "#000000",
                "foreground": "#ffffff",
                "toolbar_background": "#000000",
                "border": "#ffffff",
                "accent": "#ffff00",
                "accent_hover": "#ffff80",
                # Button colors
                "button_background": "#000000",
                "button_text": "#ffffff",
                "button_border": "#ffffff",
                "button_hover_background": "#ffffff",
                "button_hover_border": "#ffff00",
                # List colors
                "sidebar_background": "#000000",
                "item_background": "#000000",
                "item_border": "#ffffff",
                "item_hover_background": "#ffffff",
                "item_hover_border": "#ffff00",
                "item_selected_background": "#ffffff",
                "item_selected_border": "#ffff00",
                # Message colors
                "chat_background": "#000000",
                "message_background": "#000000",
                "message_border": "#ffffff",
                "user_message_background": "#ffffff",
                "user_message_border": "#ffff00",
                "assistant_message_background": "#000000",
                "assistant_message_border": "#ffffff",
                # Input colors
                "input_background": "#000000",
                "input_field_background": "#000000",
                "input_text": "#ffffff",
                "input_border": "#ffffff",
                # Scrollbar colors
                "scrollbar_background": "#000000",
                "scrollbar_handle": "#ffffff",
                "scrollbar_handle_hover": "#ffff00",
            },
            is_dark=True,
            is_high_contrast=True,
        )

        self._themes = {
            "dark": dark_theme,
            "light": light_theme,
            "high_contrast": high_contrast_theme,
        }

        self._current_theme = dark_theme

    def _load_custom_themes(self):
        """Load custom themes from disk."""
        try:
            for theme_file in self.themes_dir.glob("*.json"):
                try:
                    with open(theme_file, "r", encoding="utf-8") as f:
                        theme_data = json.load(f)
                        theme = Theme.from_dict(theme_data)
                        self._themes[theme.id] = theme
                        logger.info(f"Loaded custom theme: {theme.name}")
                except Exception as e:
                    logger.error(f"Failed to load theme {theme_file}: {e}")
        except Exception as e:
            logger.error(f"Failed to load custom themes: {e}")

    def get_theme(self, theme_id: str) -> Optional[Theme]:
        """Get theme by ID."""
        return self._themes.get(theme_id)

    def get_themes(self) -> List[Theme]:
        """Get all available themes."""
        return list(self._themes.values())

    def set_theme(self, theme_id: str) -> bool:
        """Set current theme."""
        if theme := self.get_theme(theme_id):
            self._current_theme = theme
            self.theme_changed.emit(theme)
            return True
        return False

    def add_custom_theme(self, theme: Theme) -> bool:
        """Add a custom theme."""
        if theme.id in self._themes:
            return False

        try:
            themes_dir = self.themes_dir
            themes_dir.mkdir(parents=True, exist_ok=True)

            theme_file = themes_dir / f"{theme.id}.json"
            with open(theme_file, "w", encoding="utf-8") as f:
                json.dump(theme.to_dict(), f, indent=4)

            self._themes[theme.id] = theme
            logger.info(f"Added custom theme: {theme.name}")
            self.themes_updated.emit(self.get_themes())
            return True
        except Exception as e:
            logger.error(f"Failed to save theme {theme.name}: {e}")
            return False

    def remove_custom_theme(self, theme_id: str) -> bool:
        """Remove a custom theme."""
        if theme_id not in self._themes or theme_id in [
            "dark",
            "light",
            "high_contrast",
        ]:
            return False

        try:
            themes_dir = self.themes_dir
            theme_file = themes_dir / f"{theme_id}.json"
            if theme_file.exists():
                theme_file.unlink()

            del self._themes[theme_id]
            logger.info(f"Removed custom theme: {theme_id}")
            self.themes_updated.emit(self.get_themes())
            return True
        except Exception as e:
            logger.error(f"Failed to remove theme {theme_id}: {e}")
            return False

    def get_current_theme(self) -> Theme:
        """Get current theme."""
        return self._current_theme


# Global instance
theme_manager = ThemeManager()
