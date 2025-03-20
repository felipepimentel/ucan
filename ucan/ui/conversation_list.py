from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ucan.config.constants import RESOURCES_DIR
from ucan.core.app_controller import AppController
from ucan.core.conversation import Conversation


class ConversationItem(QWidget):
    """Widget para exibir uma conversa na lista."""

    clicked = Signal(Conversation)

    def __init__(self, conversation: Conversation, parent=None):
        super().__init__(parent)
        self.conversation = conversation
        self.setObjectName("conversationItem")
        self._setup_ui()
        self.setProperty("selected", False)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        # Header with title and time
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        # Title
        title = QLabel(self.conversation.title or "Nova Conversa")
        title.setObjectName("conversationItemTitle")
        title.setWordWrap(True)
        header_layout.addWidget(title, 1)  # Stretch factor 1

        # Time and badge in a container
        info_container = QWidget()
        info_layout = QHBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(8)

        # Time
        updated_at = datetime.fromisoformat(self.conversation.updated_at)
        time = QLabel(updated_at.strftime("%H:%M"))
        time.setObjectName("conversationItemTime")
        info_layout.addWidget(time)

        header_layout.addWidget(info_container)
        layout.addWidget(header)

        # Preview of last message
        if self.conversation.messages:
            last_message = self.conversation.messages[-1]
            preview = QLabel(
                last_message.content[:100] + "..."
                if len(last_message.content) > 100
                else last_message.content
            )
            preview.setObjectName("conversationItemPreview")
            preview.setWordWrap(True)
            preview.setMaximumHeight(36)  # Limit to roughly 2 lines
            layout.addWidget(preview)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.conversation)

    def setSelected(self, selected: bool):
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)


class ConversationList(QWidget):
    """Widget de lista de conversas."""

    conversation_selected = Signal(Conversation)

    def __init__(self, controller: AppController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setObjectName("conversationList")
        self._setup_ui()
        self._setup_signals()

        self.controller.conversation_created.connect(self._add_conversation)
        self.controller.conversation_updated.connect(self._update_conversation)
        self.controller.conversation_deleted.connect(self._remove_conversation)

        self._current_conversation = None

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setObjectName("conversationHeader")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(16, 16, 16, 16)
        header_layout.setSpacing(12)

        # Title and New Button
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)

        title = QLabel("Conversas")
        title.setObjectName("conversationTitle")
        title_layout.addWidget(title)

        title_layout.addStretch()

        new_button = QPushButton()
        new_button.setIcon(QIcon(str(RESOURCES_DIR / "icons" / "plus.svg")))
        new_button.setToolTip("Nova Conversa (Ctrl+N)")
        new_button.setFixedSize(36, 36)
        new_button.setObjectName("newButton")
        new_button.clicked.connect(self.controller.new_conversation)
        title_layout.addWidget(new_button)

        header_layout.addLayout(title_layout)

        # Search
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(8)

        search = QLineEdit()
        search.setObjectName("conversationSearch")
        search.setPlaceholderText("Pesquisar conversas...")
        search.setFixedHeight(40)
        search_layout.addWidget(search)

        header_layout.addLayout(search_layout)

        layout.addWidget(header)

        # Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setObjectName("conversationScroll")

        # Container for conversation items
        self.conversation_container = QWidget()
        self.conversation_container.setObjectName("conversationContainer")
        self.conversation_layout = QVBoxLayout(self.conversation_container)
        self.conversation_layout.setContentsMargins(8, 8, 8, 8)
        self.conversation_layout.setSpacing(2)
        self.conversation_layout.addStretch()

        scroll_area.setWidget(self.conversation_container)
        layout.addWidget(scroll_area)

    def _setup_signals(self):
        self.conversation_selected.connect(self.controller.select_conversation)

    def _add_conversation(self, conversation: Conversation):
        self.conversation_layout.takeAt(self.conversation_layout.count() - 1)
        item = ConversationItem(conversation)
        item.clicked.connect(self._on_conversation_clicked)
        self.conversation_layout.addWidget(item)
        self.conversation_layout.addStretch()

    def _update_conversation(self, conversation: Conversation):
        for i in range(self.conversation_layout.count()):
            item = self.conversation_layout.itemAt(i).widget()
            if (
                isinstance(item, ConversationItem)
                and item.conversation.id == conversation.id
            ):
                item.conversation = conversation
                item.setSelected(
                    conversation.id == self._current_conversation.id
                    if self._current_conversation
                    else False
                )
                break

    def _remove_conversation(self, conversation_id: str):
        for i in range(self.conversation_layout.count()):
            item = self.conversation_layout.itemAt(i).widget()
            if (
                isinstance(item, ConversationItem)
                and item.conversation.id == conversation_id
            ):
                self.conversation_layout.takeAt(i)
                item.deleteLater()
                break

    def _on_conversation_clicked(self, conversation: Conversation):
        self._current_conversation = conversation
        for i in range(self.conversation_layout.count()):
            item = self.conversation_layout.itemAt(i).widget()
            if isinstance(item, ConversationItem):
                item.setSelected(item.conversation.id == conversation.id)
        self.conversation_selected.emit(conversation)
