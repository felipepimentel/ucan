"""
Diálogo para criar ou editar tipos de conversa.
"""

from typing import Optional

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ConversationTypeDialog(QDialog):
    """Diálogo para criar ou editar tipos de conversa."""

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Inicializa o diálogo.

        Args:
            parent: Widget pai
        """
        super().__init__(parent)
        self.setWindowTitle("Tipo de Conversa")
        self._setup_ui()

    def _setup_ui(self):
        """Configura a interface do usuário."""
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Nome
        name_layout = QHBoxLayout()
        name_label = QLabel("Nome:")
        self.name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Descrição
        description_label = QLabel("Descrição:")
        self.description_input = QTextEdit()
        layout.addWidget(description_label)
        layout.addWidget(self.description_input)

        # Botões
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        save_button = QPushButton("Salvar")
        save_button.clicked.connect(self.accept)
        save_button.setDefault(True)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_values(self):
        """
        Obtém os valores do diálogo.

        Returns:
            Tupla com nome e descrição
        """
        return self.name_input.text(), self.description_input.toPlainText()
