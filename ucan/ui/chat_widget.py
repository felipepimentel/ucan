"""
Widget principal do chat.
"""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import QEvent, QObject, Qt, Signal
from PySide6.QtGui import QIcon, QKeyEvent, QTextCursor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ChatWidget(QWidget):
    """Widget para exibição e interação com o chat."""

    message_sent = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Inicializa o widget de chat.

        Args:
            parent: Widget pai
        """
        super().__init__(parent)
        self.setObjectName("chatWidget")
        self._setup_ui()

        # Configura o tema
        from ucan.ui.theme_manager import theme_manager

        theme_manager.theme_changed.connect(self._apply_theme)
        self._apply_theme()

    def _setup_ui(self):
        """Configura a interface do chat."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Área de mensagens
        self.messages_container = QWidget()
        self.messages_container.setObjectName("messagesContainer")
        messages_layout = QVBoxLayout(self.messages_container)
        messages_layout.setContentsMargins(0, 0, 0, 0)
        messages_layout.setSpacing(0)

        self.messages_area = QTextEdit()
        self.messages_area.setObjectName("messagesArea")
        self.messages_area.setReadOnly(True)
        messages_layout.addWidget(self.messages_area)

        layout.addWidget(self.messages_container, stretch=1)

        # Área de entrada
        input_container = QWidget()
        input_container.setObjectName("chatInputContainer")
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(8, 8, 8, 8)
        input_layout.setSpacing(8)

        self.input_field = QTextEdit()
        self.input_field.setObjectName("chatInputField")
        self.input_field.setPlaceholderText(
            "Digite sua mensagem... (Enter para enviar, Shift+Enter para nova linha)"
        )
        self.input_field.setMaximumHeight(120)
        input_layout.addWidget(self.input_field)

        send_button = QPushButton()
        send_button.setObjectName("chatSendButton")
        send_button.setIcon(
            QIcon(
                str(
                    Path(__file__).parent.parent.parent
                    / "assets"
                    / "icons"
                    / "send.svg"
                )
            )
        )
        send_button.setFixedSize(40, 40)
        send_button.clicked.connect(self._send_message)
        input_layout.addWidget(send_button)

        layout.addWidget(input_container)

        # Conecta o evento de tecla pressionada
        self.input_field.installEventFilter(self)

    def _apply_theme(self):
        """Aplica o tema atual."""
        from ucan.ui.theme_manager import theme_manager

        if theme := theme_manager.current_theme:
            self.setStyleSheet(theme.generate_stylesheet())
            # Atualiza também os componentes filhos importantes
            self.messages_container.setStyleSheet(theme.generate_stylesheet())
            self.messages_area.setStyleSheet(theme.generate_stylesheet())
            self.input_field.setStyleSheet(theme.generate_stylesheet())

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """Filtra eventos do campo de entrada."""
        if obj == self.input_field and event.type() == QEvent.KeyPress:
            key_event = QKeyEvent(event)
            if (
                key_event.key() == Qt.Key_Return
                and not key_event.modifiers() & Qt.ShiftModifier
            ):
                self._send_message()
                return True
            elif (
                key_event.key() == Qt.Key_Return
                and key_event.modifiers() & Qt.ShiftModifier
            ):
                cursor = self.input_field.textCursor()
                cursor.insertText("\n")
                return True
        return super().eventFilter(obj, event)

    def _send_message(self):
        """Envia a mensagem atual."""
        message = self.input_field.toPlainText().strip()
        if message:
            self._add_message("Você", message)
            self.input_field.clear()
            self.message_sent.emit(message)

    def _add_message(self, sender: str, content: str):
        """Adiciona uma mensagem à área de chat."""
        cursor = self.messages_area.textCursor()
        cursor.movePosition(QTextCursor.End)

        # Adiciona espaçamento entre mensagens
        if not cursor.atStart():
            cursor.insertText("\n\n")

        # Formata a mensagem
        cursor.insertHtml(f"<b>{sender}:</b><br>")
        cursor.insertText(content)

        # Move o cursor para o final
        cursor.movePosition(QTextCursor.End)
        self.messages_area.setTextCursor(cursor)
        self.messages_area.ensureCursorVisible()
