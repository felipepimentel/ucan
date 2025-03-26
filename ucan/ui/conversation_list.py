from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ucan.ui.icons import load_icon


class ConversationItem(QFrame):
    """Item que representa uma conversa na lista."""

    clicked = Signal(str)

    def __init__(
        self,
        conversation_id: str,
        title: str,
        preview: str,
        parent: Optional[QWidget] = None,
    ):
        """
        Inicializa o item de conversa.

        Args:
            conversation_id: ID da conversa
            title: Título da conversa
            preview: Prévia da última mensagem
            parent: Widget pai
        """
        super().__init__(parent)
        self.conversation_id = conversation_id
        self.setObjectName("conversationItem")
        self.setFrameStyle(QFrame.StyledPanel)
        self._setup_ui(title, preview)

    def _setup_ui(self, title: str, preview: str) -> None:
        """
        Configura a interface do item.

        Args:
            title: Título da conversa
            preview: Prévia da última mensagem
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Cabeçalho com ícone e título
        header = QHBoxLayout()
        header.setSpacing(8)

        icon = QLabel()
        icon.setPixmap(load_icon("chat.svg").pixmap(24, 24))
        header.addWidget(icon)

        title_label = QLabel(title)
        title_label.setObjectName("conversationTitle")
        header.addWidget(title_label)
        header.addStretch()

        layout.addLayout(header)

        # Prévia da mensagem
        if preview:
            preview_label = QLabel(preview)
            preview_label.setObjectName("conversationPreview")
            preview_label.setWordWrap(True)
            layout.addWidget(preview_label)

    def mousePressEvent(self, event) -> None:
        """
        Manipula evento de clique.

        Args:
            event: Evento de mouse
        """
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.conversation_id)


class ConversationList(QWidget):
    """Lista de conversas disponíveis."""

    conversation_selected = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Inicializa a lista de conversas.

        Args:
            parent: Widget pai
        """
        super().__init__(parent)
        self.setObjectName("conversationList")
        self._setup_ui()

        # Configura o tema
        from ucan.ui.theme_manager import theme_manager

        theme_manager.theme_changed.connect(self._apply_theme)
        self._apply_theme()

    def _setup_ui(self) -> None:
        """Configura a interface da lista."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Área de rolagem para conversas
        scroll = QScrollArea()
        scroll.setObjectName("conversationsScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Container para conversas
        self.conversations_container = QWidget()
        self.conversations_container.setObjectName("conversationsContainer")
        self.conversations_layout = QVBoxLayout(self.conversations_container)
        self.conversations_layout.setContentsMargins(16, 16, 16, 16)
        self.conversations_layout.setSpacing(16)
        self.conversations_layout.addStretch()

        scroll.setWidget(self.conversations_container)
        layout.addWidget(scroll)

    def add_conversation(
        self, conversation_id: str, title: str = "Nova Conversa", preview: str = ""
    ) -> None:
        """
        Adiciona uma conversa à lista.

        Args:
            conversation_id: ID da conversa
            title: Título da conversa
            preview: Prévia da última mensagem
        """
        item = ConversationItem(conversation_id, title, preview)
        item.clicked.connect(self.conversation_selected)
        # Inserir antes do stretch
        self.conversations_layout.insertWidget(
            self.conversations_layout.count() - 1, item
        )

    def clear(self) -> None:
        """Limpa todas as conversas da lista."""
        while self.conversations_layout.count() > 1:  # Manter o stretch
            item = self.conversations_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _apply_theme(self):
        """Aplica o tema atual."""
        from ucan.ui.theme_manager import theme_manager

        if theme := theme_manager.current_theme:
            self.setStyleSheet(theme.generate_stylesheet())
            # Atualiza também os componentes filhos importantes
            self.conversations_layout.setStyleSheet(theme.generate_stylesheet())
