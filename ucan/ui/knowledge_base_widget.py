"""
Widget para gerenciamento de bases de conhecimento.
"""

from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ucan.core.knowledge_base import KnowledgeBase
from ucan.ui.knowledge_base_dialog import KnowledgeBaseDialog


class KnowledgeBaseWidget(QWidget):
    """Widget para gerenciamento de bases de conhecimento."""

    knowledge_base_selected = Signal(KnowledgeBase)
    add_files_requested = Signal(KnowledgeBase, list)
    add_directory_requested = Signal(KnowledgeBase, Path, str, bool)
    create_base_requested = Signal(str, str, str)

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Inicializa o widget.

        Args:
            parent: Widget pai (opcional)
        """
        super().__init__(parent)
        self._setup_ui()
        self._current_base: Optional[KnowledgeBase] = None

    def _setup_ui(self):
        """Configura a interface do usuário."""
        layout = QHBoxLayout()
        self.setLayout(layout)

        # Painel esquerdo - Lista de bases
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)

        # Lista de bases
        self.base_list = QListWidget()
        self.base_list.itemClicked.connect(self._on_base_selected)
        left_layout.addWidget(QLabel("Bases de Conhecimento"))
        left_layout.addWidget(self.base_list)

        # Botão para criar nova base
        create_button = QPushButton("Nova Base")
        create_button.clicked.connect(self._show_create_dialog)
        left_layout.addWidget(create_button)

        layout.addWidget(left_panel)

        # Painel direito - Detalhes da base
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)

        # Informações da base
        self.name_label = QLabel()
        self.description_label = QLabel()
        self.scope_label = QLabel()
        right_layout.addWidget(self.name_label)
        right_layout.addWidget(self.description_label)
        right_layout.addWidget(self.scope_label)

        # Lista de arquivos
        right_layout.addWidget(QLabel("Arquivos"))
        self.file_list = QListWidget()
        right_layout.addWidget(self.file_list)

        # Botões de ação
        button_layout = QHBoxLayout()

        add_files_button = QPushButton("Adicionar Arquivos")
        add_files_button.clicked.connect(self._on_add_files)
        button_layout.addWidget(add_files_button)

        add_dir_button = QPushButton("Adicionar Diretório")
        add_dir_button.clicked.connect(self._on_add_directory)
        button_layout.addWidget(add_dir_button)

        right_layout.addLayout(button_layout)
        layout.addWidget(right_panel)

    def set_knowledge_bases(self, bases: List[KnowledgeBase]):
        """
        Atualiza a lista de bases de conhecimento.

        Args:
            bases: Lista de bases de conhecimento
        """
        self.base_list.clear()
        for base in bases:
            item = QListWidgetItem(base.name)
            item.setData(Qt.UserRole, base)
            self.base_list.addItem(item)

    def _on_base_selected(self, item: QListWidgetItem):
        """
        Manipula a seleção de uma base na lista.

        Args:
            item: Item selecionado
        """
        base = item.data(Qt.UserRole)
        self._current_base = base
        self.knowledge_base_selected.emit(base)
        self._update_base_details()

    def _update_base_details(self):
        """Atualiza os detalhes da base selecionada."""
        if not self._current_base:
            return

        self.name_label.setText(f"Nome: {self._current_base.name}")
        self.description_label.setText(f"Descrição: {self._current_base.description}")
        self.scope_label.setText(f"Escopo: {self._current_base.scope}")

        self.file_list.clear()
        for item in self._current_base.get_items():
            self.file_list.addItem(item.file_name)

    def _show_create_dialog(self):
        """Mostra o diálogo para criar uma nova base."""
        dialog = KnowledgeBaseDialog(self)
        if dialog.exec():
            name, description, scope = dialog.get_values()
            self.create_base_requested.emit(name, description, scope)

    def _on_add_files(self):
        """Manipula a adição de arquivos à base."""
        if not self._current_base:
            return

        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Selecionar Arquivos",
            str(Path.home()),
            "Todos os Arquivos (*.*)",
        )

        if files:
            self.add_files_requested.emit(self._current_base, [Path(f) for f in files])

    def _on_add_directory(self):
        """Manipula a adição de um diretório à base."""
        if not self._current_base:
            return

        directory = QFileDialog.getExistingDirectory(
            self,
            "Selecionar Diretório",
            str(Path.home()),
            QFileDialog.ShowDirsOnly,
        )

        if directory:
            dialog = AddDirectoryDialog(self)
            if dialog.exec():
                pattern = dialog.pattern_edit.text()
                recursive = dialog.recursive_check.isChecked()
                self.add_directory_requested.emit(
                    self._current_base, Path(directory), pattern, recursive
                )


class CreateBaseDialog(QWidget):
    """Diálogo para criar uma nova base de conhecimento."""

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Inicializa o diálogo.

        Args:
            parent: Widget pai (opcional)
        """
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Configura a interface do usuário."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Campo de nome
        layout.addWidget(QLabel("Nome:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)

        # Campo de descrição
        layout.addWidget(QLabel("Descrição:"))
        self.description_edit = QTextEdit()
        layout.addWidget(self.description_edit)

        # Botões
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def exec(self) -> bool:
        """
        Executa o diálogo.

        Returns:
            True se o usuário clicou em OK, False caso contrário
        """
        return QMessageBox.exec(self) == QMessageBox.Ok


class AddDirectoryDialog(QWidget):
    """Diálogo para adicionar um diretório à base."""

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Inicializa o diálogo.

        Args:
            parent: Widget pai (opcional)
        """
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Configura a interface do usuário."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Campo de padrão
        layout.addWidget(QLabel("Padrão de arquivos (ex: *.txt):"))
        self.pattern_edit = QLineEdit()
        self.pattern_edit.setText("*")
        layout.addWidget(self.pattern_edit)

        # Checkbox recursivo
        self.recursive_check = QCheckBox("Incluir subdiretórios")
        self.recursive_check.setChecked(True)
        layout.addWidget(self.recursive_check)

        # Botões
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def exec(self) -> bool:
        """
        Executa o diálogo.

        Returns:
            True se o usuário clicou em OK, False caso contrário
        """
        return QMessageBox.exec(self) == QMessageBox.Ok
