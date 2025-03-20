"""Widget para exibição de mensagens."""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from ucan.core.message import Message, MessageType


class MessageWidget(QWidget):
    """Widget para exibição de mensagens."""

    def __init__(self, message: Message, parent=None):
        """Inicializa o widget de mensagem."""
        super().__init__(parent)
        self.message = message
        self._setup_ui()

    def _setup_ui(self):
        """Configura a interface do usuário."""
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Adiciona o ícone apropriado
        icon_label = QLabel()
        icon_path = self._get_icon_path()
        icon_pixmap = QPixmap(str(icon_path))
        icon_label.setPixmap(icon_pixmap)
        icon_label.setFixedSize(24, 24)
        layout.addWidget(icon_label)

        # Adiciona o conteúdo da mensagem
        message_label = QLabel(self.message.content)
        message_label.setWordWrap(True)
        message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(message_label, 1)

        self.setLayout(layout)

    def _get_icon_path(self) -> Path:
        """Retorna o caminho do ícone baseado no tipo da mensagem."""
        icons_dir = Path(__file__).parent.parent / "resources" / "icons"
        icon_map = {
            MessageType.USER: "user.svg",
            MessageType.ASSISTANT: "assistant.svg",
            MessageType.SYSTEM: "system.svg",
        }
        return icons_dir / icon_map[self.message.type]
