"""
Knowledge base dialog for the UCAN application.
"""

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
)

from ucan.core.knowledge_base import KnowledgeBase
from ucan.ui.theme_manager import theme_manager


class KnowledgeBaseDialog(QDialog):
    """Dialog for managing knowledge bases."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bases de Conhecimento")
        self.setMinimumSize(600, 400)
        self._setup_ui()
        self._setup_signals()
        self._apply_theme(theme_manager.get_current_theme())

    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)

        # Knowledge base list
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # Add knowledge base
        add_layout = QHBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nome da base de conhecimento")
        add_layout.addWidget(self.name_input)

        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Caminho da base de conhecimento")
        add_layout.addWidget(self.path_input)

        self.add_button = QPushButton("Adicionar")
        self.add_button.clicked.connect(self._add_knowledge_base)
        add_layout.addWidget(self.add_button)

        layout.addLayout(add_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.close_button = QPushButton("Fechar")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def _setup_signals(self):
        """Setup signal connections."""
        theme_manager.theme_changed.connect(self._apply_theme)

    def _add_knowledge_base(self):
        """Add a new knowledge base."""
        name = self.name_input.text().strip()
        path = self.path_input.text().strip()

        if name and path:
            knowledge_base = KnowledgeBase(name=name, path=path)
            self.list_widget.addItem(str(knowledge_base))
            self.name_input.clear()
            self.path_input.clear()

    def _apply_theme(self, theme):
        """Apply the current theme."""
        self.setStyleSheet(theme.get_stylesheet())
