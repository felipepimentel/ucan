"""
Widget principal do chat.
"""

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from ucan.controller import AppController
from ucan.ui.components import ChatInput, MessageBubble


class ChatWidget(QWidget):
    """Widget principal do chat."""

    message_sent = Signal(str)

    def __init__(self, controller: AppController, parent: Optional[QWidget] = None):
        """
        Inicializa o widget de chat.

        Args:
            controller: Controlador da aplicação
            parent: Widget pai
        """
        super().__init__(parent)
        self.controller = controller
        self.setObjectName("chatWidget")
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Configura a interface do widget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Área de rolagem para mensagens
        scroll = QScrollArea()
        scroll.setObjectName("messagesScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Container para mensagens
        self.messages_container = QWidget()
        self.messages_container.setObjectName("messagesContainer")
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setContentsMargins(16, 16, 16, 16)
        self.messages_layout.setSpacing(16)
        self.messages_layout.addStretch()

        scroll.setWidget(self.messages_container)
        layout.addWidget(scroll)

        # Campo de entrada
        self.chat_input = ChatInput()
        self.chat_input.message_sent.connect(self.message_sent)
        layout.addWidget(self.chat_input)

    def add_message(self, message: str, is_user: bool = False) -> None:
        """
        Adiciona uma mensagem ao chat.

        Args:
            message: Conteúdo da mensagem
            is_user: Se True, é uma mensagem do usuário
        """
        bubble = MessageBubble(message, is_user)
        # Inserir antes do stretch
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, bubble)
        # Rolar para a última mensagem
        self.messages_container.parent().ensureWidgetVisible(bubble)

    def clear_messages(self) -> None:
        """Limpa todas as mensagens do chat."""
        while self.messages_layout.count() > 1:  # Manter o stretch
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def load_conversation(self, conversation_id: str) -> None:
        """
        Carrega uma conversa no chat.

        Args:
            conversation_id: ID da conversa
        """
        # TODO: Implementar carregamento de mensagens
        pass
