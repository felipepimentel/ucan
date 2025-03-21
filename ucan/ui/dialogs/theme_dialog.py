"""
Theme dialog for UCAN application.

This dialog allows users to manage themes, including switching between themes,
creating new themes, and customizing existing ones.
"""

import logging
from typing import Optional, Tuple

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ucan.ui.theme_manager import Theme, theme_manager

logger = logging.getLogger(__name__)


class ColorPicker(QWidget):
    """Widget for picking colors with preview."""

    def __init__(self, initial_color: str = "#000000", parent=None):
        """Initialize the color picker."""
        super().__init__(parent)
        self._color = QColor(initial_color)
        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.color_button = QPushButton()
        self.color_button.setFixedSize(30, 30)
        self.color_button.clicked.connect(self._show_color_dialog)

        self.color_value = QLineEdit(self._color.name())
        self.color_value.setFixedWidth(100)
        self.color_value.textChanged.connect(self._update_from_text)

        layout.addWidget(self.color_button)
        layout.addWidget(self.color_value)

        self._update_preview()

    def _show_color_dialog(self):
        """Show the color picker dialog."""
        color = QColorDialog.getColor(self._color, self)
        if color.isValid():
            self._color = color
            self._update_preview()

    def _update_preview(self):
        """Update the color preview."""
        self.color_button.setStyleSheet(
            f"background-color: {self._color.name()};border: 1px solid #888888;"
        )
        self.color_value.setText(self._color.name())

    def _update_from_text(self, text: str):
        """Update color from text input."""
        color = QColor(text)
        if color.isValid():
            self._color = color
            self._update_preview()

    def get_color(self) -> str:
        """Get the selected color as a hex string."""
        return self._color.name()

    def set_color(self, color: str):
        """Set the current color."""
        self._color = QColor(color)
        self._update_preview()


class ThemeDialog(QDialog):
    """Dialog for managing themes."""

    def __init__(self, parent=None):
        """Initialize the theme dialog."""
        super().__init__(parent)
        self.setWindowTitle("Temas")
        self.setMinimumSize(600, 400)
        self._setup_ui()
        self._load_themes()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Tabs
        self.tab_widget = QTabWidget()
        self.switch_tab = QWidget()
        self.create_tab = QWidget()

        self.tab_widget.addTab(self.switch_tab, "Trocar Tema")
        self.tab_widget.addTab(self.create_tab, "Criar Tema")

        # Switch theme tab
        switch_layout = QVBoxLayout(self.switch_tab)

        theme_layout = QHBoxLayout()
        theme_label = QLabel("Tema:")
        self.theme_combo = QComboBox()
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()

        switch_layout.addLayout(theme_layout)
        switch_layout.addStretch()

        # Create theme tab
        create_layout = QFormLayout(self.create_tab)

        self.name_input = QLineEdit()
        self.dark_mode = QCheckBox("Modo Escuro")
        self.high_contrast = QCheckBox("Alto Contraste")

        create_layout.addRow("Nome:", self.name_input)
        create_layout.addRow("", self.dark_mode)
        create_layout.addRow("", self.high_contrast)

        # Color pickers
        self.color_pickers = {}
        colors = [
            ("background", "Fundo"),
            ("foreground", "Texto"),
            ("button_background", "Fundo do Botão"),
            ("button_foreground", "Texto do Botão"),
            ("button_hover_background", "Fundo do Botão (Hover)"),
            ("input_background", "Fundo do Input"),
            ("input_foreground", "Texto do Input"),
            ("border", "Borda"),
        ]

        for color_id, label in colors:
            picker = ColorPicker()
            create_layout.addRow(f"{label}:", picker)
            self.color_pickers[color_id] = picker

        # Buttons
        button_layout = QHBoxLayout()

        self.apply_button = QPushButton("Aplicar")
        self.apply_button.clicked.connect(self._apply_theme)

        self.create_button = QPushButton("Criar")
        self.create_button.clicked.connect(self._create_theme)

        self.close_button = QPushButton("Fechar")
        self.close_button.clicked.connect(self.close)

        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.close_button)

        # Main layout
        layout.addWidget(self.tab_widget)
        layout.addLayout(button_layout)

    def _load_themes(self):
        """Load available themes into the combo box."""
        self.theme_combo.clear()

        for theme in theme_manager.get_themes():
            self.theme_combo.addItem(theme.name, theme.id)

        # Seleciona o tema atual
        current_theme = theme_manager.current_theme
        if current_theme:
            index = self.theme_combo.findData(current_theme.id)
            if index >= 0:
                self.theme_combo.setCurrentIndex(index)

    def _apply_theme(self):
        """Apply the selected theme."""
        if self.tab_widget.currentIndex() == 0:
            # Switch theme tab
            theme_id = self.theme_combo.currentData()
            if theme_id:
                theme_manager.set_theme(theme_id)

    def _create_theme(self):
        """Create a new theme from the form data."""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(
                self,
                "Erro",
                "Por favor, insira um nome para o tema.",
            )
            return

        # Generate a theme ID from the name
        theme_id = name.lower().replace(" ", "_")

        # Collect colors
        colors = {key: picker.get_color() for key, picker in self.color_pickers.items()}

        # Create the theme
        theme = Theme(
            id=theme_id,
            name=name,
            colors=colors,
            is_dark=self.dark_mode.isChecked(),
            is_high_contrast=self.high_contrast.isChecked(),
        )

        # Add the theme
        if theme_manager.add_custom_theme(theme):
            QMessageBox.information(
                self,
                "Sucesso",
                f"Tema '{name}' criado com sucesso.",
            )
            self._load_themes()
            self.tab_widget.setCurrentIndex(0)
            index = self.theme_combo.findData(theme_id)
            if index >= 0:
                self.theme_combo.setCurrentIndex(index)
        else:
            QMessageBox.warning(
                self,
                "Erro",
                f"Não foi possível criar o tema '{name}'.",
            )

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
