"""
Janela principal da aplicação UCAN.
"""

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStatusBar,
    QWidget,
)

from ucan.config.constants import (
    APP_VERSION,
    RESOURCES_DIR,
)
from ucan.core.app_controller import AppController
from ucan.ui.chat_widget import ChatWidget
from ucan.ui.conversation_list import ConversationList


class MainWindow(QMainWindow):
    """Janela principal da aplicação UCAN."""

    error_occurred = Signal(str)  # Sinal emitido quando ocorre um erro
    status_message = Signal(str)  # Sinal emitido para atualizar a barra de status

    def __init__(self, controller: AppController) -> None:
        """Inicializa a janela principal."""
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.controller = controller
        self._setup_window()
        self._setup_ui()
        self._setup_signals()
        self._setup_menu()

    def _setup_window(self):
        self.setWindowTitle("UCAN - Universal Chat Assistant Network")
        self.setWindowIcon(QIcon(str(RESOURCES_DIR / "icons" / "app_icon.svg")))
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)

    def _setup_ui(self) -> None:
        """Configura a interface do usuário."""
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        layout.addWidget(self.splitter)

        self.conversation_list = ConversationList(self.controller)
        self.splitter.addWidget(self.conversation_list)

        self.chat_widget = ChatWidget(self.controller)
        self.splitter.addWidget(self.chat_widget)

        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        self.status_bar = QStatusBar()
        self.status_bar.setObjectName("statusBar")
        self.setStatusBar(self.status_bar)

    def _setup_signals(self) -> None:
        """Configura os sinais da interface."""
        self.error_occurred.connect(self._show_error_dialog)
        self.status_message.connect(self.status_bar.showMessage)
        self.controller.initialization_failed.connect(self._show_error_dialog)

    def _setup_menu(self) -> None:
        """Configura o menu da aplicação."""
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&Arquivo")

        new_action = QAction(
            QIcon(str(RESOURCES_DIR / "icons" / "new.svg")), "&Nova Conversa", self
        )
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_conversation)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        export_action = QAction(
            QIcon(str(RESOURCES_DIR / "icons" / "export.svg")),
            "&Exportar Conversa",
            self,
        )
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._export_conversation)
        file_menu.addAction(export_action)

        import_action = QAction(
            QIcon(str(RESOURCES_DIR / "icons" / "import.svg")),
            "&Importar Conversa",
            self,
        )
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self._import_conversation)
        file_menu.addAction(import_action)

        file_menu.addSeparator()

        exit_action = QAction(
            QIcon(str(RESOURCES_DIR / "icons" / "exit.svg")), "Sai&r", self
        )
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menu_bar.addMenu("A&juda")

        about_action = QAction(
            QIcon(str(RESOURCES_DIR / "icons" / "about.svg")), "&Sobre", self
        )
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)

    def _show_error_dialog(self, message: str) -> None:
        """Mostra uma caixa de diálogo de erro."""
        QMessageBox.critical(self, "Erro", message)

    def _show_about_dialog(self):
        QMessageBox.about(
            self,
            "Sobre o UCAN",
            f"""<h3>UCAN - Universal Chat Assistant Network</h3>
            <p>Versão {APP_VERSION}</p>
            <p>Um assistente de chat universal e extensível.</p>""",
        )

    def _new_conversation(self) -> None:
        """Cria uma nova conversa."""
        self.controller.new_conversation()

    def _export_conversation(self) -> None:
        """Exporta a conversa atual."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Conversa", "", "Arquivos JSON (*.json)"
        )
        if file_path:
            try:
                self.controller.export_conversation(file_path)
                self.status_message.emit("Conversa exportada com sucesso!")
            except Exception as e:
                self.error_occurred.emit(f"Erro ao exportar conversa: {str(e)}")

    def _import_conversation(self) -> None:
        """Importa uma conversa."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Importar Conversa", "", "Arquivos JSON (*.json)"
        )
        if file_path:
            try:
                self.controller.import_conversation(file_path)
                self.status_message.emit("Conversa importada com sucesso!")
            except Exception as e:
                self.error_occurred.emit(f"Erro ao importar conversa: {str(e)}")

    def closeEvent(self, event):
        try:
            self.controller.save_state()
            event.accept()
        except Exception as e:
            self.error_occurred.emit(f"Erro ao salvar estado: {str(e)}")
            event.ignore()
