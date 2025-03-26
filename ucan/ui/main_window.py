"""
Janela principal da aplicação.
"""

import asyncio
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from ucan.core.app_controller import AppController
from ucan.ui.components import ChatWidget, LoadingIndicator, SearchBox, StatusBar


class MainWindow(QMainWindow):
    """Janela principal da aplicação."""

    def __init__(self, app_controller: AppController) -> None:
        """
        Inicializa a janela principal.

        Args:
            app_controller: Controlador da aplicação
        """
        super().__init__()
        self.app_controller = app_controller
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Configura a interface da janela."""
        # Configurações básicas da janela
        self.setWindowTitle("UCAN")
        self.setMinimumSize(1200, 800)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Splitter principal para dividir a interface
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(1)
        self.splitter.setChildrenCollapsible(False)
        layout.addWidget(self.splitter)

        # Sidebar (lista de conversas)
        sidebar = QWidget()
        sidebar.setObjectName("sidebarWidget")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Cabeçalho da sidebar
        sidebar_header = QWidget()
        sidebar_header_layout = QHBoxLayout(sidebar_header)
        sidebar_header_layout.setContentsMargins(16, 16, 16, 8)

        header_label = QLabel("Conversas")
        header_label.setObjectName("sectionHeader")
        sidebar_header_layout.addWidget(header_label)

        new_chat_btn = QPushButton()
        new_chat_btn.setObjectName("newChatButton")
        new_chat_btn.setIcon(QIcon.fromTheme("document-new"))
        new_chat_btn.setToolTip("Nova Conversa")
        new_chat_btn.setFixedSize(32, 32)
        new_chat_btn.clicked.connect(self._on_new_chat)
        sidebar_header_layout.addWidget(new_chat_btn)

        sidebar_layout.addWidget(sidebar_header)

        # Barra de pesquisa
        search_box = SearchBox("Pesquisar conversas...")
        search_box.search_changed.connect(self._on_search)
        sidebar_layout.addWidget(search_box)

        # Lista de conversas (placeholder por enquanto)
        conversations_list = QWidget()
        conversations_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sidebar_layout.addWidget(conversations_list)

        self.splitter.addWidget(sidebar)

        # Área principal de chat
        chat_container = QWidget()
        chat_container.setObjectName("chatWidget")
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)

        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        chat_layout.addWidget(toolbar)

        # Widget de chat
        self.chat_widget = ChatWidget(parent=chat_container)
        self.chat_widget.message_sent.connect(self._on_message_sent)
        chat_layout.addWidget(self.chat_widget)

        self.splitter.addWidget(chat_container)

        # Painel de conhecimento
        knowledge_panel = QWidget()
        knowledge_panel.setObjectName("knowledgePanel")
        knowledge_layout = QVBoxLayout(knowledge_panel)

        knowledge_header = QLabel("Base de Conhecimento")
        knowledge_header.setObjectName("sectionHeader")
        knowledge_layout.addWidget(knowledge_header)

        # Área de drop para arquivos
        drop_area = QWidget()
        drop_area.setObjectName("dropArea")
        drop_area.setAcceptDrops(True)
        drop_layout = QVBoxLayout(drop_area)
        drop_layout.setContentsMargins(16, 16, 16, 16)
        drop_layout.setSpacing(8)

        drop_icon = QLabel()
        drop_icon.setObjectName("dropIcon")
        drop_icon.setPixmap(QIcon.fromTheme("document-new").pixmap(32, 32))
        drop_icon.setAlignment(Qt.AlignCenter)
        drop_layout.addWidget(drop_icon)

        drop_label = QLabel("Arraste arquivos aqui")
        drop_label.setObjectName("dropLabel")
        drop_label.setAlignment(Qt.AlignCenter)
        drop_layout.addWidget(drop_label)

        drop_sublabel = QLabel("ou clique para selecionar")
        drop_sublabel.setObjectName("dropSubLabel")
        drop_sublabel.setAlignment(Qt.AlignCenter)
        drop_layout.addWidget(drop_sublabel)

        knowledge_layout.addWidget(drop_area)

        # Botões de ação
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 8, 0, 8)

        file_btn = QPushButton("Arquivo")
        file_btn.setObjectName("actionButton")
        file_btn.clicked.connect(self._on_file_upload)
        actions_layout.addWidget(file_btn)

        url_btn = QPushButton("URL")
        url_btn.setObjectName("actionButton")
        url_btn.clicked.connect(self._on_url_add)
        actions_layout.addWidget(url_btn)

        knowledge_layout.addWidget(actions_widget)
        knowledge_layout.addStretch()

        self.splitter.addWidget(knowledge_panel)

        # Configura as proporções do splitter
        self.splitter.setStretchFactor(0, 1)  # Sidebar
        self.splitter.setStretchFactor(1, 2)  # Chat
        self.splitter.setStretchFactor(2, 1)  # Knowledge Panel

        # Define os tamanhos iniciais
        self.splitter.setSizes([280, self.width() - 680, 400])

        # Barra de status
        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)

        # Indicador de carregamento (inicialmente oculto)
        self.loading = LoadingIndicator(self)
        self.loading.hide()

        # Habilita drag and drop
        self.setAcceptDrops(True)

        # Configura o tema
        from ucan.ui.theme_manager import theme_manager

        theme_manager.theme_changed.connect(self._apply_theme)
        self._apply_theme()

    def _apply_theme(self):
        """Aplica o tema atual."""
        from ucan.ui.theme_manager import theme_manager

        if theme := theme_manager.current_theme:
            self.setStyleSheet(theme.generate_stylesheet())
            # Atualiza também os componentes filhos importantes
            if hasattr(self, "chat_widget"):
                self.chat_widget.setStyleSheet(theme.generate_stylesheet())
            if hasattr(self, "status_bar"):
                self.status_bar.setStyleSheet(theme.generate_stylesheet())

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Manipula o evento de início de drag."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.findChild(QWidget, "dropArea").setProperty("dragOver", True)
            self.style().polish(self.findChild(QWidget, "dropArea"))

    def dragLeaveEvent(self, event: QDragEnterEvent) -> None:
        """Manipula o evento de saída de drag."""
        self.findChild(QWidget, "dropArea").setProperty("dragOver", False)
        self.style().polish(self.findChild(QWidget, "dropArea"))

    def dropEvent(self, event: QDropEvent) -> None:
        """Manipula o evento de drop."""
        self.findChild(QWidget, "dropArea").setProperty("dragOver", False)
        self.style().polish(self.findChild(QWidget, "dropArea"))

        urls = event.mimeData().urls()
        for url in urls:
            file_path = url.toLocalFile()
            if file_path:
                self.app_controller.add_file_to_knowledge_base(file_path)

    def _on_new_chat(self) -> None:
        """Cria uma nova conversa."""
        self.app_controller.new_conversation()

    def _on_search(self, query: str) -> None:
        """
        Pesquisa conversas.

        Args:
            query: Termo de pesquisa
        """
        self.app_controller.search_conversations(query)

    async def _send_message(self, message: str) -> None:
        """
        Envia uma mensagem de forma assíncrona.

        Args:
            message: Conteúdo da mensagem
        """
        await self.app_controller.send_message(message)

    def _on_message_sent(self, message: str) -> None:
        """
        Manipula o envio de uma mensagem.

        Args:
            message: Conteúdo da mensagem
        """
        if not message.strip():
            return

        # Cria uma task para enviar a mensagem de forma assíncrona
        loop = asyncio.get_event_loop()
        loop.create_task(self._send_message(message))

    def _on_file_upload(self) -> None:
        """Manipula o upload de arquivo."""
        self.app_controller.upload_file()

    def _on_url_add(self) -> None:
        """Manipula a adição de URL."""
        self.app_controller.add_url()

    def show_loading(self, message: Optional[str] = None) -> None:
        """
        Exibe o indicador de carregamento.

        Args:
            message: Mensagem opcional para exibir
        """
        if message:
            self.loading.text = message
        self.loading.show()

    def hide_loading(self) -> None:
        """Oculta o indicador de carregamento."""
        self.loading.hide()

    def update_status(self, message: str) -> None:
        """
        Atualiza a mensagem de status.

        Args:
            message: Nova mensagem
        """
        self.status_bar.update_status(message)
