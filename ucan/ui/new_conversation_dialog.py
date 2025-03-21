"""
New conversation dialog for the UCAN application.
"""

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from ucan.ui.theme_manager import theme_manager


class NewConversationDialog(QDialog):
    """Dialog for creating a new conversation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nova Conversa")
        self.setMinimumSize(400, 300)
        self._setup_ui()
        self._setup_signals()
        self._apply_theme(theme_manager.current_theme)

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)

        # Title
        title_layout = QHBoxLayout()
        title_label = QLabel("Título:")
        self.title_input = QLineEdit()
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.title_input)
        layout.addLayout(title_layout)

        # Type
        type_layout = QHBoxLayout()
        type_label = QLabel("Tipo:")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Geral", "Programação", "Pesquisa"])
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)

        # Description
        description_label = QLabel("Descrição:")
        self.description_input = QTextEdit()
        layout.addWidget(description_label)
        layout.addWidget(self.description_input)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.create_button = QPushButton("Criar")
        self.create_button.clicked.connect(self.accept)
        self.create_button.setDefault(True)
        button_layout.addWidget(self.create_button)

        layout.addLayout(button_layout)

    def _setup_signals(self):
        """Setup signal connections."""
        theme_manager.theme_changed.connect(self._apply_theme)

    def _apply_theme(self, theme):
        """Apply the current theme."""
        self.setStyleSheet(theme.get_stylesheet())

    def get_values(self):
        """Get the dialog values."""
        type_map = {
            "Geral": "general",
            "Programação": "programming",
            "Pesquisa": "research",
        }
        return (
            self.title_input.text(),
            type_map[self.type_combo.currentText()],
            self.description_input.toPlainText(),
        )
