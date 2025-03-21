"""
Janela principal da aplicação UCAN.
"""

from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QFont, QIcon
from PySide6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from ucan.config.constants import RESOURCES_DIR
from ucan.core.app_controller import AppController
from ucan.core.knowledge_base import KnowledgeBase
from ucan.ui.chat_widget import ChatWidget
from ucan.ui.conversation_list_widget import ConversationListWidget
from ucan.ui.conversation_type_dialog import ConversationTypeDialog
from ucan.ui.dialogs.theme_dialog import ThemeDialog
from ucan.ui.knowledge_base_dialog import KnowledgeBaseDialog
from ucan.ui.new_conversation_dialog import NewConversationDialog
from ucan.ui.theme_manager import theme_manager


class MainWindow(QMainWindow):
    """Janela principal da aplicação."""

    def __init__(self, controller: AppController):
        """
        Inicializa a janela principal.

        Args:
            controller: Controlador da aplicação
        """
        super().__init__()
        self.controller = controller
        self.setWindowTitle("UCAN")
        self.setMinimumSize(800, 600)
        self._setup_ui()
        self._setup_menu()
        self._setup_signals()
        self._apply_theme()

    def _setup_ui(self):
        """Configura a interface do usuário."""
        self.setWindowTitle("UCAN")
        self.setMinimumSize(QSize(1200, 800))
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
        """)

        # Widget central
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)

        # Header com título e subtítulo
        header = QWidget()
        header.setObjectName("header")
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(20, 15, 20, 15)
        header_layout.setSpacing(5)
        header.setLayout(header_layout)

        title = QLabel("UCAN")
        title.setObjectName("appTitle")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)

        subtitle = QLabel("Seu assistente de programação")
        subtitle.setObjectName("appSubtitle")
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle.setFont(subtitle_font)
        header_layout.addWidget(subtitle)

        main_layout.addWidget(header)

        # Barra de ferramentas moderna
        toolbar = QToolBar("Principal")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        toolbar.setObjectName("mainToolbar")
        self.addToolBar(toolbar)

        # Botão Nova Conversa com ícone
        new_chat_action = QAction(
            QIcon(str(RESOURCES_DIR / "icons" / "chat-plus.svg")), "Nova Conversa", self
        )
        new_chat_action.triggered.connect(self._show_new_conversation_dialog)
        new_chat_action.setStatusTip("Criar uma nova conversa")
        toolbar.addAction(new_chat_action)

        # Botão Novo Tipo com ícone
        new_type_action = QAction(
            QIcon(str(RESOURCES_DIR / "icons" / "system.svg")), "Novo Tipo", self
        )
        new_type_action.triggered.connect(self._show_conversation_type_dialog)
        new_type_action.setStatusTip("Criar um novo tipo de conversa")
        toolbar.addAction(new_type_action)

        # Botão Nova Base com ícone
        new_kb_action = QAction(
            QIcon(str(RESOURCES_DIR / "icons" / "book-open.svg")), "Nova Base", self
        )
        new_kb_action.triggered.connect(self._show_knowledge_base_dialog)
        new_kb_action.setStatusTip("Criar uma nova base de conhecimento")
        toolbar.addAction(new_kb_action)

        # Splitter principal com proporções melhores
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setObjectName("mainSplitter")
        main_layout.addWidget(splitter)

        # Container da lista de conversas
        conversation_container = QWidget()
        conversation_container.setObjectName("conversationContainer")
        conversation_layout = QVBoxLayout()
        conversation_layout.setContentsMargins(0, 0, 0, 0)
        conversation_layout.setSpacing(0)
        conversation_container.setLayout(conversation_layout)

        # Título da lista de conversas
        conversation_header = QWidget()
        conversation_header.setObjectName("conversationHeader")
        conversation_header_layout = QHBoxLayout()
        conversation_header_layout.setContentsMargins(15, 15, 15, 15)
        conversation_header.setLayout(conversation_header_layout)

        conversation_title = QLabel("Conversas")
        conversation_title.setObjectName("sectionTitle")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        conversation_title.setFont(title_font)
        conversation_header_layout.addWidget(conversation_title)

        conversation_layout.addWidget(conversation_header)

        # Lista de conversas com estilo moderno
        self.conversation_list = ConversationListWidget()
        self.conversation_list.setObjectName("conversationListWidget")
        self.conversation_list.setMinimumWidth(280)
        self.conversation_list.setMaximumWidth(350)
        conversation_layout.addWidget(self.conversation_list)

        splitter.addWidget(conversation_container)

        # Widget de chat
        self.chat_widget = ChatWidget(self.controller)
        self.chat_widget.setObjectName("chatWidget")
        splitter.addWidget(self.chat_widget)

        # Ajusta o tamanho inicial do splitter (25% lista, 75% chat)
        splitter.setSizes([250, 950])

        # Barra de status moderna
        self.status_bar = QStatusBar()
        self.status_bar.setObjectName("statusBar")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Pronto")

    def _setup_menu(self):
        """Configura o menu da aplicação."""
        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)

        # Menu Arquivo
        file_menu = menu_bar.addMenu("Arquivo")

        import_action = QAction("Importar Conversa", self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self._on_import_conversation)
        file_menu.addAction(import_action)

        export_action = QAction("Exportar Conversa", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._on_export_conversation)
        file_menu.addAction(export_action)

        theme_action = QAction("&Temas...", self)
        theme_action.setStatusTip("Gerenciar temas")
        theme_action.triggered.connect(self._show_theme_dialog)
        file_menu.addAction(theme_action)

        file_menu.addSeparator()

        exit_action = QAction("Sair", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Menu Exibir
        view_menu = menu_bar.addMenu("Exibir")

        knowledge_action = QAction("Bases de Conhecimento", self)
        knowledge_action.setCheckable(True)
        knowledge_action.setChecked(True)
        knowledge_action.triggered.connect(self._on_toggle_knowledge_base)
        view_menu.addAction(knowledge_action)

        # Menu Configurações
        settings_menu = menu_bar.addMenu("Configurações")

        # Menu Ajuda
        help_menu = menu_bar.addMenu("Ajuda")

        # About action
        about_action = QAction("Sobre", self)
        about_action.setStatusTip("Sobre o UCAN")
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_signals(self):
        """Configura os sinais da aplicação."""
        # Sinais do controller
        self.controller.conversations_updated.connect(
            self.conversation_list.set_conversations
        )
        self.controller.conversation_selected.connect(self.chat_widget.set_conversation)
        self.controller.conversation_type_created.connect(
            self._on_conversation_type_created
        )
        self.controller.knowledge_base_created.connect(self._on_knowledge_base_created)

        # Sinais da lista de conversas
        self.conversation_list.conversation_selected.connect(
            self.controller.select_conversation
        )
        self.conversation_list.new_conversation_requested.connect(
            self._show_new_conversation_dialog
        )

        # Atualiza a lista de tipos de conversa
        self.conversation_list.set_conversation_types(
            self.controller.get_conversation_types()
        )

        # Conexões de tema e hot reload
        theme_manager.theme_changed.connect(self._apply_theme)
        theme_manager.css_file_changed.connect(self._on_css_file_changed)

    def _show_new_conversation_dialog(self):
        """Exibe o diálogo de nova conversa."""
        dialog = NewConversationDialog(
            self,
            conversation_types=self.controller.get_conversation_types(),
        )
        if dialog.exec():
            name, conv_type = dialog.get_values()
            self.controller.create_conversation(name, conv_type)

    def _show_conversation_type_dialog(self):
        """Exibe o diálogo de novo tipo de conversa."""
        dialog = ConversationTypeDialog(self)
        if dialog.exec():
            name, description = dialog.get_values()
            self.controller.create_conversation_type(name, description)

    def _show_knowledge_base_dialog(self):
        """Exibe o diálogo de nova base de conhecimento."""
        dialog = KnowledgeBaseDialog(self)
        if dialog.exec():
            name, description, scope = dialog.get_values()
            self.controller.create_knowledge_base(name, description, scope)

    def _on_import_conversation(self):
        """Manipula a importação de uma conversa."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Importar Conversa",
            str(Path.home()),
            "Arquivos JSON (*.json)",
        )

        if file_path:
            conversation_id = self.controller.import_conversation(Path(file_path))
            if conversation_id:
                QMessageBox.information(
                    self, "Sucesso", "Conversa importada com sucesso!"
                )
            else:
                QMessageBox.warning(
                    self, "Erro", "Não foi possível importar a conversa."
                )

    def _on_export_conversation(self):
        """Manipula a exportação de uma conversa."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Conversa",
            str(Path.home()),
            "Arquivos JSON (*.json)",
        )

        if file_path:
            if self.controller.export_conversation(Path(file_path)):
                QMessageBox.information(
                    self, "Sucesso", "Conversa exportada com sucesso!"
                )
            else:
                QMessageBox.warning(
                    self, "Erro", "Não foi possível exportar a conversa."
                )

    def _on_toggle_knowledge_base(self, checked: bool):
        """
        Manipula a exibição/ocultação do dock de bases de conhecimento.

        Args:
            checked: Se o dock deve ser exibido
        """
        for dock in self.findChildren(QDockWidget):
            if dock.windowTitle() == "Bases de Conhecimento":
                dock.setVisible(checked)

    def _show_error(self, message: str):
        """
        Exibe uma mensagem de erro.

        Args:
            message: Mensagem de erro
        """
        QMessageBox.critical(self, "Erro", message)

    def _on_knowledge_base_created(self, base: KnowledgeBase):
        """
        Manipula a criação de uma base de conhecimento.

        Args:
            base: Base de conhecimento criada
        """
        QMessageBox.information(
            self, "Sucesso", f"Base de conhecimento '{base.name}' criada com sucesso!"
        )

    def _on_conversation_type_created(self):
        """Chamado quando um novo tipo de conversa é criado."""
        self.conversation_list.set_conversation_types(
            self.controller.get_conversation_types()
        )
        QMessageBox.information(self, "Sucesso", "Tipo de conversa criado com sucesso!")

    def _show_theme_dialog(self):
        """Show the theme management dialog."""
        dialog = ThemeDialog(self)
        dialog.exec()

    def _show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "Sobre o UCAN",
            "UCAN v0.1.0\n\n"
            "Um assistente de IA conversacional para ajudar em tarefas de programação.\n\n"
            "© 2024 UCAN Team",
        )

    def _apply_theme(self):
        """
        Aplica o tema atual à janela principal.
        """
        try:
            # Aplicar estilos básicos diretamente aos widgets importantes
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1a1b26;
                }
                
                QMenuBar {
                    background-color: #24283b;
                    color: #a9b1d6;
                    border-bottom: 1px solid #32344a;
                }
                
                QStatusBar {
                    background-color: #1f2335;
                    color: #a9b1d6;
                    border-top: 1px solid #32344a;
                }
                
                QPushButton {
                    background-color: #7aa2f7;
                    color: #1a1b26;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 600;
                }
            """)
            
            # Aplicar estilos específicos aos componentes principais
            if hasattr(self, 'chat_widget'):
                self.chat_widget._apply_theme()
                
            if hasattr(self, 'conversation_list'):
                self.conversation_list._apply_theme()
        
        except Exception as e:
            logger.error(f"Erro ao aplicar tema à janela principal: {e}")
            # Se falhar, aplicar estilo mínimo
            self.setStyleSheet("background-color: #1a1b26;")

    def _on_css_file_changed(self):
        """
        Chamado quando um arquivo CSS é alterado.
        Atualiza toda a UI imediatamente.
        """
        logger.info("Applying hot reload changes to the entire UI")
        self._apply_theme()

        # Atualiza também widgets filhos importantes
        if hasattr(self, 'chat_widget'):
            self.chat_widget._apply_theme()
            
        if hasattr(self, 'conversation_list'):
            self.conversation_list._apply_theme()

        # Atualiza a barra de status com mensagem informativa
        self.status_bar.showMessage("Hot reload: CSS atualizado", 3000)
