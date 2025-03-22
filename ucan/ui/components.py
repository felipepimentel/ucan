"""
Componentes reutilizáveis para a interface gráfica.
"""

import re
from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import (
    QEasingCurve,
    QEvent,
    QObject,
    QPoint,
    QPropertyAnimation,
    QRect,
    QSize,
    Qt,
    QTime,
    QTimerEvent,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QHideEvent,
    QIcon,
    QKeyEvent,
    QPainter,
    QPaintEvent,
    QShowEvent,
    QTextBlockFormat,
    QTextCharFormat,
    QTextCursor,
    QTextFormat,
)
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStatusBar,
    QTextEdit,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from ucan.config.constants import PRIMARY_COLOR


class MessageBubble(QWidget):
    """Widget para exibir mensagens no chat."""

    def __init__(
        self,
        message: str,
        is_user: bool = False,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Inicializa o widget de mensagem.

        Args:
            message: Conteúdo da mensagem
            is_user: Se True, é uma mensagem do usuário
            parent: Widget pai
        """
        super().__init__(parent)
        self.setObjectName("messageBubble")
        self.is_user = is_user
        self._setup_ui(message)
        self._setup_animation()

    def _setup_ui(self, message: str) -> None:
        """Configura a interface do widget."""
        # Layout principal com margens adequadas
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)

        # Container para a mensagem com estilo apropriado
        container = QWidget()
        container.setObjectName("messageContainer")
        container.setProperty("isUser", self.is_user)
        container.setProperty(
            "class", "user-message" if self.is_user else "assistant-message"
        )

        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(16, 12, 16, 12)
        container_layout.setSpacing(8)

        # Cabeçalho da mensagem
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 4)
        header_layout.setSpacing(8)

        # Ícone do remetente
        icon_label = QLabel()
        icon_label.setFixedSize(24, 24)
        icon = QIcon.fromTheme("user" if self.is_user else "assistant")
        if not icon.isNull():
            icon_label.setPixmap(icon.pixmap(24, 24))
        header_layout.addWidget(icon_label)

        # Nome do remetente
        sender_label = QLabel("Você" if self.is_user else "Assistente")
        sender_label.setObjectName("senderLabel")
        header_layout.addWidget(sender_label)

        # Timestamp
        time_label = QLabel(QTime.currentTime().toString("HH:mm"))
        time_label.setObjectName("timeLabel")
        header_layout.addStretch()
        header_layout.addWidget(time_label)

        container_layout.addWidget(header)

        # Conteúdo da mensagem com suporte a markdown
        content = QTextEdit()
        content.setObjectName("messageContent")
        content.setReadOnly(True)
        content.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        content.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content.setMinimumHeight(40)
        content.setMaximumHeight(400)

        # Configurar formatação markdown
        doc = content.document()
        doc.setDefaultStyleSheet("""
            code { 
                background: rgba(0, 0, 0, 0.2); 
                padding: 2px 4px; 
                border-radius: 4px; 
                font-family: monospace;
            }
            pre {
                background: rgba(0, 0, 0, 0.2);
                padding: 8px;
                border-radius: 8px;
                font-family: monospace;
                white-space: pre-wrap;
            }
            a { color: #7B68EE; }
            p { margin: 0; }
        """)

        # Processar markdown e definir HTML
        html_content = self._process_markdown(message)
        content.setHtml(html_content)

        # Ajustar altura baseado no conteúdo
        doc_height = content.document().size().height()
        content.setFixedHeight(min(max(40, doc_height + 20), 400))

        container_layout.addWidget(content)

        # Botões de ação
        actions = QWidget()
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 4, 0, 0)
        actions_layout.setSpacing(8)

        if not self.is_user:
            # Botão de copiar
            copy_button = QPushButton()
            copy_button.setIcon(QIcon.fromTheme("edit-copy"))
            copy_button.setToolTip("Copiar mensagem")
            copy_button.setObjectName("actionButton")
            copy_button.clicked.connect(lambda: self._copy_message(message))
            actions_layout.addWidget(copy_button)

            # Botão de código
            code_button = QPushButton()
            code_button.setIcon(QIcon.fromTheme("text-x-script"))
            code_button.setToolTip("Extrair código")
            code_button.setObjectName("actionButton")
            code_button.clicked.connect(self._extract_code)
            actions_layout.addWidget(code_button)

        actions_layout.addStretch()
        container_layout.addWidget(actions)

        layout.addWidget(container)

    def _setup_animation(self) -> None:
        """Configura a animação de fade in."""
        self.setAutoFillBackground(True)
        self.opacity_effect = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_effect.setDuration(200)
        self.opacity_effect.setStartValue(0)
        self.opacity_effect.setEndValue(1)
        self.opacity_effect.setEasingCurve(QEasingCurve.OutCubic)
        self.opacity_effect.start()

    def _process_markdown(self, text: str) -> str:
        """
        Processa o texto markdown para HTML.

        Args:
            text: Texto em markdown

        Returns:
            HTML formatado
        """
        # Aqui você pode usar uma biblioteca markdown
        # Por enquanto, vamos fazer um processamento básico
        html = text.replace("\n", "<br>")

        # Código inline
        html = re.sub(r"`([^`]+)`", r"<code>\1</code>", html)

        # Blocos de código
        html = re.sub(r"```([^`]+)```", r"<pre><code>\1</code></pre>", html)

        # Links
        html = re.sub(r"\[([^\]]+)\]\(([^\)]+)\)", r'<a href="\2">\1</a>', html)

        return html

    def _copy_message(self, message: str) -> None:
        """
        Copia a mensagem para a área de transferência.

        Args:
            message: Mensagem a ser copiada
        """
        clipboard = QApplication.clipboard()
        clipboard.setText(message)

        # Feedback visual
        QToolTip.showText(
            self.mapToGlobal(QPoint(0, 0)), "Mensagem copiada!", self, QRect(), 1500
        )

    def _extract_code(self) -> None:
        """Extrai blocos de código da mensagem."""
        content = self.findChild(QTextEdit, "messageContent")
        if not content:
            return

        # Encontrar blocos de código
        doc = content.document()
        cursor = QTextCursor(doc)

        while not cursor.atEnd():
            block = cursor.block()
            if block.text().strip().startswith("```"):
                # Extrair o bloco de código
                start = block.position()
                while not block.text().strip().endswith("```") and block.isValid():
                    block = block.next()
                if block.isValid():
                    end = block.position() + block.length()
                    cursor.setPosition(start)
                    cursor.setPosition(end, QTextCursor.KeepAnchor)
                    code = cursor.selectedText()

                    # Remover marcadores markdown
                    code = code.replace("```", "").strip()

                    # Copiar para a área de transferência
                    clipboard = QApplication.clipboard()
                    clipboard.setText(code)

                    # Feedback visual
                    QToolTip.showText(
                        self.mapToGlobal(QPoint(0, 0)),
                        "Código copiado!",
                        self,
                        QRect(),
                        1500,
                    )
                    return
            cursor.movePosition(QTextCursor.NextBlock)


class ChatInput(QWidget):
    """Campo de entrada para mensagens do chat."""

    message_sent = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Inicializa o campo de entrada do chat.

        Args:
            parent: Widget pai
        """
        super().__init__(parent)
        self.setObjectName("chatInput")
        self.setup_ui()

    def setup_ui(self) -> None:
        """Configura a interface do campo de entrada."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 12)
        layout.setSpacing(8)

        # Container para o campo de texto
        input_container = QWidget()
        input_container.setObjectName("chatInputContainer")
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(8)

        # Área de texto para entrada da mensagem com auto-resize
        self.text_edit = QTextEdit()
        self.text_edit.setObjectName("chatInputField")
        self.text_edit.setPlaceholderText(
            "Digite sua mensagem... (Enter para enviar, Shift+Enter para nova linha)"
        )
        self.text_edit.setMaximumHeight(120)
        self.text_edit.setStyleSheet("""
            #chatInputField {
                background-color: transparent;
                border: none;
                padding: 8px 12px;
                font-size: 15px;
                line-height: 1.5;
                color: #2D3748;
            }
            #chatInputField:focus {
                outline: none;
            }
            #chatInputField::placeholder {
                color: #A0AEC0;
                font-size: 14px;
            }
        """)
        self.text_edit.textChanged.connect(self._auto_resize)
        input_layout.addWidget(self.text_edit)

        # Botão para enviar mensagem com ícone
        self.send_button = QPushButton()
        self.send_button.setObjectName("chatSendButton")
        self.send_button.setIcon(
            QIcon(
                str(
                    Path(__file__).parent.parent.parent
                    / "assets"
                    / "icons"
                    / "send.svg"
                )
            )
        )
        self.send_button.setFixedSize(40, 40)
        self.send_button.setStyleSheet("""
            #chatSendButton {
                background-color: #3182CE;
                border: none;
                border-radius: 20px;
                padding: 8px;
                margin: 0 4px;
            }
            #chatSendButton:hover {
                background-color: #2B6CB0;
            }
            #chatSendButton:pressed {
                background-color: #2C5282;
            }
            #chatSendButton:disabled {
                background-color: #CBD5E0;
            }
        """)
        self.send_button.clicked.connect(self._on_send)
        input_layout.addWidget(self.send_button)

        layout.addWidget(input_container)

        # Instalando event filter para capturar teclas
        self.text_edit.installEventFilter(self)

    def _auto_resize(self) -> None:
        """Ajusta automaticamente a altura do campo de texto."""
        document_height = self.text_edit.document().size().height()
        new_height = min(max(40, document_height + 10), 120)
        self.text_edit.setFixedHeight(int(new_height))

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """Filtra eventos para capturar teclas especiais."""
        if obj == self.text_edit and event.type() == QEvent.KeyPress:
            key_event = QKeyEvent(event)
            if key_event.key() == Qt.Key_Return or key_event.key() == Qt.Key_Enter:
                if not key_event.modifiers() & Qt.ShiftModifier:
                    self._on_send()
                    return True
        return super().eventFilter(obj, event)

    def _on_send(self) -> None:
        """Manipula o evento de envio de mensagem."""
        message = self.text_edit.toPlainText().strip()
        if message:
            self.message_sent.emit(message)
            self.text_edit.clear()
            self.text_edit.setFixedHeight(40)  # Reset height after sending


class ModelSelector(QComboBox):
    """Seletor de modelos de IA."""

    model_changed = Signal(str)

    def __init__(
        self,
        models: List[str],
        default_model: str,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Inicializa o seletor de modelos.

        Args:
            models: Lista de modelos disponíveis
            default_model: Modelo padrão selecionado
            parent: Widget pai
        """
        super().__init__(parent)
        self.setObjectName("modelSelector")

        # Adicionando modelos à lista
        self.addItems(models)

        # Selecionando o modelo padrão
        default_index = self.findText(default_model)
        if default_index >= 0:
            self.setCurrentIndex(default_index)

        # Conectando sinal de mudança
        self.currentTextChanged.connect(self.model_changed.emit)


