"""
Controlador principal da aplicação UCAN.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

from PySide6.QtCore import QObject, Signal

from ucan.config.settings import settings
from ucan.core.assistant import Assistant
from ucan.core.conversation import Conversation
from ucan.core.conversation_type import ConversationType
from ucan.core.database import db
from ucan.core.knowledge_base import KnowledgeBase
from ucan.core.knowledge_manager import KnowledgeManager
from ucan.core.llm_interface import LLMInterface, MockLLMInterface
from ucan.core.message import Message
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
    conversation_selected = Signal(Conversation)
    conversations_updated = Signal(list)
    message_sent = Signal(Message)
    knowledge_base_created = Signal(KnowledgeBase)
    knowledge_base_updated = Signal(KnowledgeBase)
    knowledge_bases_updated = Signal(list)
    conversation_type_created = Signal(ConversationType)

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
        self.assistant = Assistant()
        self._setup_directories()

    def _setup_directories(self) -> None:
        """Configura os diretórios necessários."""
        try:
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

        # Fechar conexão com o banco de dados
        try:
            db.close()
            logger.debug("Conexão com o banco de dados encerrada")
        except Exception as e:
            logger.error(f"Erro ao fechar conexão com o banco de dados: {e}")

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

    def get_conversations(self) -> List[Conversation]:
        """
        Obtém todas as conversas.

        Returns:
            Lista de conversas
        """
        conversations = Conversation.get_all()
        self.conversations_updated.emit(conversations)
        return conversations

    def select_conversation(self, conversation: Conversation) -> None:
        """
        Seleciona uma conversa.

        Args:
            conversation: Conversa a ser selecionada
        """
        self.current_conversation = conversation
        self.conversation_selected.emit(conversation)
        self.get_conversation_knowledge_bases()

    def new_conversation(
        self, title: Optional[str] = None, type_id: Optional[str] = None
    ) -> Conversation:
        """
        Cria uma nova conversa.

        Args:
            title: Título da conversa (opcional)
            type_id: ID do tipo de conversa (opcional)

        Returns:
            Nova conversa
        """
        conversation = Conversation(
            title=title or "Nova Conversa",
            type_id=type_id,
        )
        self.select_conversation(conversation)
        self.get_conversations()
        return conversation

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

        # Atualiza a conversa no banco
        self.current_conversation.save()
        self.conversation_updated.emit(self.current_conversation)

    def _save_conversation(self, conversation: Conversation) -> None:
        """
        Salva uma conversa.

        Args:
            conversation: Conversa a ser salva
        """
        try:
            db.save_conversation(
                conversation.id, conversation.title, conversation.metadata
            )
            self.conversation_updated.emit(conversation)
        except Exception as e:
            logger.error("Erro ao salvar conversa: %s", e)

    def _save_message(self, message: Message) -> None:
        """
        Salva uma mensagem.

        Args:
            message: Mensagem a ser salva
        """
        try:
            db.save_message(
                message.id,
                self.current_conversation.id,
                message.role,
                message.content,
                message.metadata,
            )
        except Exception as e:
            logger.error("Erro ao salvar mensagem: %s", e)

    def save_state(self) -> None:
        """Salva o estado da aplicação antes de fechar."""
        try:
            # We don't need to save anything here as all state is saved in real-time
            logger.info("Estado da aplicação salvo com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar estado da aplicação: {e}")
            raise

    def export_conversation(self, file_path: Path) -> bool:
        """
        Exporta a conversa atual para um arquivo.

        Args:
            file_path: Caminho do arquivo

        Returns:
            True se a exportação foi bem sucedida, False caso contrário
        """
        if not self.current_conversation:
            return False

        try:
            self.current_conversation.export_to_file(file_path)
            return True
        except Exception as e:
            logger.error("Erro ao exportar conversa: %s", e)
            return False

    def import_conversation(self, file_path: Path) -> Optional[str]:
        """
        Importa uma conversa de um arquivo.

        Args:
            file_path: Caminho do arquivo

        Returns:
            ID da conversa importada ou None se falhar
        """
        try:
            conversation = Conversation.import_from_file(file_path)
            self.get_conversations()
            return conversation.id
        except Exception as e:
            logger.error("Erro ao importar conversa: %s", e)
            return None

    def get_conversation_types(self) -> List[ConversationType]:
        """
        Obtém todos os tipos de conversação disponíveis.

        Returns:
            Lista de tipos de conversação
        """
        return ConversationType.get_all()

    def create_conversation_type(
        self, name: str, description: str, metadata: Optional[Dict] = None
    ) -> ConversationType:
        """
        Cria um novo tipo de conversação.

        Args:
            name: Nome do tipo
            description: Descrição do tipo
            metadata: Metadados adicionais (opcional)

        Returns:
            Tipo de conversação criado
        """
        conv_type = ConversationType(
            name=name, description=description, metadata=metadata
        )
        self.conversation_type_created.emit(conv_type)
        return conv_type

    def create_knowledge_base(
        self,
        name: str,
        description: str,
        scope: str,
        metadata: Optional[Dict] = None,
    ) -> Optional[KnowledgeBase]:
        """
        Cria uma nova base de conhecimento.

        Args:
            name: Nome da base
            description: Descrição da base
            scope: Escopo da base (global, type ou conversation)
            metadata: Metadados adicionais (opcional)

        Returns:
            Base de conhecimento criada ou None se falhar
        """
        if scope == "global":
            base = KnowledgeManager.create_global_base(name, description, metadata)
        elif scope == "type":
            if not self.current_conversation or not self.current_conversation.type_id:
                return None
            type_ = self.current_conversation.get_type()
            base = type_.create_knowledge_base(name, description, metadata)
        elif scope == "conversation":
            if not self.current_conversation:
                return None
            base = self.current_conversation.create_knowledge_base(
                name, description, metadata
            )
        else:
            return None

        self.knowledge_base_created.emit(base)
        return base

    def get_global_knowledge_bases(self) -> List[KnowledgeBase]:
        """
        Obtém todas as bases de conhecimento globais.

        Returns:
            Lista de bases de conhecimento globais
        """
        bases = KnowledgeManager.get_global_bases()
        self.knowledge_bases_updated.emit(bases)
        return bases

    def add_files_to_knowledge_base(
        self,
        base: KnowledgeBase,
        files: List[Path],
        metadata: Optional[Dict] = None,
    ) -> List[str]:
        """
        Adiciona múltiplos arquivos a uma base de conhecimento.

        Args:
            base: Base de conhecimento
            files: Lista de caminhos de arquivos
            metadata: Metadados adicionais (opcional)

        Returns:
            Lista de IDs dos itens criados
        """
        item_ids = KnowledgeManager.add_files_to_base(base, files, metadata)
        self.knowledge_base_updated.emit(base)
        return item_ids

    def add_directory_to_knowledge_base(
        self,
        base: KnowledgeBase,
        directory: Path,
        pattern: str = "*",
        recursive: bool = True,
        metadata: Optional[Dict] = None,
    ) -> List[str]:
        """
        Adiciona todos os arquivos de um diretório a uma base de conhecimento.

        Args:
            base: Base de conhecimento
            directory: Caminho do diretório
            pattern: Padrão para filtrar arquivos (ex: "*.txt")
            recursive: Se deve incluir subdiretórios
            metadata: Metadados adicionais (opcional)

        Returns:
            Lista de IDs dos itens criados
        """
        item_ids = KnowledgeManager.add_directory_to_base(
            base, directory, pattern, recursive, metadata
        )
        self.knowledge_base_updated.emit(base)
        return item_ids

    def get_conversation_knowledge_bases(self) -> List[KnowledgeBase]:
        """
        Obtém todas as bases de conhecimento relevantes para a conversa atual.
        Inclui bases globais, bases do tipo da conversa e bases específicas da conversa.

        Returns:
            Lista de bases de conhecimento
        """
        if not self.current_conversation:
            return []

        bases = self.current_conversation.get_knowledge_bases()
        self.knowledge_bases_updated.emit(bases)
        self.assistant.set_knowledge_bases(bases)
        return bases

    def create_conversation_knowledge_base(
        self, name: str, description: str, metadata: Optional[Dict] = None
    ) -> Optional[KnowledgeBase]:
        """
        Cria uma nova base de conhecimento para a conversa atual.

        Args:
            name: Nome da base
            description: Descrição da base
            metadata: Metadados adicionais (opcional)

        Returns:
            Base de conhecimento criada ou None se não houver conversa atual
        """
        if not self.current_conversation:
            return None

        base = self.current_conversation.create_knowledge_base(
            name, description, metadata
        )
        self.knowledge_base_created.emit(base)
        return base
