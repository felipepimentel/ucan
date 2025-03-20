"""
Diálogo de gerenciamento de temas.
"""

import logging
from typing import Dict, Optional, Tuple

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ucan.ui.theme_manager import Theme, theme_manager

logger = logging.getLogger(__name__)


class ColorPicker(QWidget):
    """Widget para seleção de cor."""

    def __init__(self, initial_color: str = "#000000", parent=None):
        super().__init__(parent)
        self._color = QColor(initial_color)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.preview = QLabel()
        self.preview.setFixedSize(32, 32)
        self.preview.setStyleSheet(
            f"""
            background-color: {self._color.name()};
            border: 1px solid #32344a;
            border-radius: 4px;
            """
        )
        layout.addWidget(self.preview)

        self.button = QPushButton("Escolher")
        self.button.clicked.connect(self._show_color_dialog)
        layout.addWidget(self.button)

        layout.addStretch()

    def _show_color_dialog(self):
        if color := QColorDialog.getColor(self._color, self):
            if color.isValid():
                self._color = color
                self.preview.setStyleSheet(
                    f"""
                    background-color: {color.name()};
                    border: 1px solid #32344a;
                    border-radius: 4px;
                    """
                )

    def get_color(self) -> str:
        """Retorna a cor selecionada em formato hexadecimal."""
        return self._color.name()

    def set_color(self, color: str):
        """Define a cor do picker."""
        self._color = QColor(color)
        self.preview.setStyleSheet(
            f"""
            background-color: {color};
            border: 1px solid #32344a;
            border-radius: 4px;
            """
        )


