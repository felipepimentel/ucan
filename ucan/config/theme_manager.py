"""
Gerenciador de temas da aplicação.
"""

from dataclasses import dataclass
from typing import Dict, Tuple

import dearpygui.dearpygui as dpg

from ucan.config.constants import DEFAULT_THEME


@dataclass
class Theme:
    """Representa um tema da aplicação."""

    window_bg: Tuple[int, int, int]
    text: Tuple[int, int, int]
    border: Tuple[int, int, int]
    button: Tuple[int, int, int]
    button_hovered: Tuple[int, int, int]
    button_active: Tuple[int, int, int]
    accent: Tuple[int, int, int]


class ThemeManager:
    """Gerencia os temas da aplicação."""

    def __init__(self):
        """Inicializa o gerenciador de temas."""
        self._themes: Dict[str, Theme] = {}
        self._current_theme: str = "default"
        self._setup_default_theme()

    def _setup_default_theme(self):
        """Configura o tema padrão."""
        self._themes["default"] = Theme(**DEFAULT_THEME)

    def apply_theme(self, theme_id: str = "default") -> None:
        """
        Aplica um tema à aplicação.

        Args:
            theme_id: ID do tema a ser aplicado
        """
        if theme_id not in self._themes:
            return

        theme = self._themes[theme_id]
        self._current_theme = theme_id

        with dpg.theme() as dpg_theme:
            with dpg.theme_component(dpg.mvAll):
                # Cores base
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, theme.window_bg)
                dpg.add_theme_color(dpg.mvThemeCol_Text, theme.text)
                dpg.add_theme_color(dpg.mvThemeCol_Border, theme.border)

                # Botões e interativos
                dpg.add_theme_color(dpg.mvThemeCol_Button, theme.button)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, theme.button_hovered)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, theme.button_active)

                # Estilos
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 6)

        dpg.bind_theme(dpg_theme)

    def add_theme(self, theme_id: str, theme: Theme) -> None:
        """
        Adiciona um novo tema.

        Args:
            theme_id: ID do tema
            theme: Tema a ser adicionado
        """
        self._themes[theme_id] = theme

    def get_theme(self, theme_id: str) -> Theme:
        """
        Obtém um tema pelo ID.

        Args:
            theme_id: ID do tema

        Returns:
            O tema solicitado ou o tema padrão se não encontrado
        """
        return self._themes.get(theme_id, self._themes["default"])

    def get_current_theme(self) -> Theme:
        """
        Obtém o tema atual.

        Returns:
            O tema atual
        """
        return self._themes[self._current_theme]

    def get_theme_ids(self) -> list[str]:
        """
        Obtém os IDs dos temas disponíveis.

        Returns:
            Lista de IDs dos temas
        """
        return list(self._themes.keys())


# Instância global do gerenciador de temas
theme_manager = ThemeManager()
