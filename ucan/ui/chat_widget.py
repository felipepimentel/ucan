"""
Widget de chat da aplicação UCAN.
"""

import asyncio
import logging
import os

import markdown
from PySide6.QtCore import (
    QEasingCurve,
    QPoint,
    QPropertyAnimation,
    QSize,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import (
    QIcon,
    QKeyEvent,
    QTextCursor,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ucan.config.theme_manager import theme_manager
from ucan.models.conversation import Conversation
from ucan.models.message import Message
from ucan.utils.resource_loader import load_icon

logger = logging.getLogger(__name__)


class MessageWidget(QWidget):
    """Widget para exibir uma mensagem."""

    def __init__(self, message: Message, parent=None) -> None:
        """
        Inicializa o widget.

        Args:
            message: Mensagem a ser exibida
            parent: Pai do widget
        """
        super().__init__(parent)
        self.message = message
        self._setup_ui()
        self._setup_animation()
        self.setObjectName(f"message_{message.role}")

    def _setup_ui(self) -> None:
        """Configura a interface do widget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(0)

        # Container principal com sombra e borda arredondada
        container = QWidget(self)
        container.setObjectName("messageContainer")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(16, 12, 16, 12)
        container_layout.setSpacing(8)

        # Cabeçalho com ícone, nome e timestamp
        header = QWidget()
        header.setObjectName("messageHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        # Container para ícone e nome (agrupados)
        role_container = QWidget()
        role_container.setObjectName("roleContainer")
        role_layout = QHBoxLayout(role_container)
        role_layout.setContentsMargins(0, 0, 0, 0)
        role_layout.setSpacing(6)

        # Ícone da role
        role_icon = QLabel()
        role_icon.setObjectName("roleIcon")

        # Usar o utilitário de carregamento de ícones
        role_pixmap = load_icon(self.message.role, size=24, fallback="user")
        role_icon.setPixmap(role_pixmap)

        role_layout.addWidget(role_icon)

        # Nome da role
        role_name = QLabel(self.message.role.capitalize())
        role_name.setObjectName("roleName")
        role_layout.addWidget(role_name)

        header_layout.addWidget(role_container)
        header_layout.addStretch()

        # Container para timestamp e status
        meta_container = QWidget()
        meta_container.setObjectName("metaContainer")
        meta_layout = QHBoxLayout(meta_container)
        meta_layout.setContentsMargins(0, 0, 0, 0)
        meta_layout.setSpacing(6)

        # Timestamp
        timestamp = QLabel(self.message.timestamp.strftime("%H:%M"))
        timestamp.setObjectName("timestampLabel")
        meta_layout.addWidget(timestamp)

        # Ícone de status
        status_icon = QLabel()
        status_icon.setObjectName("statusIcon")

        # Usar o utilitário de carregamento de ícones
        status_pixmap = load_icon("check", size=16, fallback="check-circle")
        status_icon.setPixmap(status_pixmap)

        meta_layout.addWidget(status_icon)

        header_layout.addWidget(meta_container)
        container_layout.addWidget(header)

        # Conteúdo da mensagem
        content = QLabel(markdown.markdown(self.message.content))
        content.setObjectName("messageContent")
        content.setWordWrap(True)
        content.setTextFormat(Qt.RichText)
        content.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )
        content.setOpenExternalLinks(True)
        container_layout.addWidget(content)

        layout.addWidget(container)

    def _setup_animation(self):
        """Configura a animação de fade in."""
        self.setAutoFillBackground(True)
        self.opacity_effect = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_effect.setDuration(200)
        self.opacity_effect.setStartValue(0)
        self.opacity_effect.setEndValue(1)
        self.opacity_effect.setEasingCurve(QEasingCurve.OutCubic)
        self.opacity_effect.start()


class DateSeparator(QWidget):
    """Widget para separar mensagens por data."""

    def __init__(self, date: str, parent=None):
        """
        Inicializa o separador.

        Args:
            date: Data a ser exibida
            parent: Widget pai
        """
        super().__init__(parent)
        self.setObjectName("dateSeparator")
        self._setup_ui(date)

    def _setup_ui(self, date: str) -> None:
        """
        Configura a interface do separador.

        Args:
            date: Data a ser exibida
        """
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        # Linha esquerda
        line_left = QFrame()
        line_left.setFrameShape(QFrame.HLine)
        line_left.setObjectName("separatorLine")
        layout.addWidget(line_left)

        # Label da data
        date_label = QLabel(date)
        date_label.setObjectName("separatorText")
        date_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(date_label)

        # Linha direita
        line_right = QFrame()
        line_right.setFrameShape(QFrame.HLine)
        line_right.setObjectName("separatorLine")
        layout.addWidget(line_right)

        # Configurar proporções
        layout.setStretchFactor(line_left, 1)
        layout.setStretchFactor(date_label, 0)
        layout.setStretchFactor(line_right, 1)


class KnowledgeBaseItem(QWidget):
    """Item que representa uma base de conhecimento na lista."""

    def __init__(self, kb_name, kb_scope, kb_description, parent=None):
        super().__init__(parent)
        self.setObjectName("knowledge-base-item")
        self._setup_ui(kb_name, kb_scope, kb_description)

    def _setup_ui(self, kb_name, kb_scope, kb_description):
        """Configura a UI do item."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Nome da base
        name_label = QLabel(kb_name)
        name_label.setProperty("class", "knowledge-base-name")
        name_label.setWordWrap(True)
        layout.addWidget(name_label)

        # Escopo (se houver)
        if kb_scope:
            scope_label = QLabel(kb_scope)
            scope_label.setProperty("class", "knowledge-base-scope")
            layout.addWidget(scope_label)

        # Descrição
        if kb_description:
            desc_label = QLabel(kb_description)
            desc_label.setProperty("class", "knowledge-base-description")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)


class KnowledgePanel(QWidget):
    """Painel lateral que exibe as bases de conhecimento disponíveis."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Configura a UI do painel de conhecimento."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Cabeçalho do painel
        header_container = QWidget()
        header_container.setObjectName("knowledgeTitleContainer")
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(16, 16, 16, 16)
        header_layout.setSpacing(8)

        # Ícone do cabeçalho
        icon_label = QLabel()
        icon_label.setFixedSize(QSize(24, 24))
        icon_pixmap = load_icon("book-open.svg", fallback="knowledge.svg")
        if icon_pixmap:
            icon_label.setPixmap(
                icon_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        header_layout.addWidget(icon_label)

        # Título do painel
        title_label = QLabel("Bases de Conhecimento")
        title_label.setObjectName("knowledgeTitle")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        # Botão de atualizar
        refresh_button = QPushButton()
        refresh_button.setObjectName("refreshButton")
        refresh_button.setFixedSize(QSize(32, 32))
        refresh_icon = load_icon("refresh-cw.svg", fallback="refresh.svg")
        if refresh_icon:
            refresh_button.setIcon(refresh_icon)
        refresh_button.setToolTip("Atualizar bases de conhecimento")
        refresh_button.clicked.connect(self._refresh_knowledge_bases)
        header_layout.addWidget(refresh_button)

        layout.addWidget(header_container)

        # Descrição do painel
        description = QLabel(
            "Bases de conhecimento disponíveis para enriquecer as respostas."
        )
        description.setObjectName("knowledgePanelDescription")
        description.setWordWrap(True)
        layout.addWidget(description)

        # Container para a lista e estado vazio
        self.content_stack = QStackedWidget()

        # Lista de bases de conhecimento
        list_container = QWidget()
        list_layout = QVBoxLayout(list_container)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(0)

        self.knowledge_list = QListWidget()
        self.knowledge_list.setObjectName("knowledgeList")
        self.knowledge_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.knowledge_list.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.knowledge_list.setFrameShape(QFrame.NoFrame)
        self.knowledge_list.setSelectionMode(QAbstractItemView.NoSelection)
        list_layout.addWidget(self.knowledge_list)

        # Estado vazio
        empty_container = QWidget()
        empty_layout = QVBoxLayout(empty_container)
        empty_layout.setContentsMargins(0, 0, 0, 0)
        empty_layout.setSpacing(16)

        self.empty_label = QLabel("Nenhuma base de conhecimento disponível")
        self.empty_label.setObjectName("emptyKnowledgeLabel")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setWordWrap(True)
        empty_layout.addWidget(self.empty_label)

        # Adiciona os widgets ao stack
        self.content_stack.addWidget(list_container)
        self.content_stack.addWidget(empty_container)
        layout.addWidget(self.content_stack)

        self.setObjectName("knowledgePanel")

    def update_knowledge_list(self, knowledge_bases):
        """Atualiza a lista de bases de conhecimento."""
        self.knowledge_list.clear()

        if not knowledge_bases:
            self.content_stack.setCurrentIndex(1)  # Mostra estado vazio
            return

        self.content_stack.setCurrentIndex(0)  # Mostra lista

        # Adiciona as bases de conhecimento à lista
        for kb in knowledge_bases:
            item = QListWidgetItem(self.knowledge_list)
            widget = KnowledgeBaseItem(
                kb_name=kb.get("name", "Base de Conhecimento"),
                kb_scope=kb.get("scope", ""),
                kb_description=kb.get("description", ""),
            )
            item.setSizeHint(widget.sizeHint())
            self.knowledge_list.addItem(item)
            self.knowledge_list.setItemWidget(item, widget)

    def _refresh_knowledge_bases(self):
        """Atualiza a lista de bases de conhecimento."""
        # Aqui você pode adicionar uma animação de loading se desejar
        if hasattr(self, "parent") and hasattr(self.parent(), "update_knowledge_bases"):
            self.parent().update_knowledge_bases()


class ChatWidget(QWidget):
    """
    Widget principal do chat.
    """

    messageSubmitted = Signal(str)
    triggerScrollToBottom = Signal()

    def __init__(self, controller=None, parent=None):
        """
        Inicializa o widget de chat.

        Args:
            controller: Controlador da aplicação
            parent: Widget pai
        """
        super().__init__(parent)
        self.controller = controller
        self.icons_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "resources",
            "icons",
        )

        # Inicialização de atributos
        self.input_text = None
        self.send_button = None
        self.format_bar = None
        self.messages_area = None
        self.scroll_area = None
        self._setup_ui()
        self._setup_signals()
        self._knowledge_bases = []

    def _setup_ui(self):
        """Configura a interface do widget."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Container principal
        self.main_widget = QWidget()
        self.main_widget.setObjectName("chatWidget")
        main_content_layout = QHBoxLayout(self.main_widget)
        main_content_layout.setContentsMargins(0, 0, 0, 0)
        main_content_layout.setSpacing(0)

        # Container para o conteúdo do chat
        self.chat_content = QWidget()
        chat_layout = QVBoxLayout(self.chat_content)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)

        # Cabeçalho com informações do chat
        self.header = QWidget()
        self.header.setObjectName("chatHeader")
        header_layout = QVBoxLayout(self.header)
        header_layout.setContentsMargins(20, 16, 20, 16)

        self.chat_title = QLabel("Novo Chat")
        self.chat_title.setObjectName("chatTitle")

        self.chat_subtitle = QLabel("Faça uma pergunta ou escolha um tema sugerido")
        self.chat_subtitle.setObjectName("chatSubtitle")

        header_layout.addWidget(self.chat_title)
        header_layout.addWidget(self.chat_subtitle)

        chat_layout.addWidget(self.header)

        # Área das mensagens com rolagem
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("chatScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.message_widget = QWidget()
        self.message_widget.setObjectName("messageScroll")

        self.message_layout = QVBoxLayout(self.message_widget)
        self.message_layout.setContentsMargins(10, 10, 10, 10)
        self.message_layout.setSpacing(10)
        self.message_layout.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.message_widget)
        chat_layout.addWidget(self.scroll_area)

        # Estado vazio (inicial)
        self.empty_state = QWidget()
        self.empty_state.setVisible(True)
        self._setup_empty_state()

        # Widget empilhado para alternar entre estado vazio e chat
        self.message_stack = QStackedWidget()
        self.message_stack.addWidget(self.empty_state)
        self.message_stack.addWidget(self.scroll_area)
        chat_layout.addWidget(self.message_stack)

        # Container de entrada de mensagem
        self.input_container = QWidget()
        self.input_container.setObjectName("inputContainer")
        input_layout = QVBoxLayout(self.input_container)
        input_layout.setContentsMargins(20, 16, 20, 16)

        # Barra de formatação
        self.format_bar = QWidget()
        self.format_bar.setObjectName("formatBar")
        format_layout = QHBoxLayout(self.format_bar)
        format_layout.setContentsMargins(10, 4, 10, 4)
        format_layout.setSpacing(8)

        # Botões de formatação com ícones
        self.bold_button = QPushButton()
        self.bold_button.setObjectName("boldButton")
        bold_icon = load_icon("bold.svg", size=18, fallback="format_bold.svg")
        if bold_icon:
            self.bold_button.setIcon(bold_icon)
        self.bold_button.setFixedSize(32, 32)
        self.bold_button.setToolTip("Negrito (Ctrl+B)")
        self.bold_button.clicked.connect(lambda: self._handle_format_click("bold"))
        format_layout.addWidget(self.bold_button)

        self.italic_button = QPushButton()
        self.italic_button.setObjectName("italicButton")
        italic_icon = load_icon("italic.svg", size=18, fallback="format_italic.svg")
        if italic_icon:
            self.italic_button.setIcon(italic_icon)
        self.italic_button.setFixedSize(32, 32)
        self.italic_button.setToolTip("Itálico (Ctrl+I)")
        self.italic_button.clicked.connect(lambda: self._handle_format_click("italic"))
        format_layout.addWidget(self.italic_button)

        self.code_button = QPushButton()
        self.code_button.setObjectName("codeButton")
        code_icon = load_icon("code.svg", size=18, fallback="format_code.svg")
        if code_icon:
            self.code_button.setIcon(code_icon)
        self.code_button.setFixedSize(32, 32)
        self.code_button.setToolTip("Código (Ctrl+K)")
        self.code_button.clicked.connect(lambda: self._handle_format_click("code"))
        format_layout.addWidget(self.code_button)

        # Adicionar botão de link
        self.link_button = QPushButton()
        self.link_button.setObjectName("linkButton")
        link_icon = load_icon("link.svg", size=18, fallback="format_link.svg")
        if link_icon:
            self.link_button.setIcon(link_icon)
        self.link_button.setFixedSize(32, 32)
        self.link_button.setToolTip("Link (Ctrl+L)")
        self.link_button.clicked.connect(lambda: self._handle_format_click("link"))
        format_layout.addWidget(self.link_button)

        # Armazenar referências aos botões para uso posterior
        self.format_buttons = {
            "bold": self.bold_button,
            "italic": self.italic_button,
            "code": self.code_button,
            "link": self.link_button,
        }

        format_layout.addStretch()

        # Entrada de texto
        self.input_text = QTextEdit()
        self.input_text.setObjectName("inputText")
        self.input_text.setPlaceholderText("Digite uma mensagem...")
        self.input_text.setAcceptRichText(False)
        self.input_text.setTabChangesFocus(True)
        self.input_text.setMinimumHeight(36)
        self.input_text.setMaximumHeight(120)

        # Container para botão e contador
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)

        # Contador de caracteres
        self.char_counter = QLabel("0/2000")
        self.char_counter.setObjectName("charCounter")
        button_layout.addWidget(self.char_counter)

        button_layout.addStretch()

        # Botão de enviar
        self.send_button = QPushButton("Enviar")
        self.send_button.setObjectName("sendButton")
        self.send_button.setEnabled(False)
        button_layout.addWidget(self.send_button)

        # Adiciona os widgets ao layout de entrada
        input_layout.addWidget(self.format_bar)
        input_layout.addWidget(self.input_text)
        input_layout.addWidget(button_container)

        chat_layout.addWidget(self.input_container)

        # Painel de conhecimento
        self.knowledge_panel = KnowledgePanel()

        # Splitter para redimensionar os painéis
        self.splitter = QSplitter()
        self.splitter.addWidget(self.chat_content)
        self.splitter.addWidget(self.knowledge_panel)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([700, 300])

        main_content_layout.addWidget(self.splitter)
        main_layout.addWidget(self.main_widget)

        self.setObjectName("chat_widget")

    def _setup_signals(self):
        """Set up signal connections."""
        self.input_text.textChanged.connect(self._on_text_changed)
        self.send_button.clicked.connect(self.on_send_clicked)
        theme_manager.theme_changed.connect(self._apply_theme)

        # Connect controller signals if controller exists
        if self.controller:
            self.messageSubmitted.connect(self.controller.send_message)
            self.controller.message_received.connect(self._add_message)

    def add_user_message(self, content: str) -> None:
        """
        Adiciona uma mensagem do usuário à interface.

        Args:
            content: Conteúdo da mensagem
        """
        # Passa para o método genérico de adicionar mensagem
        # Normalmente isso seria feito pelo controlador
        if not hasattr(self, "_last_message_date"):
            self._last_message_date = ""

        # Cria uma mensagem temporária
        from datetime import datetime

        from ucan.models.message import Message

        message = Message(role="user", content=content, timestamp=datetime.now())
        self._add_message(message)

    def add_error_message(self, content: str) -> None:
        """
        Adiciona uma mensagem de erro à interface.

        Args:
            content: Conteúdo da mensagem de erro
        """
        if not hasattr(self, "_last_message_date"):
            self._last_message_date = ""

        # Cria uma mensagem temporária
        from datetime import datetime

        from ucan.models.message import Message

        message = Message(
            role="system", content=f"Erro: {content}", timestamp=datetime.now()
        )
        self._add_message(message)

    def clear_input(self) -> None:
        """Limpa o campo de entrada de texto."""
        self.input_text.clear()

    def _on_text_changed(self):
        """Manipula mudanças no texto de entrada."""
        text = self.input_text.toPlainText()
        char_count = len(text)
        max_chars = 2000
        remaining = max_chars - char_count

        self.char_counter.setText(f"{char_count}/{max_chars}")
        self.char_counter.setProperty("warning", remaining < 100)
        self.char_counter.style().unpolish(self.char_counter)
        self.char_counter.style().polish(self.char_counter)

        self.send_button.setEnabled(0 < char_count <= max_chars)

    def _add_message(self, message: Message) -> None:
        """
        Adiciona uma mensagem ao chat.

        Args:
            message: Mensagem a ser adicionada
        """
        # Verificar se estamos no modo estado vazio
        if (
            hasattr(self, "empty_state_widget")
            and self.scroll_area.widget() == self.empty_state_widget
        ):
            # Substituir o widget vazio pelo container de mensagens
            self.scroll_area.setWidget(self.message_widget)

        # Remove the stretch at the end
        stretch_item = self.message_layout.takeAt(self.message_layout.count() - 1)
        if stretch_item:
            stretch_item.widget().deleteLater() if stretch_item.widget() else None

        message_date = message.timestamp.strftime("%Y-%m-%d")
        if self._last_message_date != message_date:
            separator = DateSeparator(message.timestamp.strftime("%d de %B de %Y"))
            self.message_layout.addWidget(separator)
            self._last_message_date = message_date

        message_widget = MessageWidget(message)
        self.message_layout.addWidget(message_widget)

        # Adiciona o stretch novamente
        self.message_layout.addStretch()

        # Rolagem animada para a parte inferior
        QTimer.singleShot(100, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        """Scroll to the bottom of the message area."""
        if self.scroll_area and self.scroll_area.verticalScrollBar():
            QTimer.singleShot(
                50,
                lambda: self.scroll_area.verticalScrollBar().setValue(
                    self.scroll_area.verticalScrollBar().maximum()
                ),
            )

    async def send_message(self, content: str) -> None:
        """
        Envia uma mensagem para o controlador.

        Args:
            content: Conteúdo da mensagem
        """
        if not content.strip():
            return

        # Adiciona a mensagem à interface
        self.add_user_message(content)
        self.clear_input()

        # Envia a mensagem para o controlador
        try:
            await self.controller.send_message(content)
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
            self.add_error_message(str(e))

    def on_send_clicked(self) -> None:
        """Manipula o clique no botão de enviar."""
        content = self.input_text.toPlainText().strip()
        if content:
            # Usa asyncio.create_task para executar a corotina
            asyncio.create_task(self.send_message(content))

    def on_return_pressed(self) -> None:
        """Manipula o pressionamento da tecla Enter."""
        if not (QApplication.keyboardModifiers() & Qt.ShiftModifier):
            content = self.input_text.toPlainText().strip()
            if content:
                # Usa asyncio.create_task para executar a corotina
                asyncio.create_task(self.send_message(content))
                return
        super().keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_Return, Qt.NoModifier))

    def _send_message(self) -> None:
        """Envia a mensagem atual."""
        content = self.input_text.toPlainText().strip()
        if not content or len(content) > 2000:
            return

        self.input_text.clear()
        self.message_submitted.emit(content)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle key press events."""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            key = event.key()
            if key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
                self._send_message()
                return
            elif key == Qt.Key.Key_B:
                self._toggle_format("bold")
                return
            elif key == Qt.Key.Key_I:
                self._toggle_format("italic")
                return
            elif key == Qt.Key.Key_K:
                self._toggle_format("code")
                return
            elif key == Qt.Key.Key_L:
                self._toggle_format("link")
                return
            elif key == Qt.Key.Key_P:
                self.preview_button.click()
                return
        super().keyPressEvent(event)

    def _toggle_format(self, format_type: str) -> None:
        """Toggle formatting for selected text."""
        button = self.format_buttons[format_type]
        button.animateClick()  # Provides visual feedback
        cursor = self.input_text.textCursor()

        if not cursor.hasSelection():
            return

        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        text = cursor.selectedText()

        if format_type == "bold":
            new_text = f"**{text}**" if not text.startswith("**") else text[2:-2]
        elif format_type == "italic":
            new_text = f"*{text}*" if not text.startswith("*") else text[1:-1]
        elif format_type == "code":
            new_text = f"`{text}`" if not text.startswith("`") else text[1:-1]
        elif format_type == "link":
            if text.startswith("["):
                new_text = text[1:-1].split("](")[0]
            else:
                new_text = f"[{text}]()"
                # Move cursor inside parentheses
                end += 3

        cursor.insertText(new_text)
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        self.input_text.setTextCursor(cursor)

        if format_type == "link" and not text.startswith("["):
            cursor.setPosition(end - 1)
            self.input_text.setTextCursor(cursor)

    def _toggle_preview(self):
        """Alterna entre o modo de edição e preview do texto."""
        if not hasattr(self, "_preview_mode"):
            self._preview_mode = False

        self._preview_mode = not self._preview_mode
        current_text = self.input_text.toPlainText()

        if self._preview_mode:
            # Converte o texto para HTML usando markdown
            html = markdown.markdown(current_text)
            self.input_text.setHtml(html)
            self.input_text.setReadOnly(True)
        else:
            self.input_text.setPlainText(current_text)
            self.input_text.setReadOnly(False)

        # Atualiza o estado do botão
        preview_button = self.findChild(QPushButton, "previewButton")
        if preview_button:
            preview_button.setChecked(self._preview_mode)

    def _handle_format_click(self, format_type):
        """Aplica a formatação selecionada ao texto.

        Args:
            format_type (str): Tipo de formatação (bold, italic, code, link).
        """
        cursor = self.input_text.textCursor()
        selected_text = cursor.selectedText()

        if format_type == "bold":
            formatted_text = (
                f"**{selected_text}**" if selected_text else "**texto em negrito**"
            )
        elif format_type == "italic":
            formatted_text = (
                f"*{selected_text}*" if selected_text else "*texto em itálico*"
            )
        elif format_type == "code":
            formatted_text = f"`{selected_text}`" if selected_text else "`código`"
        elif format_type == "link":
            formatted_text = (
                f"[{selected_text}](url)" if selected_text else "[texto do link](url)"
            )
        else:
            return

        # Se não houver texto selecionado, seleciona o texto padrão inserido
        cursor.insertText(formatted_text)
        if not selected_text:
            new_position = cursor.position()
            cursor.setPosition(new_position - len(formatted_text))
            cursor.setPosition(new_position, Qt.KeepAnchor)
            self.input_text.setTextCursor(cursor)

        self.input_text.setFocus()

    def _update_format_buttons(self):
        """Atualiza o estado dos botões de formatação baseado no texto selecionado."""
        cursor = self.input_text.textCursor()
        text = cursor.selectedText()

        # Verifica se o texto selecionado está dentro de marcações Markdown
        for format_type, button in self.format_buttons.items():
            if format_type == "bold":
                is_formatted = text.startswith("**") and text.endswith("**")
            elif format_type == "italic":
                is_formatted = text.startswith("*") and text.endswith("*")
            elif format_type == "code":
                is_formatted = text.startswith("`") and text.endswith("`")
            elif format_type == "link":
                is_formatted = (
                    text.startswith("[") and "](" in text and text.endswith(")")
                )
            else:
                is_formatted = False

            button.setChecked(is_formatted)

    def set_conversation(self, conversation: Conversation) -> None:
        """Define a conversa atual."""
        self.current_conversation = conversation

        # Verificar se o layout ainda existe antes de tentar manipulá-lo
        try:
            # Clear existing messages
            while self.message_layout and self.message_layout.count():
                item = self.message_layout.takeAt(0)
                if item and item.widget():
                    item.widget().deleteLater()

            # Add new messages
            if conversation:
                messages = conversation.get_messages()
                for message in messages:
                    self._add_message(message)
        except RuntimeError:
            # O layout pode ter sido excluído pelo Qt
            pass

        self.update_title()
        self.update_knowledge_bases()

    def update_title(self) -> None:
        """Atualiza o título do chat."""
        if self.current_conversation:
            self.chat_title.setText(self.current_conversation.title)
        else:
            self.chat_title.setText("Novo Chat")

    def update_knowledge_bases(self) -> None:
        """Atualiza a lista de bases de conhecimento."""
        if self.current_conversation:
            self._knowledge_bases = self.current_conversation.get_knowledge_bases()
        else:
            self._knowledge_bases = []

        self.knowledge_panel.update_knowledge_list(self._knowledge_bases)

    def _apply_theme(self):
        """
        Atualiza os estilos deste widget quando o tema muda ou
        há um hot reload de CSS.
        """
        try:
            # Importação de estilos
            from ucan.ui.styles import style_manager

            # Aplicar estilos básicos para todo o widget
            basic_styles = """
                QWidget#chatWidget {
                    background-color: #1a1b26;
                    color: #a9b1d6;
                }
                
                #chatHeader {
                    background-color: #20232D;
                    border-bottom: 1px solid #2F3241;
                    padding: 10px 16px;
                }
                
                #chatTitle {
                    color: #E4E6EB;
                    font-size: 20px;
                    font-weight: 700;
                }
                
                #chatSubtitle {
                    color: #9EA0A5;
                    font-size: 13px;
                }
                
                /* Input Text */
                QTextEdit#messageInput {
                    background-color: #1f2335;
                    color: #c0caf5;
                    border: 1px solid #32344a;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 14px;
                    min-height: 36px;
                    max-height: 120px;
                }

                /* Send Button */
                QPushButton#sendButton {
                    background-color: #7aa2f7;
                    color: #1a1b26;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 600;
                    min-width: 100px;
                }
                
                QPushButton#sendButton:hover {
                    background-color: #89b4fa;
                }
                
                QPushButton#sendButton:disabled {
                    background-color: #414868;
                    color: #565f89;
                }
            """
            self.setStyleSheet(basic_styles)

            # Aplicar estilos específicos ao estado vazio se existir
            if hasattr(self, "empty_state_widget"):
                empty_state_styles = style_manager.get_empty_state_stylesheet()
                self.empty_state_widget.setStyleSheet(empty_state_styles)

            # Estilos específicos para os componentes de entrada
            if hasattr(self, "input_text"):
                self.input_text.setStyleSheet("""
                    QTextEdit {
                        background-color: #1f2335;
                        color: #c0caf5;
                        border: 1px solid #32344a;
                        border-radius: 8px;
                        padding: 8px 12px;
                        font-size: 14px;
                    }
                    
                    QTextEdit:focus {
                        border-color: #7aa2f7;
                    }
                """)

            if hasattr(self, "send_button"):
                self.send_button.setStyleSheet("""
                    QPushButton {
                        background-color: #7aa2f7;
                        color: #1a1b26;
                        border: none;
                        border-radius: 6px;
                        padding: 8px 16px;
                        font-weight: 600;
                    }
                    
                    QPushButton:hover {
                        background-color: #89b4fa;
                    }
                    
                    QPushButton:disabled {
                        background-color: #414868;
                        color: #565f89;
                    }
                """)

        except Exception as e:
            logger.error(f"Erro ao aplicar tema: {e}")
            # Se falhar, aplicar estilos mínimos
            self.setStyleSheet("")

    def _setup_empty_state(self):
        self.empty_state = QWidget()
        self.empty_state.setObjectName("emptyState")

        # Layout for empty state
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 30, 20, 30)
        layout.setSpacing(16)
        self.empty_state.setLayout(layout)

        # Panel for content
        panel = QWidget()
        panel.setObjectName("emptyStatePanel")
        panel_layout = QVBoxLayout()
        panel_layout.setContentsMargins(30, 40, 30, 40)
        panel_layout.setSpacing(20)
        panel.setLayout(panel_layout)

        # Icon
        icon_label = QLabel()
        icon_label.setObjectName("emptyStateIcon")
        icon_size = QSize(80, 80)

        # Try to load chat icon first, fallback to message icon if not available
        icon_path = os.path.join(self.icons_dir, "chat.svg")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(self.icons_dir, "message-circle.svg")

        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            pixmap = icon.pixmap(icon_size)
            icon_label.setPixmap(pixmap)
        else:
            # If no icon is available, create a text-based placeholder
            icon_label.setText("💬")
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setStyleSheet("font-size: 60px;")

        icon_label.setAlignment(Qt.AlignCenter)

        # Setup icon float animation
        self.icon_animation = QPropertyAnimation(icon_label, b"pos")
        self.icon_animation.setDuration(3000)
        self.icon_animation.setStartValue(QPoint(0, 0))
        self.icon_animation.setEndValue(QPoint(0, 10))
        self.icon_animation.setEasingCurve(QEasingCurve.InOutSine)
        self.icon_animation.setLoopCount(-1)  # Infinite loop

        # Add direction change
        self.icon_animation.finished.connect(self._reverse_animation)

        # Welcome text
        text_label = QLabel("Bem-vindo ao UCAN")
        text_label.setObjectName("emptyStateText")
        text_label.setAlignment(Qt.AlignCenter)

        # Subtext
        subtext_label = QLabel(
            "Faça perguntas sobre qualquer assunto e receba respostas instantâneas"
        )
        subtext_label.setObjectName("emptyStateSubtext")
        subtext_label.setAlignment(Qt.AlignCenter)
        subtext_label.setWordWrap(True)

        # Suggestions title
        suggestions_title = QLabel("Experimente perguntar sobre:")
        suggestions_title.setObjectName("suggestionsTitle")
        suggestions_title.setAlignment(Qt.AlignCenter)

        # Suggestions container
        suggestions_container = QWidget()
        suggestions_container.setObjectName("suggestionsContainer")
        suggestions_layout = QVBoxLayout()
        suggestions_layout.setContentsMargins(15, 15, 15, 15)
        suggestions_layout.setSpacing(10)
        suggestions_container.setLayout(suggestions_layout)

        # Add suggestion cards
        common_questions = [
            "Como posso aprender programação?",
            "Explique o que é inteligência artificial",
            "O que são redes neurais?",
            "Quais são as melhores práticas de segurança cibernética?",
            "Como funciona a blockchain?",
        ]

        import random

        random.shuffle(common_questions)
        selected_questions = common_questions[:3]  # Show only 3 random questions

        for question in selected_questions:
            self._create_suggestion_card(suggestions_layout, question)

        # More suggestions button
        more_button = QPushButton("Sugerir mais tópicos")
        more_button.setObjectName("suggestionButton")
        more_button.setCursor(Qt.PointingHandCursor)
        more_button.clicked.connect(self._suggest_more_topics)

        # Add all elements to layouts
        panel_layout.addWidget(icon_label, 0, Qt.AlignCenter)
        panel_layout.addWidget(text_label, 0, Qt.AlignCenter)
        panel_layout.addWidget(subtext_label, 0, Qt.AlignCenter)
        panel_layout.addWidget(suggestions_title, 0, Qt.AlignCenter)
        panel_layout.addWidget(suggestions_container)
        panel_layout.addWidget(more_button, 0, Qt.AlignCenter)

        layout.addWidget(panel, 0, Qt.AlignCenter)

        # Start animation
        QTimer.singleShot(800, self.icon_animation.start)

    def _reverse_animation(self):
        # Reverse the animation direction
        start = self.icon_animation.startValue()
        end = self.icon_animation.endValue()
        self.icon_animation.setStartValue(end)
        self.icon_animation.setEndValue(start)
        self.icon_animation.start()

    def _create_suggestion_card(self, layout, question_text):
        card = QPushButton(question_text)
        card.setObjectName("suggestionCard")
        card.setCursor(Qt.PointingHandCursor)
        card.clicked.connect(lambda: self._use_suggestion(question_text))
        layout.addWidget(card)

    def _use_suggestion(self, text):
        # Set the suggested text to the input field
        self.input_text.setPlainText(text)
        self.input_text.setFocus()

        # Position cursor at the end of the text
        cursor = self.input_text.textCursor()
        cursor.movePosition(cursor.End)
        self.input_text.setTextCursor(cursor)

    def _suggest_more_topics(self):
        # Generate new random suggestions
        topics = [
            "Como funciona o aprendizado de máquina?",
            "O que é programação orientada a objetos?",
            "Explique a diferença entre HTTP e HTTPS",
            "O que é cloud computing?",
            "Como funciona o reconhecimento facial?",
            "O que é um algoritmo?",
            "Como a internet funciona?",
            "O que são cookies em websites?",
            "Quais são as linguagens de programação mais populares?",
            "Como proteger meus dados pessoais online?",
        ]

        # Get the suggestions container
        parent = self.sender().parent()
        suggestions_container = None
        for i in range(parent.layout().count()):
            item = parent.layout().itemAt(i).widget()
            if item and item.objectName() == "suggestionsContainer":
                suggestions_container = item
                break

        if suggestions_container:
            # Clear existing suggestions
            while suggestions_container.layout().count():
                item = suggestions_container.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            # Add new random suggestions
            import random

            random.shuffle(topics)
            selected_topics = topics[:3]

            for topic in selected_topics:
                self._create_suggestion_card(suggestions_container.layout(), topic)