class ThemeDialog(QDialog):
    """Diálogo de gerenciamento de temas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gerenciar Temas")
        self.setMinimumSize(800, 600)
        self._setup_ui()
        self._load_themes()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_switch_tab(), "Trocar Tema")
        self.tabs.addTab(self._create_create_tab(), "Criar Tema")
        layout.addWidget(self.tabs)

        # Botões
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.apply_button = QPushButton("Aplicar")
        self.apply_button.clicked.connect(self._apply_theme)
        button_layout.addWidget(self.apply_button)

        self.close_button = QPushButton("Fechar")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def _create_switch_tab(self) -> QWidget:
        """Cria a aba de troca de tema."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Seletor de tema
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Tema:"))

        self.theme_combo = QComboBox()
        self.theme_combo.currentIndexChanged.connect(self._on_theme_selected)
        theme_layout.addWidget(self.theme_combo)

        layout.addLayout(theme_layout)

        # Preview
        preview_label = QLabel("Preview:")
        layout.addWidget(preview_label)

        self.preview_widget = QWidget()
        self.preview_widget.setMinimumHeight(300)
        layout.addWidget(self.preview_widget)

        layout.addStretch()
        return tab

    def _create_create_tab(self) -> QWidget:
        """Cria a aba de criação de tema."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Scroll area para as configurações
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Container para as configurações
        container = QWidget()
        form_layout = QFormLayout(container)

        # Campos básicos
        self.name_input = QLineEdit()
        form_layout.addRow("Nome:", self.name_input)

        self.id_input = QLineEdit()
        form_layout.addRow("ID:", self.id_input)

        # Opções
        self.is_dark_combo = QComboBox()
        self.is_dark_combo.addItems(["Escuro", "Claro"])
        form_layout.addRow("Tipo:", self.is_dark_combo)

        self.is_high_contrast_combo = QComboBox()
        self.is_high_contrast_combo.addItems(["Normal", "Alto Contraste"])
        form_layout.addRow("Contraste:", self.is_high_contrast_combo)

        # Cores
        form_layout.addRow(QLabel("\nCores Base:"))
        self.color_pickers: Dict[str, ColorPicker] = {}

        base_colors = {
            "background": "Fundo",
            "foreground": "Texto",
            "toolbar_background": "Barra de Ferramentas",
            "border": "Bordas",
            "accent": "Destaque",
            "accent_hover": "Destaque (Hover)",
        }

        for key, label in base_colors.items():
            picker = ColorPicker()
            self.color_pickers[key] = picker
            form_layout.addRow(f"{label}:", picker)

        form_layout.addRow(QLabel("\nBotões:"))
        button_colors = {
            "button_background": "Fundo",
            "button_text": "Texto",
            "button_border": "Borda",
            "button_hover_background": "Fundo (Hover)",
            "button_hover_border": "Borda (Hover)",
        }

        for key, label in button_colors.items():
            picker = ColorPicker()
            self.color_pickers[key] = picker
            form_layout.addRow(f"{label}:", picker)

        form_layout.addRow(QLabel("\nLista de Conversas:"))
        list_colors = {
            "sidebar_background": "Fundo",
            "item_background": "Item",
            "item_border": "Borda do Item",
            "item_hover_background": "Item (Hover)",
            "item_hover_border": "Borda do Item (Hover)",
            "item_selected_background": "Item Selecionado",
            "item_selected_border": "Borda do Item Selecionado",
        }

        for key, label in list_colors.items():
            picker = ColorPicker()
            self.color_pickers[key] = picker
            form_layout.addRow(f"{label}:", picker)

        form_layout.addRow(QLabel("\nMensagens:"))
        message_colors = {
            "chat_background": "Fundo do Chat",
            "message_background": "Mensagem",
            "message_border": "Borda da Mensagem",
            "user_message_background": "Mensagem do Usuário",
            "user_message_border": "Borda (Usuário)",
            "assistant_message_background": "Mensagem do Assistente",
            "assistant_message_border": "Borda (Assistente)",
        }

        for key, label in message_colors.items():
            picker = ColorPicker()
            self.color_pickers[key] = picker
            form_layout.addRow(f"{label}:", picker)

        form_layout.addRow(QLabel("\nInput:"))
        input_colors = {
            "input_background": "Fundo da Área",
            "input_field_background": "Fundo do Campo",
            "input_text": "Texto",
            "input_border": "Borda",
        }

        for key, label in input_colors.items():
            picker = ColorPicker()
            self.color_pickers[key] = picker
            form_layout.addRow(f"{label}:", picker)

        form_layout.addRow(QLabel("\nScrollbar:"))
        scroll_colors = {
            "scrollbar_background": "Fundo",
            "scrollbar_handle": "Handle",
            "scrollbar_handle_hover": "Handle (Hover)",
        }

        for key, label in scroll_colors.items():
            picker = ColorPicker()
            self.color_pickers[key] = picker
            form_layout.addRow(f"{label}:", picker)

        scroll.setWidget(container)
        layout.addWidget(scroll)

        # Botões de ação
        action_layout = QHBoxLayout()

        self.load_base_combo = QComboBox()
        self.load_base_combo.addItems(["Dark Theme", "Light Theme", "High Contrast"])
        action_layout.addWidget(QLabel("Carregar base:"))
        action_layout.addWidget(self.load_base_combo)

        self.load_base_button = QPushButton("Carregar")
        self.load_base_button.clicked.connect(self._load_base_theme)
        action_layout.addWidget(self.load_base_button)

        action_layout.addStretch()

        self.create_button = QPushButton("Criar Tema")
        self.create_button.clicked.connect(self._create_theme)
        action_layout.addWidget(self.create_button)

        layout.addLayout(action_layout)

        return tab

    def _load_themes(self):
        """Carrega os temas disponíveis no combo."""
        self.theme_combo.clear()
        for theme in theme_manager.get_themes():
            self.theme_combo.addItem(theme.name, theme.id)

    def _on_theme_selected(self, index: int):
        """Chamado quando um tema é selecionado no combo."""
        if index >= 0:
            theme_id = self.theme_combo.itemData(index)
            if theme := theme_manager.get_theme(theme_id):
                self._update_preview(theme)

    def _update_preview(self, theme: Theme):
        """Atualiza o preview com o tema selecionado."""
        self.preview_widget.setStyleSheet(theme.get_stylesheet())

    def _load_base_theme(self):
        """Carrega um tema base para edição."""
        theme_name = self.load_base_combo.currentText()
        theme_map = {
            "Dark Theme": "dark",
            "Light Theme": "light",
            "High Contrast": "high_contrast",
        }

        if theme := theme_manager.get_theme(theme_map[theme_name]):
            # Preenche os campos básicos
            self.name_input.setText(f"Custom {theme.name}")
            self.id_input.setText(f"custom_{theme.id}")
            self.is_dark_combo.setCurrentIndex(0 if theme.is_dark else 1)
            self.is_high_contrast_combo.setCurrentIndex(
                1 if theme.is_high_contrast else 0
            )

            # Preenche os color pickers
            for key, picker in self.color_pickers.items():
                if color := theme.colors.get(key):
                    picker.set_color(color)

    def _create_theme(self):
        """Cria um novo tema customizado."""
        name = self.name_input.text().strip()
        theme_id = self.id_input.text().strip()

        if not name or not theme_id:
            return

        colors = {key: picker.get_color() for key, picker in self.color_pickers.items()}

        theme = Theme(
            name=name,
            id=theme_id,
            colors=colors,
            is_dark=self.is_dark_combo.currentIndex() == 0,
            is_high_contrast=self.is_high_contrast_combo.currentIndex() == 1,
        )

        if theme_manager.add_custom_theme(theme):
            self._load_themes()
            self.theme_combo.setCurrentText(name)

    def _apply_theme(self):
        """Aplica o tema selecionado."""
        if index := self.theme_combo.currentIndex() >= 0:
            theme_id = self.theme_combo.itemData(index)
            theme_manager.set_theme(theme_id)

    def get_selected_theme(self) -> Optional[Tuple[str, str]]:
        """
        Retorna o tema selecionado.

        Returns:
            Tupla com (id, nome) do tema ou None se nenhum selecionado
        """
        if index := self.theme_combo.currentIndex() >= 0:
            return (
                self.theme_combo.itemData(index),
                self.theme_combo.itemText(index),
            )
        return None