class IconButton(QPushButton):
    """Botão com ícone estilizado."""

    def __init__(
        self,
        icon_name: str,
        tooltip: str,
        color: str = PRIMARY_COLOR,
        size: int = 24,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Inicializa o botão com ícone.

        Args:
            icon_name: Nome do ícone no tema
            tooltip: Texto de dica para o botão
            color: Cor do ícone
            size: Tamanho do ícone
            parent: Widget pai
        """
        super().__init__(parent)
        self.setObjectName("iconButton")

        # Configurando o ícone
        icon = QIcon.fromTheme(icon_name)
        self.setIcon(icon)

        # Configurando o estilo
        self.setToolTip(tooltip)
        self.setFixedSize(QSize(size, size))
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {color};
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: {size // 2}px;
            }}
        """)


class SearchBox(QWidget):
    """Caixa de pesquisa estilizada."""

    search_changed = Signal(str)

    def __init__(
        self,
        placeholder: str = "Pesquisar...",
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Inicializa a caixa de pesquisa.

        Args:
            placeholder: Texto de placeholder
            parent: Widget pai
        """
        super().__init__(parent)
        self.setObjectName("searchBox")
        self._setup_ui(placeholder)

    def _setup_ui(self, placeholder: str) -> None:
        """Configura a interface da caixa de pesquisa."""
        # Layout principal
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        # Container interno
        container = QWidget()
        container.setObjectName("searchContainer")
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(8, 4, 8, 4)
        container_layout.setSpacing(8)

        # Ícone de pesquisa
        search_icon = QLabel()
        search_icon.setObjectName("searchIcon")
        search_icon.setPixmap(QIcon.fromTheme("edit-find").pixmap(16, 16))
        container_layout.addWidget(search_icon)

        # Campo de texto
        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText(placeholder)
        self.search_input.textChanged.connect(self.search_changed.emit)
        container_layout.addWidget(self.search_input)

        # Botão de limpar
        self.clear_button = QPushButton()
        self.clear_button.setObjectName("clearButton")
        self.clear_button.setIcon(QIcon.fromTheme("edit-clear"))
        self.clear_button.setFixedSize(16, 16)
        self.clear_button.clicked.connect(self.search_input.clear)
        self.clear_button.hide()
        container_layout.addWidget(self.clear_button)

        layout.addWidget(container)

        # Conecta o sinal para mostrar/ocultar o botão de limpar
        self.search_input.textChanged.connect(self._toggle_clear_button)

        # Estilo
        self.setStyleSheet("""
            #searchBox {
                background: transparent;
                border: none;
            }
            
            #searchContainer {
                background-color: #F5F7FA;
                border: 1px solid #E0E4E8;
                border-radius: 20px;
            }
            
            #searchContainer:focus-within {
                border-color: #2196F3;
                background-color: #FFFFFF;
            }
            
            #searchInput {
                background: transparent;
                border: none;
                color: #2C3E50;
                font-size: 14px;
                padding: 0;
            }
            
            #searchInput:focus {
                outline: none;
            }
            
            #searchInput::placeholder {
                color: #A0AEC0;
            }
            
            #searchIcon {
                opacity: 0.5;
            }
            
            #clearButton {
                background: transparent;
                border: none;
                padding: 0;
                opacity: 0.5;
            }
            
            #clearButton:hover {
                opacity: 0.8;
            }
        """)

    def _toggle_clear_button(self, text: str) -> None:
        """
        Mostra ou oculta o botão de limpar baseado no texto.

        Args:
            text: Texto atual do campo de pesquisa
        """
        self.clear_button.setVisible(bool(text))


class LoadingIndicator(QWidget):
    """Indicador de carregamento animado com texto."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        color: str = PRIMARY_COLOR,
        size: int = 40,
        text: str = "Carregando...",
    ) -> None:
        """
        Inicializa o indicador de carregamento.

        Args:
            parent: Widget pai
            color: Cor do indicador
            size: Tamanho do indicador
            text: Texto a ser exibido
        """
        super().__init__(parent)
        self.setObjectName("loadingIndicator")

        # Configurações visuais
        self.angle = 0
        self.color = QColor(color)
        self.text = text
        self.dots = 0
        self.dot_timer = 0

        # Configurar tamanho
        self.indicator_size = size
        self.setMinimumSize(max(size, 200), size + 30)

        # Timers para animações
        self.spin_timer = self.startTimer(30)  # Timer para rotação
        self.dot_timer = self.startTimer(500)  # Timer para os pontos

        # Efeito de fade in
        self.setAutoFillBackground(True)
        self.opacity_effect = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_effect.setDuration(200)
        self.opacity_effect.setStartValue(0)
        self.opacity_effect.setEndValue(1)
        self.opacity_effect.setEasingCurve(QEasingCurve.OutCubic)
        self.opacity_effect.start()

    def timerEvent(self, event: QTimerEvent) -> None:
        """
        Manipula eventos do timer para animações.

        Args:
            event: Evento do timer
        """
        if event.timerId() == self.spin_timer:
            self.angle = (self.angle + 5) % 360
            self.update()
        elif event.timerId() == self.dot_timer:
            self.dots = (self.dots + 1) % 4
            self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Desenha o indicador de carregamento.

        Args:
            event: Evento de pintura
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Desenhar o spinner
        center_x = self.width() / 2
        center_y = (self.height() - 20) / 2  # Ajuste para o texto

        painter.translate(center_x, center_y)
        painter.rotate(self.angle)

        painter.setPen(Qt.NoPen)

        # Desenha vários círculos em posições diferentes com opacidade variada
        for i in range(8):
            painter.save()
            painter.rotate(i * 45)
            painter.translate(self.indicator_size / 4, 0)

            # Varia a opacidade baseada na posição
            opacity = 255 - ((i * 30) % 255)
            color = QColor(self.color)
            color.setAlpha(opacity)
            painter.setBrush(color)

            circle_size = self.indicator_size / 10
            painter.drawEllipse(
                -circle_size / 2, -circle_size / 2, circle_size, circle_size
            )
            painter.restore()

        # Desenhar o texto
        painter.resetTransform()
        text = self.text + "." * self.dots
        font = painter.font()
        font.setPointSize(10)
        painter.setFont(font)

        text_rect = painter.fontMetrics().boundingRect(text)
        text_x = (self.width() - text_rect.width()) / 2
        text_y = center_y + self.indicator_size / 2 + 20

        painter.setPen(self.color)
        painter.drawText(int(text_x), int(text_y), text)

    def showEvent(self, event: QShowEvent) -> None:
        """
        Manipula evento de exibição.

        Args:
            event: Evento de exibição
        """
        super().showEvent(event)
        self.spin_timer = self.startTimer(30)
        self.dot_timer = self.startTimer(500)

    def hideEvent(self, event: QHideEvent) -> None:
        """
        Manipula evento de ocultação.

        Args:
            event: Evento de ocultação
        """
        super().hideEvent(event)
        if self.spin_timer:
            self.killTimer(self.spin_timer)
        if self.dot_timer:
            self.killTimer(self.dot_timer)


