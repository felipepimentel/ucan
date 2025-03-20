"""
Controlador principal da aplicação UCAN.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, Signal

from ucan.config.settings import settings
from ucan.core.conversation import Conversation
from ucan.core.llm_interface import LLMInterface, MockLLMInterface
from ucan.core.models import Message
from ucan.utils.file_watcher import FileWatcher

logger = logging.getLogger(__name__)


class AppController(QObject):
    """Controlador principal da aplicação."""

    message_received = Signal(Message)
    hot_reload_requested = Signal()
    initialization_failed = Signal(str)
    conversation_created = Signal(Conversation)
    conversation_deleted = Signal(str)
    conversation_updated = Signal(Conversation)
    conversations_loaded = Signal(list)
    conversation_added = Signal(Conversation)
    error_occurred = Signal(str)
    status_message = Signal(str)

    def __init__(self, language_model_interface: Optional[LLMInterface] = None) -> None:
        """
        Inicializa o controlador.

        Args:
            language_model_interface: Interface com o modelo de linguagem
        """
        super().__init__()
        self.llm = (
            language_model_interface
            if language_model_interface is not None
            else MockLLMInterface()
        )
        self.current_conversation: Optional[Conversation] = None
        self._file_watcher = None
        self._setup_directories()

    def _setup_directories(self) -> None:
        """Configura os diretórios necessários."""
        try:
            os.makedirs(settings.CONVERSATIONS_DIR, exist_ok=True)
            os.makedirs(settings.CACHE_DIR, exist_ok=True)
            os.makedirs(settings.LOG_DIR, exist_ok=True)
        except Exception as e:
            logger.error(f"Erro ao configurar diretórios: {e}")
            self.initialization_failed.emit(str(e))

    def _setup_hot_reload(self) -> None:
        """Set up the hot reload system."""
        try:
            project_root = Path(__file__).parent.parent.parent
            logger.debug(f"Configurando hot reload para o diretório: {project_root}")

            # Criar e configurar o observador de arquivos
            self._file_watcher = FileWatcher(project_root)
            self._file_watcher.file_changed.connect(self._on_file_changed)
            self._file_watcher.start()

            logger.info("Sistema de hot reload configurado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao configurar hot reload: {e}")
            self.initialization_failed.emit(f"Erro ao configurar hot reload: {e}")

    def _on_file_changed(self, file_path: str) -> None:
        """
        Chamado quando um arquivo é modificado.

        Args:
            file_path: Caminho do arquivo modificado
        """
        logger.debug(f"Arquivo modificado: {file_path}")
        self.hot_reload_requested.emit()

    async def initialize(self) -> None:
        """Initialize the application controller."""
        logger.info("Iniciando controlador da aplicação...")
        self._setup_hot_reload()
        # Carregar conversas iniciais
        self.refresh_conversation_list()
        # Se não houver conversa atual, criar uma nova
        if not self.current_conversation:
            self.new_conversation()

    def shutdown(self) -> None:
        """Clean shutdown of the application."""
        logger.info("Iniciando encerramento do controlador...")

        # Cleanup hot reload
        if self._file_watcher:
            try:
                self._file_watcher.stop()
                logger.debug("Sistema de hot reload encerrado")
            except Exception as e:
                logger.error(f"Erro ao encerrar hot reload: {e}")

        # Add any other cleanup needed here

        logger.info("Controlador encerrado com sucesso")

    def __del__(self):
        """Ensure cleanup on deletion."""
        self.shutdown()

    def refresh_conversation_list(self) -> None:
        """Atualiza a lista de conversas e emite o sinal conversations_loaded."""
        try:
            conversations = self.get_conversations()
            self.conversations_loaded.emit(conversations)
        except Exception as e:
            logger.error(f"Erro ao atualizar lista de conversas: {e}")

    def get_conversations(self) -> list[Conversation]:
        """
        Obtém a lista de conversas.

        Returns:
            Lista de conversas carregadas
        """
        conversations_dir = settings.CONVERSATIONS_DIR
        conversations_dir.mkdir(exist_ok=True)

        conversations = []
        for file_path in conversations_dir.glob("*.json"):
            try:
                conversation = Conversation.import_from_file(file_path)
                if conversation:
                    conversations.append(conversation)
            except Exception as e:
                logger.error("Erro ao carregar conversa %s: %s", file_path, e)

        return sorted(conversations, key=lambda c: c.updated_at, reverse=True)

    def select_conversation(self, conversation: Conversation) -> None:
        """
        Seleciona uma conversa.

        Args:
            conversation: Conversa a ser selecionada
        """
        self.current_conversation = conversation
        self.conversation_updated.emit(conversation)

    def new_conversation(self, title: Optional[str] = None) -> None:
        """
        Cria uma nova conversa.

        Args:
            title: Título da conversa (opcional)
        """
        if title is None:
            title = f"Nova Conversa ({datetime.now().strftime('%d/%m/%Y %H:%M')})"

        conversation = Conversation(title=title)
        self.current_conversation = conversation
        self._save_conversation(conversation)
        self.conversation_created.emit(conversation)
        self.refresh_conversation_list()

    async def send_message(self, content: str) -> None:
        """
        Envia uma mensagem para o assistente.

        Args:
            content: Conteúdo da mensagem
        """
        if not self.current_conversation:
            raise RuntimeError("Nenhuma conversa selecionada")

        user_message = self.current_conversation.add_message("user", content)
        self.message_received.emit(user_message)

        try:
            response = await self.llm.generate_response(content)
            assistant_message = self.current_conversation.add_message(
                "assistant", response
            )
            self.message_received.emit(assistant_message)
        except Exception as e:
            logger.error("Erro ao gerar resposta: %s", e)
            error_message = self.current_conversation.add_message(
                "system", f"Erro ao gerar resposta: {e}"
            )
            self.message_received.emit(error_message)

        self._save_conversation(self.current_conversation)

    def _save_conversation(self, conversation: Conversation) -> None:
        """
        Salva uma conversa.

        Args:
            conversation: Conversa a ser salva
        """
        try:
            file_path = conversation.save()
            self.conversation_updated.emit(conversation)
        except Exception as e:
            logger.error("Erro ao salvar conversa: %s", e)

    def export_conversation(self, export_path: Path) -> bool:
        """
        Exporta a conversa atual.

        Args:
            export_path: Caminho para exportar a conversa

        Returns:
            True se a exportação foi bem sucedida, False caso contrário
        """
        if not self.current_conversation:
            return False

        return self.current_conversation.export(export_path)

    def import_conversation(self, import_path: Path) -> Optional[str]:
        """
        Importa uma conversa.

        Args:
            import_path: Caminho do arquivo a ser importado

        Returns:
            ID da conversa importada ou None se falhou
        """
        try:
            conversation = Conversation.import_from_file(import_path)
            if conversation:
                self._save_conversation(conversation)
                self.conversation_created.emit(conversation)
                return conversation.id
            return None
        except Exception as e:
            logger.error("Erro ao importar conversa: %s", e)
            return None

    def save_state(self) -> None:
        """Salva o estado da aplicação antes de fechar."""
        try:
            if self.current_conversation:
                self._save_conversation(self.current_conversation)
            logger.info("Estado da aplicação salvo com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar estado da aplicação: {e}")
            raise
