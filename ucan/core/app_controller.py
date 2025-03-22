"""
Controlador principal da aplicação UCAN.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional

from ucan.config.settings import settings
from ucan.core.assistant import Assistant
from ucan.core.conversation import Conversation
from ucan.core.conversation_type import ConversationType
from ucan.core.database import db
from ucan.core.knowledge_base import KnowledgeBase
from ucan.core.knowledge_manager import KnowledgeManager
from ucan.core.llm_interface import LLMInterface, get_llm_interface
from ucan.core.models import Message
from ucan.utils.file_watcher import FileWatcher

logger = logging.getLogger(__name__)


class EventEmitter:
    """Simple event emitter implementation."""

    def __init__(self):
        self._events = {}

    def on(self, event: str, callback: Callable):
        """Register an event callback."""
        if event not in self._events:
            self._events[event] = []
        self._events[event].append(callback)

    def emit(self, event: str, *args, **kwargs):
        """Emit an event with arguments."""
        if event in self._events:
            for callback in self._events[event]:
                callback(*args, **kwargs)


class AppController(EventEmitter):
    """Controlador principal da aplicação."""

    def __init__(self, language_model_interface: Optional[LLMInterface] = None) -> None:
        """
        Inicializa o controlador.

        Args:
            language_model_interface: Interface com o modelo de linguagem
        """
        super().__init__()

        # Se não foi fornecida uma interface, cria uma com base nas configurações
        if not language_model_interface:
            language_model_interface = get_llm_interface()

        self.llm = language_model_interface
        self.assistant = Assistant(self.llm)
        self.current_conversation = None
        self.conversations = []
        self.knowledge_manager = KnowledgeManager()
        self._setup_directories()
        self._setup_hot_reload()

    def _setup_directories(self) -> None:
        """Configura os diretórios necessários."""
        try:
            os.makedirs(settings.CACHE_DIR, exist_ok=True)
            os.makedirs(settings.LOG_DIR, exist_ok=True)
        except Exception as e:
            logger.error(f"Erro ao configurar diretórios: {e}")
            self.emit("initialization_failed", str(e))

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
            self.emit("initialization_failed", f"Erro ao configurar hot reload: {e}")

    def _on_file_changed(self, file_path: str) -> None:
        """
        Chamado quando um arquivo é modificado.

        Args:
            file_path: Caminho do arquivo modificado
        """
        logger.debug(f"Arquivo modificado: {file_path}")

        # Se for um arquivo CSS, recarrega os estilos
        if file_path.endswith((".css", ".qss")):
            from ucan.ui.theme_manager import theme_manager

            if theme_manager:
                theme_manager._reload_current_theme()
                logger.debug("Estilos recarregados após modificação")

        self.emit("hot_reload_requested")

    async def initialize(self) -> None:
        """Initialize the application controller."""
        logger.info("Iniciando controlador da aplicação...")
        # Carregar conversas iniciais
        self.refresh_conversation_list()
        # Se não houver conversa atual, criar uma nova
        if not self.current_conversation:
            self.new_conversation()

    async def shutdown(self) -> None:
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

    async def __del__(self):
        """Ensure cleanup on deletion."""
        await self.shutdown()

    def refresh_conversation_list(self) -> None:
        """Atualiza a lista de conversas e emite o sinal conversations_loaded."""
        try:
            conversations = self.get_conversations()
            self.emit("conversations_loaded", conversations)
        except Exception as e:
            logger.error(f"Erro ao atualizar lista de conversas: {e}")

    def get_conversations(self) -> List[Conversation]:
        """
        Obtém todas as conversas.

        Returns:
            Lista de conversas
        """
        return self.conversations

    def select_conversation(self, conversation: Conversation) -> None:
        """
        Seleciona uma conversa.

        Args:
            conversation: Conversa a ser selecionada
        """
        self.current_conversation = conversation
        self.emit("conversation_selected", conversation)
        self.get_conversation_knowledge_bases()

    def new_conversation(
        self, title: Optional[str] = None, type_id: Optional[str] = None
    ) -> Conversation:
        """
        Cria uma nova conversa.

        Args:
            title: Título da conversa
            type_id: ID do tipo de conversa

        Returns:
            Nova conversa
        """
        title = title or "Nova Conversa"
        type_name = None
        meta_data = {}

        # Se um tipo foi especificado, buscar informações
        if type_id:
            conv_type = self.get_conversation_type(type_id)
            if conv_type:
                type_name = conv_type.name
                meta_data = conv_type.meta_data or {}

        # Criar nova conversa
        conversation = Conversation.create(
            title=title,
            type_id=type_id,
            type_name=type_name,
            meta_data=meta_data,
        )

        # Adicionar à lista e selecionar
        self.conversations.append(conversation)
        self.current_conversation = conversation
        self.emit("conversation_created", conversation)
        return conversation

    async def send_message(self, message: str) -> None:
        """
        Envia uma mensagem para o assistente.

        Args:
            message: Conteúdo da mensagem
        """
        if not self.current_conversation:
            raise RuntimeError("Nenhuma conversa selecionada")

        # Criar e adicionar mensagem do usuário
        user_message = Message(content=message, role="user", meta_data={})
        self.current_conversation.messages.append(user_message)
        self.emit("message_received", user_message)

        try:
            # Gerar resposta do assistente
            response = await self.llm.generate_response(message)
            assistant_message = Message(
                content=response, role="assistant", meta_data={}
            )
            self.current_conversation.messages.append(assistant_message)
            self.emit("message_received", assistant_message)
        except Exception as e:
            logger.error("Erro ao gerar resposta: %s", e)
            error_message = Message(
                content=f"Erro ao gerar resposta: {e}", role="system", meta_data={}
            )
            self.current_conversation.messages.append(error_message)
            self.emit("message_received", error_message)

        # Atualiza a conversa no banco
        self.current_conversation.updated_at = datetime.now()
        self._save_conversation(self.current_conversation)
        self.emit("conversation_updated", self.current_conversation)

    def _save_conversation(self, conversation: Conversation) -> None:
        """
        Salva uma conversa.

        Args:
            conversation: Conversa a ser salva
        """
        try:
            # Salva a conversa
            db.save_conversation(
                conversation.id,
                conversation.title,
                conversation.messages[-1].content if conversation.messages else "",
            )

            # Salva todas as mensagens da conversa
            for message in conversation.messages:
                if not hasattr(
                    message, "_saved"
                ):  # Evita salvar a mesma mensagem múltiplas vezes
                    db.save_message(
                        message.id,
                        conversation.id,
                        message.role,
                        message.content,
                        message.meta_data or {},
                    )
                    setattr(message, "_saved", True)

            self.emit("conversation_updated", conversation)
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
        self.emit("conversation_type_created", conv_type)
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

        self.emit("knowledge_base_created", base)
        return base

    def get_global_knowledge_bases(self) -> List[KnowledgeBase]:
        """
        Obtém todas as bases de conhecimento globais.

        Returns:
            Lista de bases de conhecimento globais
        """
        bases = KnowledgeManager.get_global_bases()
        self.emit("knowledge_bases_updated", bases)
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
        self.emit("knowledge_base_updated", base)
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
        self.emit("knowledge_base_updated", base)
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
        self.emit("knowledge_bases_updated", bases)
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
        self.emit("knowledge_base_created", base)
        return base

    def _create_initial_conversation(self):
        """Cria a conversa inicial."""
        conversation = Conversation.create("Nova Conversa")
        self.conversations.append(conversation)
        self.current_conversation = conversation

    def get_current_conversation(self) -> Optional[Conversation]:
        """
        Obtém a conversa atual.

        Returns:
            Conversa atual ou None se nenhuma selecionada
        """
        return self.current_conversation

    def get_conversation_type(self, type_id: str) -> Optional[ConversationType]:
        """
        Obtém um tipo de conversa pelo ID.

        Args:
            type_id: ID do tipo de conversa

        Returns:
            Tipo de conversa ou None se não encontrado
        """
        try:
            with db.get_session() as session:
                return session.query(ConversationType).filter_by(id=type_id).first()
        except Exception as e:
            logger.error(f"Erro ao buscar tipo de conversa: {e}")
            return None
