"""Widget para exibição de item de base de conhecimento."""

from pathlib import Path

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ucan.core.knowledge_base import KnowledgeBase


class KnowledgeBaseItem(QWidget):
    """Widget para exibição de item de base de conhecimento."""

    def __init__(self, knowledge_base: KnowledgeBase, parent=None):
        """Inicializa o widget de item de base de conhecimento."""
        super().__init__(parent)
        self.knowledge_base = knowledge_base
        self._setup_ui()

    def _setup_ui(self):
        """Configura a interface do usuário."""
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Adiciona o ícone
        icon_label = QLabel()
        icon_path = (
            Path(__file__).parent.parent / "resources" / "icons" / "knowledge.svg"
        )
        icon_pixmap = QPixmap(str(icon_path))
        icon_label.setPixmap(icon_pixmap)
        icon_label.setFixedSize(24, 24)
        layout.addWidget(icon_label)

        # Informações da base de conhecimento
        info_layout = QVBoxLayout()

        # Nome e escopo
        header_layout = QHBoxLayout()
        name_label = QLabel(self.knowledge_base.name)
        name_label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(name_label)

        scope_label = QLabel(f"({self.knowledge_base.scope})")
        scope_label.setStyleSheet("color: #666666;")
        header_layout.addWidget(scope_label)
        header_layout.addStretch()
        info_layout.addLayout(header_layout)

        # Descrição
        if self.knowledge_base.description:
            description_label = QLabel(self.knowledge_base.description)
            description_label.setWordWrap(True)
            description_label.setStyleSheet("color: #333333;")
            info_layout.addWidget(description_label)

        layout.addLayout(info_layout, 1)
        self.setLayout(layout)
