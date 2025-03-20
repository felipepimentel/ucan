"""
Componentes reutilizáveis para a interface gráfica.
"""

from typing import List, Optional

from PySide6.QtCore import QSize, Qt, QTimerEvent, Signal
from PySide6.QtGui import QColor, QHideEvent, QIcon, QPainter, QPaintEvent, QShowEvent
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from ucan.config.constants import PRIMARY_COLOR


class MessageBubble(QFrame):
    """Bolha de mensagem para exibir conversas."""

    def __init__(
        self,
        message: str,
        is_user: bool = False,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Inicializa a bolha de mensagem.

        Args:
            message: Texto da mensagem
            is_user: True se a mensagem for do usuário, False se for do assistente
            parent: Widget pai
        """
        super().__init__(parent)
        self.is_user = is_user
        self.setObjectName("messageBubble")

        # Configuração de layout e estilo
        self.setStyleSheet(f"""
            #messageBubble {{
                border-radius: 12px;
                padding: 10px;
                background-color: {PRIMARY_COLOR if is_user else "#3d5a80"};
            }}
        """)

        # Layout vertical para a mensagem
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Adicionando o texto da mensagem
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setTextFormat(Qt.TextFormat.MarkdownText)
        layout.addWidget(message_label)

        # Alinhamento baseado em quem enviou a mensagem
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)


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

        # Área de texto para entrada da mensagem
        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlaceholderText("Digite sua mensagem aqui...")
        self.text_edit.setMaximumHeight(100)
        layout.addWidget(self.text_edit)

        # Layout para botões
        button_layout = QHBoxLayout()

        # Botão para enviar mensagem
        self.send_button = QPushButton("Enviar")
        self.send_button.setIcon(QIcon.fromTheme("mail-send"))
        self.send_button.clicked.connect(self._on_send)

        # Adicionando espaçador e botão ao layout
        button_layout.addStretch()
        button_layout.addWidget(self.send_button)

        layout.addLayout(button_layout)

        # Conectando atalho Enter para enviar mensagem
        self.text_edit.textChanged.connect(self._check_enter)

    def _on_send(self) -> None:
        """Manipula o evento de envio de mensagem."""
        message = self.text_edit.toPlainText().strip()
        if message:
            self.message_sent.emit(message)
            self.text_edit.clear()

    def _check_enter(self) -> None:
        """Verifica se o usuário pressionou Enter para enviar a mensagem."""
        text = self.text_edit.toPlainText()
        if text.endswith("\n"):
            # Remove a quebra de linha e envia, exceto se Shift+Enter foi usado
            cursor_position = self.text_edit.textCursor().position()
            document_size = len(self.text_edit.toPlainText())

            if cursor_position == document_size:  # Cursor no final do texto
                text = text.rstrip("\n")
                self.text_edit.setPlainText(text)
                self._on_send()


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

        # Layout principal
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Ícone de pesquisa
        self.search_icon = QLabel()
        self.search_icon.setPixmap(QIcon.fromTheme("edit-find").pixmap(16, 16))
        layout.addWidget(self.search_icon)

        # Campo de texto
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(placeholder)
        self.search_input.textChanged.connect(self.search_changed.emit)
        layout.addWidget(self.search_input)

        # Estilo
        self.setStyleSheet("""
            #searchBox {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 5px 10px;
            }
            QLineEdit {
                background-color: transparent;
                border: none;
            }
        """)


class LoadingIndicator(QWidget):
    """Indicador de carregamento animado."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        color: str = PRIMARY_COLOR,
        size: int = 40,
    ) -> None:
        """
        Inicializa o indicador de carregamento.

        Args:
            parent: Widget pai
            color: Cor do indicador
            size: Tamanho do indicador
        """
        super().__init__(parent)
        self.setObjectName("loadingIndicator")

        # Configurações visuais
        self.angle = 0
        self.color = QColor(color)
        self.setFixedSize(size, size)

        # Timer para animação
        self.timer_id = self.startTimer(30)

    def timerEvent(self, event: QTimerEvent) -> None:
        """Manipula eventos do timer para animação."""
        self.angle = (self.angle + 5) % 360
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """Desenha o indicador de carregamento."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width, height = self.width(), self.height()
        painter.translate(width / 2, height / 2)
        painter.rotate(self.angle)

        painter.setPen(Qt.NoPen)

        # Desenha vários círculos em posições diferentes com opacidade variada
        for i in range(8):
            painter.save()
            painter.rotate(i * 45)
            painter.translate(width / 4, 0)

            # Varia a opacidade baseada na posição
            opacity = 255 - ((i * 30) % 255)
            color = QColor(self.color)
            color.setAlpha(opacity)
            painter.setBrush(color)

            painter.drawEllipse(-width / 20, -height / 20, width / 10, height / 10)
            painter.restore()

    def showEvent(self, event: QShowEvent) -> None:
        """Manipula evento de exibição."""
        super().showEvent(event)
        self.timer_id = self.startTimer(30)

    def hideEvent(self, event: QHideEvent) -> None:
        """Manipula evento de ocultação."""
        super().hideEvent(event)
        self.killTimer(self.timer_id)


class StatusBar(QStatusBar):
    """Barra de status da aplicação."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Inicializa a barra de status.

        Args:
            parent: Widget pai
        """
        super().__init__(parent)
        self.setObjectName("statusBar")

        # Configurar layout
        self.status_label = QLabel()
        self.status_label.setObjectName("statusLabel")
        self.addWidget(self.status_label)

        # Indicador de conexão
        self.connection_indicator = QLabel()
        self.connection_indicator.setObjectName("connectionIndicator")
        self.connection_indicator.setFixedSize(16, 16)
        self.addPermanentWidget(self.connection_indicator)

        # Configurar estado inicial
        self.set_status_message("Pronto")
        self.set_connection_status(False)

    def set_status_message(self, message: str) -> None:
        """
        Define a mensagem de status.

        Args:
            message: Mensagem a ser exibida
        """
        self.status_label.setText(message)

    def set_connection_status(self, connected: bool) -> None:
        """
        Define o status de conexão.

        Args:
            connected: True se conectado, False caso contrário
        """
        color = "#4CAF50" if connected else "#F44336"
        self.connection_indicator.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                border-radius: 8px;
            }}
        """)