class StatusBar(QStatusBar):
    """Barra de status personalizada."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Inicializa a barra de status.

        Args:
            parent: Widget pai
        """
        super().__init__(parent)
        self.setObjectName("statusBar")
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Configura a interface da barra de status."""
        # Status padrão
        self.showMessage("Pronto")

    def update_status(self, message: str) -> None:
        """
        Atualiza a mensagem de status.

        Args:
            message: Nova mensagem
        """
        self.showMessage(message)


class ChatWidget(QWidget):
    """Widget para exibição e interação com o chat."""

    message_sent = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chatWidget")
        self._setup_ui()

    def _setup_ui(self):
        """Configura a interface do chat."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Área de mensagens
        messages_container = QWidget()
        messages_container.setObjectName("messagesContainer")
        messages_container.setStyleSheet("""
            #messagesContainer {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        messages_layout = QVBoxLayout(messages_container)
        messages_layout.setContentsMargins(0, 0, 0, 0)
        messages_layout.setSpacing(0)

        self.messages_area = QTextEdit()
        self.messages_area.setObjectName("messagesArea")
        self.messages_area.setReadOnly(True)
        self.messages_area.setStyleSheet("""
            #messagesArea {
                background-color: transparent;
                border: none;
                padding: 20px;
                font-size: 15px;
                line-height: 1.5;
            }
            #messagesArea p {
                margin: 0;
                padding: 0;
            }
        """)
        messages_layout.addWidget(self.messages_area)

        layout.addWidget(messages_container, stretch=1)

        # Área de entrada
        input_container = QWidget()
        input_container.setObjectName("chatInputContainer")
        input_container.setStyleSheet("""
            #chatInputContainer {
                background-color: #FFFFFF;
                border: 2px solid #E2E8F0;
                border-radius: 12px;
                padding: 8px;
                margin-top: 8px;
            }
            #chatInputContainer:focus-within {
                border-color: #2196F3;
            }
        """)
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(8, 8, 8, 8)
        input_layout.setSpacing(8)

        self.input_field = QTextEdit()
        self.input_field.setObjectName("chatInputField")
        self.input_field.setPlaceholderText(
            "Digite sua mensagem... (Enter para enviar, Shift+Enter para nova linha)"
        )
        self.input_field.setMaximumHeight(120)
        self.input_field.setStyleSheet("""
            #chatInputField {
                background-color: transparent;
                border: none;
                padding: 8px 12px;
                font-size: 15px;
                line-height: 1.5;
                color: #2D3748;
            }
            #chatInputField:focus {
                outline: none;
            }
            #chatInputField::placeholder {
                color: #A0AEC0;
                font-size: 14px;
            }
        """)
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
        send_button.setStyleSheet("""
            #chatSendButton {
                background-color: #3182CE;
                border: none;
                border-radius: 20px;
                padding: 8px;
                margin: 0 4px;
            }
            #chatSendButton:hover {
                background-color: #2B6CB0;
            }
            #chatSendButton:pressed {
                background-color: #2C5282;
            }
            #chatSendButton:disabled {
                background-color: #CBD5E0;
            }
        """)
        send_button.clicked.connect(self._send_message)
        input_layout.addWidget(send_button)

        layout.addWidget(input_container)

        # Conecta o evento de tecla pressionada
        self.input_field.installEventFilter(self)

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
            empty_format = QTextBlockFormat()
            empty_format.setTopMargin(20)
            cursor.insertBlock(empty_format)

        # Formata o container da mensagem
        format_block = QTextBlockFormat()
        is_user = sender == "Você"

        # Define margens e alinhamento
        format_block.setLeftMargin(24 if not is_user else 120)
        format_block.setRightMargin(120 if not is_user else 24)
        format_block.setTopMargin(8)
        format_block.setBottomMargin(8)

        # Define o estilo do bloco
        format_block.setBackground(QColor("#EBF8FF") if is_user else QColor("#F8FAFC"))
        format_block.setProperty(QTextFormat.FrameMargin, 16)
        cursor.insertBlock(format_block)

        # Insere o cabeçalho da mensagem
        header_format = QTextCharFormat()
        header_format.setFontWeight(QFont.DemiBold)
        header_format.setForeground(QColor("#3182CE") if is_user else QColor("#4A5568"))
        header_format.setFontPointSize(13)

        # Adiciona ícone e nome do remetente
        cursor.insertText("👤 " if is_user else "🤖 ", header_format)
        cursor.insertText(f"{sender} • ", header_format)

        # Adiciona timestamp
        time_format = QTextCharFormat()
        time_format.setForeground(QColor("#718096"))
        time_format.setFontPointSize(12)
        cursor.insertText(QTime.currentTime().toString("HH:mm"), time_format)
        cursor.insertText("\n")

        # Insere o conteúdo da mensagem
        content_format = QTextCharFormat()
        content_format.setFontPointSize(15)
        content_format.setForeground(QColor("#2D3748"))
        content_format.setFontFamily("Inter")

        # Processa o texto para destacar código e links
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if i > 0:
                cursor.insertText("\n")

            # Detecta blocos de código
            if line.startswith("```") or line.startswith("`"):
                code_format = QTextCharFormat()
                code_format.setFontFamily("JetBrains Mono")
                code_format.setFontPointSize(14)
                code_format.setBackground(QColor("#EDF2F7"))
                code_format.setForeground(QColor("#2D3748"))
                cursor.insertText(line, code_format)
            # Detecta links
            elif line.startswith("http://") or line.startswith("https://"):
                link_format = QTextCharFormat()
                link_format.setFontUnderline(True)
                link_format.setForeground(QColor("#4299E1"))
                cursor.insertText(line, link_format)
            else:
                cursor.insertText(line, content_format)

        # Rola para a última mensagem
        self.messages_area.setTextCursor(cursor)
        self.messages_area.ensureCursorVisible()


class TextEditor(QWidget):
    """Editor de texto simples."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Configura a interface do editor."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Digite seu texto aqui...")
        layout.addWidget(self.text_edit)
