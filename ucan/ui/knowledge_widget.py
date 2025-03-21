import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QPixmap, QVBoxLayout, QWidget


class KnowledgeWidget:
    def _setup_empty_state(self):
        """Configura o estado vazio quando não há bases de conhecimento."""
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setContentsMargins(16, 24, 16, 24)

        # Ícone para o estado vazio
        icon_label = QLabel()
        icon_label.setObjectName("emptyKnowledgeIcon")
        icon_path = os.path.join(
            os.path.dirname(__file__), "../resources/icons/book-open.svg"
        )
        icon_pixmap = QPixmap(icon_path)
        if not icon_pixmap.isNull():
            icon_label.setPixmap(
                icon_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )

        # Texto principal
        text_label = QLabel("Sem bases de conhecimento")
        text_label.setObjectName("emptyKnowledgeText")

        # Texto informativo
        info_label = QLabel(
            "Adicione conteúdos para melhorar as respostas do assistente com conhecimentos específicos."
        )
        info_label.setObjectName("emptyKnowledgeSubtext")
        info_label.setWordWrap(True)

        # Criar placeholder para importar conteúdo
        placeholder1 = self._create_knowledge_placeholder(
            "Importar arquivo",
            "Adicione PDFs, documentação técnica ou outros arquivos",
            "import.svg",
        )

        # Criar placeholder para criar nova base
        placeholder2 = self._create_knowledge_placeholder(
            "Nova base de conhecimento",
            "Crie uma base vazia para adicionar conteúdo manualmente",
            "folder-plus.svg",
        )

        empty_layout.addWidget(icon_label, 0, Qt.AlignCenter)
        empty_layout.addWidget(text_label, 0, Qt.AlignCenter)
        empty_layout.addWidget(info_label, 0, Qt.AlignCenter)
        empty_layout.addSpacing(16)
        empty_layout.addWidget(placeholder1)
        empty_layout.addWidget(placeholder2)
        empty_layout.addStretch()

        # Adicionar ao layout principal
        self.main_layout.addWidget(empty_widget)
        self.empty_state_widget = empty_widget

    def _create_knowledge_placeholder(self, title, description, icon_name):
        """Cria um placeholder para adição de base de conhecimento."""
        placeholder = QWidget()
        placeholder.setObjectName("knowledgePlaceholder")
        placeholder.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(placeholder)
        layout.setContentsMargins(12, 12, 12, 12)

        # Adicionar classe CSS para estilização
        placeholder.setProperty("class", "knowledge-placeholder")

        # Ícone
        icon_label = QLabel()
        icon_label.setProperty("class", "knowledge-placeholder-icon")
        icon_path = os.path.join(
            os.path.dirname(__file__), f"../resources/icons/{icon_name}"
        )
        icon_pixmap = QPixmap(icon_path)
        if not icon_pixmap.isNull():
            icon_label.setPixmap(
                icon_pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )

        # Título
        title_label = QLabel(title)
        title_label.setProperty("class", "knowledge-placeholder-title")
        title_label.setStyleSheet("font-weight: 600; color: #E4E6EB; font-size: 14px;")

        # Descrição
        desc_label = QLabel(description)
        desc_label.setProperty("class", "knowledge-placeholder-text")
        desc_label.setWordWrap(True)

        layout.addWidget(icon_label, 0, Qt.AlignCenter)
        layout.addWidget(title_label, 0, Qt.AlignCenter)
        layout.addWidget(desc_label, 0, Qt.AlignCenter)

        return placeholder
