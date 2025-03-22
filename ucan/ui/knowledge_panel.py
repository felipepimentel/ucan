"""
Painel de bases de conhecimento.
"""

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ucan.ui.icons import load_icon


class KnowledgeBaseItem(QFrame):
    """Item que representa uma base de conhecimento."""

    clicked = Signal(str)

    def __init__(
        self, kb_id: str, name: str, description: str, parent: Optional[QWidget] = None
    ):
        """
        Inicializa o item de base de conhecimento.

        Args:
            kb_id: ID da base de conhecimento
            name: Nome da base
            description: Descrição da base
            parent: Widget pai
        """
        super().__init__(parent)
        self.kb_id = kb_id
        self.setObjectName("knowledgeBaseItem")
        self.setFrameStyle(QFrame.StyledPanel)
        self._setup_ui(name, description)

    def _setup_ui(self, name: str, description: str) -> None:
        """
        Configura a interface do item.

        Args:
            name: Nome da base
            description: Descrição da base
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Cabeçalho com ícone e nome
        header = QHBoxLayout()
        header.setSpacing(8)

        icon = QLabel()
        icon.setPixmap(load_icon("book.svg").pixmap(24, 24))
        header.addWidget(icon)

        name_label = QLabel(name)
        name_label.setObjectName("kbName")
        header.addWidget(name_label)
        header.addStretch()

        layout.addLayout(header)

        # Descrição
        if description:
            desc_label = QLabel(description)
            desc_label.setObjectName("kbDescription")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

    def mousePressEvent(self, event) -> None:
        """
        Manipula evento de clique.

        Args:
            event: Evento de mouse
        """
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.kb_id)


class KnowledgePanel(QWidget):
    """Painel que exibe e gerencia bases de conhecimento."""

    kb_selected = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Inicializa o painel de conhecimento.

        Args:
            parent: Widget pai
        """
        super().__init__(parent)
        self.setObjectName("knowledgePanel")
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Configura a interface do painel."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Área de ações
        actions = QWidget()
        actions.setObjectName("kbActions")
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(16, 16, 16, 16)
        actions_layout.setSpacing(8)

        # Botão de adicionar arquivo
        add_file_btn = QPushButton()
        add_file_btn.setIcon(QIcon.fromTheme("document-new"))
        add_file_btn.setText("Arquivo")
        add_file_btn.setToolTip("Adicionar arquivo à base")
        add_file_btn.clicked.connect(self._on_add_file)
        actions_layout.addWidget(add_file_btn)

        # Botão de adicionar URL
        add_url_btn = QPushButton()
        add_url_btn.setIcon(QIcon.fromTheme("web-browser"))
        add_url_btn.setText("URL")
        add_url_btn.setToolTip("Adicionar URL à base")
        add_url_btn.clicked.connect(self._on_add_url)
        actions_layout.addWidget(add_url_btn)

        actions_layout.addStretch()

        layout.addWidget(actions)

        # Área de rolagem para as bases
        scroll = QScrollArea()
        scroll.setObjectName("kbScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Container para as bases
        self.kb_container = QWidget()
        self.kb_container.setObjectName("kbContainer")
        self.kb_layout = QVBoxLayout(self.kb_container)
        self.kb_layout.setContentsMargins(16, 16, 16, 16)
        self.kb_layout.setSpacing(16)
        self.kb_layout.addStretch()

        scroll.setWidget(self.kb_container)
        layout.addWidget(scroll)

    def add_knowledge_base(self, kb_id: str, name: str, description: str) -> None:
        """
        Adiciona uma base de conhecimento ao painel.

        Args:
            kb_id: ID da base
            name: Nome da base
            description: Descrição da base
        """
        item = KnowledgeBaseItem(kb_id, name, description)
        item.clicked.connect(self.kb_selected)
        # Inserir antes do stretch
        self.kb_layout.insertWidget(self.kb_layout.count() - 1, item)

    def clear(self) -> None:
        """Limpa todas as bases de conhecimento."""
        while self.kb_layout.count() > 1:  # Manter o stretch
            item = self.kb_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _on_add_file(self) -> None:
        """Callback para adicionar arquivo."""
        # Implementar lógica de adicionar arquivo
        pass

    def _on_add_url(self) -> None:
        """Callback para adicionar URL."""
        # Implementar lógica de adicionar URL
        pass
