"""
Widget para exibição da lista de conversas.
"""

from typing import List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QVBoxLayout,
    QWidget,
)

from ucan.core.conversation import Conversation
from ucan.core.conversation_type import ConversationType


class ConversationListWidget(QWidget):
    """Widget para exibição da lista de conversas."""

    conversation_selected = Signal(Conversation)
    new_conversation_requested = Signal(Optional[str])

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Inicializa o widget.

        Args:
            parent: Widget pai (opcional)
        """
        super().__init__(parent)
        self._setup_ui()
        self._conversation_types: List[ConversationType] = []
        self._conversations: List[Conversation] = []

    def _setup_ui(self):
        """Configura a interface do usuário."""
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(15)
        self.setLayout(layout)

        # Título da seção
        header = QLabel("Conversas")
        header.setObjectName("conversationsHeader")
        header.setAlignment(Qt.AlignLeft)
        layout.addWidget(header)

        # Seletor de tipo
        type_layout = QHBoxLayout()
        type_layout.setContentsMargins(0, 0, 0, 0)
        type_layout.setSpacing(10)

        type_label = QLabel("Tipo:")
        type_label.setObjectName("typeLabel")
        type_layout.addWidget(type_label)

        self.type_combo = QComboBox()
        self.type_combo.setObjectName("typeComboBox")
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        type_layout.addWidget(self.type_combo, 1)

        layout.addLayout(type_layout)

        # Caixa de pesquisa
        self.search_box = QLineEdit()
        self.search_box.setObjectName("searchBox")
        self.search_box.setPlaceholderText("Buscar conversas...")
        self.search_box.setClearButtonEnabled(True)
        layout.addWidget(self.search_box)

        # Lista de conversas
        self.conversation_list = QListWidget()
        self.conversation_list.setObjectName("conversationsList")
        self.conversation_list.setFrameShape(QListWidget.NoFrame)
        self.conversation_list.itemClicked.connect(self._on_conversation_selected)
        self.conversation_list.setAlternatingRowColors(True)
        self.conversation_list.setSelectionMode(QListWidget.SingleSelection)
        layout.addWidget(self.conversation_list, 1)

    def set_conversations(self, conversations: List[Conversation]):
        """
        Atualiza a lista de conversas.

        Args:
            conversations: Lista de conversas
        """
        self._conversations = conversations
        self._update_conversation_list()

    def set_conversation_types(self, types: List[ConversationType]):
        """
        Atualiza a lista de tipos de conversa.

        Args:
            types: Lista de tipos de conversa
        """
        self._conversation_types = types
        self.type_combo.clear()
        self.type_combo.addItem("Todos")
        for type_ in types:
            self.type_combo.addItem(type_.name, type_.id)

    def _update_conversation_list(self):
        """Atualiza a lista de conversas com base no filtro de tipo."""
        self.conversation_list.clear()
        type_id = (
            self.type_combo.currentData()
            if self.type_combo.currentIndex() > 0
            else None
        )

        for conversation in self._conversations:
            if type_id is None or conversation.type_id == type_id:
                item = QListWidgetItem()
                item.setData(Qt.UserRole, conversation)
                self._update_conversation_item(item)
                self.conversation_list.addItem(item)

    def _update_conversation_item(self, item: QListWidgetItem):
        """
        Atualiza a exibição de um item da lista.

        Args:
            item: Item a ser atualizado
        """
        conversation = item.data(Qt.UserRole)
        type_name = "Sem tipo"

        if conversation.type_id:
            for type_ in self._conversation_types:
                if type_.id == conversation.type_id:
                    type_name = type_.name
                    break

        item.setText(f"{conversation.title} ({type_name})")

    def _on_conversation_selected(self, item: QListWidgetItem):
        """
        Manipula a seleção de uma conversa na lista.

        Args:
            item: Item selecionado
        """
        conversation = item.data(Qt.UserRole)
        self.conversation_selected.emit(conversation)

    def _on_new_conversation(self):
        """Manipula a criação de uma nova conversa."""
        type_id = None
        if self.type_combo.currentIndex() > 0:
            type_id = self.type_combo.currentData()
        self.new_conversation_requested.emit(type_id)

    def _on_type_changed(self, index: int):
        """
        Manipula a mudança de tipo selecionado.

        Args:
            index: Índice do tipo selecionado
        """
        self._update_conversation_list()

    def contextMenuEvent(self, event):
        """
        Manipula o evento de menu de contexto.

        Args:
            event: O evento de menu de contexto.
        """
        index = self.conversation_list.indexAt(event.pos())
        if index.isValid():
            conversation_id = index.data(Qt.UserRole)
            menu = QMenu(self)
            menu.addAction("Apagar", lambda: self._delete_conversation(conversation_id))
            menu.exec(event.globalPos())

    def _apply_theme(self):
        """
        Atualiza os estilos deste widget quando o tema muda ou
        há um hot reload de CSS.
        """
        from ucan.ui.theme_manager import theme_manager

        theme = theme_manager.current_theme
        if theme:
            self.setStyleSheet(theme.generate_stylesheet())

            # Atualiza também os componentes filhos importantes
            self.conversation_list.setStyleSheet(theme.generate_stylesheet())
            self.search_box.setStyleSheet(theme.generate_stylesheet())
