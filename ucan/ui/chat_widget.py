"""
Widget de chat da aplicação UCAN.
"""

import asyncio
import logging
from typing import List, Optional

import markdown
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QSize, Qt, Signal
from PySide6.QtGui import QFont, QIcon, QKeyEvent, QPixmap, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ucan.config.constants import RESOURCES_DIR
from ucan.core.app_controller import AppController
from ucan.core.conversation import Conversation
from ucan.core.knowledge_base import KnowledgeBase
from ucan.core.message import Message
from ucan.ui.theme_manager import theme_manager

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
        role_icon.setPixmap(
            QPixmap(str(RESOURCES_DIR / "icons" / f"{self.message.role}.svg")).scaled(
                24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
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
        status_icon.setPixmap(
            QPixmap(str(RESOURCES_DIR / "icons" / "check.svg")).scaled(
                16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
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
    """Widget para exibir uma base de conhecimento."""

    def __init__(self, base: KnowledgeBase, parent=None):
        """
        Inicializa o widget.

        Args:
            base: Base de conhecimento
            parent: Widget pai
        """
        super().__init__(parent)
        self.base = base
        self._setup_ui()

    def _setup_ui(self):
        """Configura a interface do widget."""
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        self.setLayout(layout)

        # Container principal
        container = QWidget()
        container.setObjectName("knowledgeBaseContainer")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(8, 8, 8, 8)

        # Nome e escopo
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        name_label = QLabel(self.base.name)
        name_label.setObjectName("knowledgeBaseName")
        header_layout.addWidget(name_label)

        scope_label = QLabel(f"({self.base.scope})")
        scope_label.setObjectName("knowledgeBaseScope")
        header_layout.addWidget(scope_label)

        header_layout.addStretch()
        container_layout.addWidget(header)

        # Descrição
        if self.base.description:
            description = QLabel(self.base.description)
            description.setObjectName("knowledgeBaseDescription")
            description.setWordWrap(True)
            container_layout.addWidget(description)

        layout.addWidget(container)


class ChatWidget(QWidget):
    """Widget de chat."""

    message_received = Signal(Message)
    message_sent = Signal(str)

    def __init__(
        self, controller: AppController, parent: Optional[QWidget] = None
    ) -> None:
        """
        Inicializa o widget.

        Args:
            controller: Controlador da aplicação
            parent: Pai do widget
        """
        super().__init__(parent)
        self.controller = controller
        self.setObjectName("chatWidget")
        self._setup_ui()
        self._setup_signals()
        self._last_message_date = None
        self._current_conversation: Optional[Conversation] = None
        self._knowledge_bases: List[KnowledgeBase] = []
        self._apply_theme()

        # Conectar sinais
        self.controller.message_received.connect(self._add_message)
        self.message_sent.connect(self.controller.send_message)
        theme_manager.theme_changed.connect(self._apply_theme)

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setObjectName("chatHeader")
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(20, 15, 20, 15)
        header_layout.setSpacing(5)
        header.setLayout(header_layout)

        # Title with icon
        title_container = QWidget()
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(10)
        title_container.setLayout(title_layout)

        title_icon = QLabel()
        title_icon.setPixmap(
            QPixmap(str(RESOURCES_DIR / "icons" / "chat.svg")).scaled(
                32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
        title_layout.addWidget(title_icon)

        self.title_label = QLabel("Nova Conversa")
        self.title_label.setObjectName("chatTitle")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()

        header_layout.addWidget(title_container)

        # Subtitle
        self.subtitle_label = QLabel("Inicie uma nova conversa")
        self.subtitle_label.setObjectName("chatSubtitle")
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        self.subtitle_label.setFont(subtitle_font)
        header_layout.addWidget(self.subtitle_label)

        layout.addWidget(header)

        # Main content area with splitter
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Messages area
        messages_widget = QWidget()
        messages_layout = QVBoxLayout(messages_widget)
        messages_layout.setContentsMargins(0, 0, 0, 0)
        messages_layout.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setObjectName("chatScrollArea")

        self.message_container = QWidget()
        self.message_container.setObjectName("messageContainer")
        self.message_layout = QVBoxLayout(self.message_container)
        self.message_layout.addStretch()

        self.scroll_area.setWidget(self.message_container)
        messages_layout.addWidget(self.scroll_area)

        # Input area with modern design
        input_container = QWidget()
        input_container.setObjectName("inputContainer")
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(20, 15, 20, 15)
        input_layout.setSpacing(10)

        # Format bar
        format_bar = QWidget()
        format_bar.setObjectName("formatBar")
        format_layout = QHBoxLayout(format_bar)
        format_layout.setContentsMargins(0, 0, 0, 0)
        format_layout.setSpacing(8)

        # Format buttons
        format_buttons = [
            ("bold", "Negrito (Ctrl+B)"),
            ("italic", "Itálico (Ctrl+I)"),
            ("code", "Código (Ctrl+K)"),
            ("link", "Link (Ctrl+L)"),
        ]

        self.format_buttons = {}
        for btn_id, tooltip in format_buttons:
            button = QPushButton()
            button.setObjectName(f"formatButton_{btn_id}")
            button.setIcon(QIcon(str(RESOURCES_DIR / "icons" / f"{btn_id}.svg")))
            button.setIconSize(QSize(16, 16))
            button.setToolTip(tooltip)
            button.setCheckable(True)
            button.clicked.connect(
                lambda checked, b=btn_id: self._handle_format_click(b)
            )
            format_layout.addWidget(button)
            self.format_buttons[btn_id] = button

        format_layout.addStretch()

        # Preview button
        self.preview_button = QPushButton()
        self.preview_button.setObjectName("previewButton")
        self.preview_button.setIcon(QIcon(str(RESOURCES_DIR / "icons" / "preview.svg")))
        self.preview_button.setIconSize(QSize(16, 16))
        self.preview_button.setToolTip("Visualizar (Ctrl+P)")
        self.preview_button.setCheckable(True)
        self.preview_button.clicked.connect(self._toggle_preview)
        format_layout.addWidget(self.preview_button)

        input_layout.addWidget(format_bar)

        # Message input with send button
        input_row = QWidget()
        input_row_layout = QHBoxLayout(input_row)
        input_row_layout.setContentsMargins(0, 0, 0, 0)
        input_row_layout.setSpacing(10)

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Digite sua mensagem...")
        self.input_text.setMinimumHeight(50)
        self.input_text.setMaximumHeight(100)
        self.input_text.setObjectName("messageInput")
        input_row_layout.addWidget(self.input_text)

        # Character counter
        self.char_counter = QLabel("0/2000")
        self.char_counter.setObjectName("charCounter")
        input_row_layout.addWidget(self.char_counter)

        # Send button
        self.send_button = QPushButton()
        self.send_button.setObjectName("sendButton")
        self.send_button.setIcon(QIcon(str(RESOURCES_DIR / "icons" / "send.svg")))
        self.send_button.setIconSize(QSize(20, 20))
        self.send_button.setFixedSize(40, 40)
        self.send_button.setToolTip("Enviar mensagem (Ctrl+Enter)")
        self.send_button.clicked.connect(self._send_message)
        input_row_layout.addWidget(self.send_button)

        input_layout.addWidget(input_row)

        messages_layout.addWidget(input_container)
        content_layout.addWidget(messages_widget, stretch=7)

        # Knowledge base panel
        knowledge_panel = QWidget()
        knowledge_panel.setObjectName("knowledgePanel")
        knowledge_layout = QVBoxLayout(knowledge_panel)
        knowledge_layout.setContentsMargins(15, 15, 15, 15)
        knowledge_layout.setSpacing(10)

        # Knowledge base header
        kb_header = QWidget()
        kb_header_layout = QHBoxLayout(kb_header)
        kb_header_layout.setContentsMargins(0, 0, 0, 0)
        kb_header_layout.setSpacing(10)

        kb_icon = QLabel()
        kb_icon.setPixmap(
            QPixmap(str(RESOURCES_DIR / "icons" / "book.svg")).scaled(
                24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
        kb_header_layout.addWidget(kb_icon)

        kb_title = QLabel("Bases de Conhecimento")
        kb_title.setObjectName("knowledgeTitle")
        kb_title_font = QFont()
        kb_title_font.setPointSize(14)
        kb_title_font.setBold(True)
        kb_title.setFont(kb_title_font)
        kb_header_layout.addWidget(kb_title)
        kb_header_layout.addStretch()

        knowledge_layout.addWidget(kb_header)

        self.knowledge_list = QListWidget()
        self.knowledge_list.setObjectName("knowledgeList")
        knowledge_layout.addWidget(self.knowledge_list)

        content_layout.addWidget(knowledge_panel, stretch=3)

        layout.addLayout(content_layout)

    def _setup_signals(self):
        """Set up signal connections."""
        self.input_text.textChanged.connect(self._on_text_changed)
        theme_manager.theme_changed.connect(self._apply_theme)

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
        self.message_layout.scrollToBottom()

    def _scroll_to_bottom(self):
        """Scroll the messages area to the bottom with animation."""
        scrollbar = self.message_layout.verticalScrollBar()
        current = scrollbar.value()
        maximum = scrollbar.maximum()

        if current < maximum:
            animation = QPropertyAnimation(scrollbar, b"value", self)
            animation.setDuration(300)
            animation.setStartValue(current)
            animation.setEndValue(maximum)
            animation.setEasingCurve(QEasingCurve.OutCubic)
            animation.start()

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
        self.message_sent.emit(content)

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

        # Clear existing messages
        while self.message_layout.count():
            item = self.message_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add new messages
        if conversation:
            messages = conversation.get_messages()
            for message in messages:
                self._add_message(message)

        self.update_title()
        self.update_knowledge_bases()

    def _update_knowledge_list(self):
        """Atualiza a lista de bases de conhecimento."""
        self.knowledge_list.clear()
        for base in self._knowledge_bases:
            item = QListWidgetItem()
            widget = KnowledgeBaseItem(base)
            item.setSizeHint(widget.sizeHint())
            self.knowledge_list.addItem(item)
            self.knowledge_list.setItemWidget(item, widget)

    def add_message(self, message: Message):
        """
        Adiciona uma mensagem à lista.

        Args:
            message: Mensagem a ser adicionada
        """
        item = QListWidgetItem()
        widget = MessageWidget(message)
        item.setSizeHint(widget.sizeHint())
        self.message_layout.addItem(item)
        self.message_layout.setItemWidget(item, widget)
        self.message_layout.scrollToBottom()

    def update_title(self) -> None:
        """Atualiza o título do chat."""
        if self.current_conversation:
            self.title_label.setText(self.current_conversation.title)
        else:
            self.title_label.setText("")

    def update_knowledge_bases(self) -> None:
        """Atualiza a lista de bases de conhecimento."""
        if self.current_conversation:
            self._knowledge_bases = self.current_conversation.get_knowledge_bases()
        else:
            self._knowledge_bases = []
        self._update_knowledge_list()

    def _apply_theme(self):
        """
        Atualiza os estilos deste widget quando o tema muda ou
        há um hot reload de CSS.
        """
        theme = theme_manager.current_theme
        if theme:
            self.setStyleSheet(theme.generate_stylesheet())

            # Atualiza também os componentes filhos importantes
            self.input_text.setStyleSheet(theme.generate_stylesheet())
