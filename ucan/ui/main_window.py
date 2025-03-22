"""
Janela principal da aplicação.
"""

import asyncio
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
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

        # Define os estilos
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F7FA;
            }
            
            #sidebarWidget {
                background-color: #FFFFFF;
                border-right: 1px solid #E2E8F0;
                min-width: 280px;
                max-width: 380px;
            }
            
            #chatWidget {
                background-color: #FFFFFF;
                border-radius: 8px;
                margin: 16px;
            }
            
            #knowledgePanel {
                background-color: #FFFFFF;
                border-left: 1px solid #E2E8F0;
                min-width: 320px;
                max-width: 420px;
                padding: 0;
            }
            
            #knowledgePanel #sectionHeader {
                background-color: #F8FAFC;
                border-bottom: 1px solid #E2E8F0;
                padding: 16px 20px;
                margin: 0;
            }
            
            #knowledgePanel #actionButton {
                background-color: #EBF8FF;
                color: #2B6CB0;
                border: 2px solid #BEE3F8;
                font-weight: 600;
            }
            
            #knowledgePanel #actionButton:hover {
                background-color: #BEE3F8;
                border-color: #90CDF4;
            }
            
            #knowledgePanel #actionButton:pressed {
                background-color: #90CDF4;
                border-color: #63B3ED;
            }
            
            QStatusBar {
                background-color: #F8FAFC;
                border-top: 1px solid #E2E8F0;
                color: #4A5568;
                padding: 6px 16px;
                font-size: 13px;
            }
            
            QStatusBar::item {
                border: none;
            }
            
            #searchBox {
                background-color: #F8FAFC;
                border: 2px solid #E2E8F0;
                border-radius: 24px;
                padding: 10px 16px;
                margin: 12px 16px;
            }
            
            #searchBox:focus-within {
                border-color: #2196F3;
                background-color: #FFFFFF;
                box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
            }
            
            #searchBox QLineEdit {
                background: transparent;
                border: none;
                color: #2C3E50;
            }
        """)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Splitter principal para dividir a interface
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

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

        # Atualiza o estilo do botão de nova conversa
        self.setStyleSheet(
            self.styleSheet()
            + """
            #newChatButton {
                background-color: #E3F2FD;
                border: none;
                border-radius: 16px;
                padding: 6px;
            }
            
            #newChatButton:hover {
                background-color: #BBDEFB;
            }
            
            #newChatButton:pressed {
                background-color: #90CAF9;
            }
        """
        )

        sidebar_layout.addWidget(sidebar_header)

        # Barra de pesquisa
        search_box = SearchBox("Pesquisar conversas...")
        search_box.search_changed.connect(self._on_search)
        sidebar_layout.addWidget(search_box)

        # Lista de conversas (placeholder por enquanto)
        conversations_list = QWidget()
        conversations_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sidebar_layout.addWidget(conversations_list)

        splitter.addWidget(sidebar)

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
        self.chat_widget = ChatWidget()
        self.chat_widget.message_sent.connect(self._on_message_sent)
        chat_layout.addWidget(self.chat_widget)

        splitter.addWidget(chat_container)

        # Painel de conhecimento
        knowledge_panel = QWidget()
        knowledge_panel.setObjectName("knowledgePanel")
        knowledge_layout = QVBoxLayout(knowledge_panel)

        knowledge_header = QLabel("Base de Conhecimento")
        knowledge_header.setObjectName("sectionHeader")
        knowledge_layout.addWidget(knowledge_header)

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

        splitter.addWidget(knowledge_panel)

        # Configura as proporções do splitter
        splitter.setStretchFactor(0, 1)  # Sidebar
        splitter.setStretchFactor(1, 2)  # Chat
        splitter.setStretchFactor(2, 1)  # Knowledge Panel

        # Barra de status
        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)

        # Indicador de carregamento (inicialmente oculto)
        self.loading = LoadingIndicator(self)
        self.loading.hide()

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
