"""
Módulo de gerenciamento de conversas.
"""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ucan.core.database import db
from ucan.core.knowledge_base import KnowledgeBase
from ucan.core.models import Message

logger = logging.getLogger(__name__)


class Conversation:
    """Representa uma conversa entre o usuário e o assistente."""

    def __init__(
        self,
        title: Optional[str] = None,
        id: Optional[str] = None,
        type_id: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        meta_data: Optional[Dict] = None,
    ) -> None:
        """
        Inicializa uma nova conversa.

        Args:
            title: Título da conversa
            id: ID da conversa (opcional)
            type_id: ID do tipo da conversa (opcional)
            created_at: Data de criação (opcional)
            updated_at: Data de atualização (opcional)
            meta_data: Metadados adicionais (opcional)
        """
        self.id = id or str(uuid.uuid4())
        self.title = title or "Nova Conversa"
        self.type_id = type_id
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or self.created_at
        self.meta_data = meta_data or {}
        self.messages: List[Message] = []

        # Se um ID foi fornecido, tenta carregar do banco
        if id:
            self._load_from_db()

    def _load_from_db(self) -> None:
        """Carrega os dados da conversa do banco de dados."""
        try:
            # Carrega dados da conversa
            conversation_data = db.get_conversation(self.id)
            if conversation_data:
                self.title = conversation_data["title"]
                self.type_id = conversation_data.get("type_id")
                self.created_at = conversation_data["created_at"].isoformat()
                self.updated_at = conversation_data["updated_at"].isoformat()
                self.meta_data = conversation_data["meta_data"]

                # Carrega mensagens
                messages_data = db.get_messages(self.id)
                self.messages = []
                for msg in messages_data:
                    self.messages.append(
                        Message(
                            id=msg["id"],
                            role=msg["role"],
                            content=msg["content"],
                            created_at=msg["created_at"].isoformat(),
                            meta_data=msg["meta_data"],
                        )
                    )
        except Exception as e:
            logger.error(f"Erro ao carregar conversa do banco: {e}")

    def add_message(
        self,
        role: str,
        content: str,
        id: Optional[str] = None,
        created_at: Optional[str] = None,
        meta_data: Optional[Dict] = None,
    ) -> Message:
        """
        Adiciona uma mensagem à conversa.

        Args:
            role: Papel do remetente (user, assistant, system)
            content: Conteúdo da mensagem
            id: ID da mensagem (opcional)
            created_at: Data de criação (opcional)
            meta_data: Metadados adicionais (opcional)

        Returns:
            Mensagem adicionada
        """
        message = Message(
            id=id or str(uuid.uuid4()),
            role=role,
            content=content,
            created_at=created_at or datetime.utcnow().isoformat(),
            meta_data=meta_data or {},
        )
        self.messages.append(message)
        self.updated_at = datetime.utcnow().isoformat()

        # Salva a mensagem no banco
        try:
            db.save_message(
                message.id,
                self.id,
                message.role,
                message.content,
                message.meta_data,
            )
        except Exception as e:
            logger.error(f"Erro ao salvar mensagem no banco: {e}")

        return message

    def save(self) -> bool:
        """
        Salva a conversa no banco de dados.

        Returns:
            True se a operação foi bem sucedida, False caso contrário
        """
        try:
            db.save_conversation(self.id, self.title, self.meta_data)
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar conversa no banco: {e}")
            return False

    def get_knowledge_bases(self) -> List[KnowledgeBase]:
        """
        Obtém todas as bases de conhecimento disponíveis para esta conversa.

        Returns:
            Lista de bases de conhecimento
        """
        bases = []

        # Bases globais
        bases.extend(KnowledgeBase.get_global_bases())

        # Bases do tipo da conversa
        if self.type_id:
            bases.extend(KnowledgeBase.get_type_bases(self.type_id))

        # Bases específicas da conversa
        bases.extend(KnowledgeBase.get_conversation_bases(self.id))

        return bases

    def create_knowledge_base(
        self, name: str, description: str, meta_data: Optional[Dict] = None
    ) -> KnowledgeBase:
        """
        Cria uma nova base de conhecimento para esta conversa.

        Args:
            name: Nome da base
            description: Descrição da base
            meta_data: Metadados adicionais (opcional)

        Returns:
            Base de conhecimento criada
        """
        return KnowledgeBase(
            name=name,
            description=description,
            scope="conversation",
            conversation_id=self.id,
            meta_data=meta_data,
        )

    def to_dict(self) -> Dict:
        """
        Converte a conversa para um dicionário.

        Returns:
            Dicionário com os dados da conversa
        """
        return {
            "id": self.id,
            "title": self.title,
            "type_id": self.type_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "meta_data": self.meta_data,
            "messages": [message.to_dict() for message in self.messages],
        }

    def export(self, file_path: Path) -> bool:
        """
        Exporta a conversa para um arquivo.

        Args:
            file_path: Caminho do arquivo

        Returns:
            True se a exportação foi bem sucedida, False caso contrário
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Erro ao exportar conversa: {e}")
            return False

    @classmethod
    def import_from_file(cls, file_path: Path) -> Optional["Conversation"]:
        """
        Importa uma conversa de um arquivo.

        Args:
            file_path: Caminho do arquivo

        Returns:
            Conversa importada ou None se falhou
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            conversation = cls(
                title=data.get("title"),
                id=data.get("id"),
                type_id=data.get("type_id"),
                created_at=data.get("created_at"),
                updated_at=data.get("updated_at"),
                meta_data=data.get("meta_data", {}),
            )

            for message_data in data.get("messages", []):
                conversation.add_message(
                    role=message_data["role"],
                    content=message_data["content"],
                    id=message_data.get("id"),
                    created_at=message_data.get("created_at"),
                    meta_data=message_data.get("meta_data", {}),
                )

            return conversation
        except Exception as e:
            logger.error(f"Erro ao importar conversa: {e}")
            return None

    @classmethod
    def load(cls, conversation_id: str) -> Optional["Conversation"]:
        """
        Carrega uma conversa do banco de dados.

        Args:
            conversation_id: ID da conversa

        Returns:
            Conversa carregada ou None se não encontrada
        """
        try:
            return cls(id=conversation_id)
        except Exception as e:
            logger.error(f"Erro ao carregar conversa: {e}")
            return None

    @classmethod
    def get_all(cls) -> List["Conversation"]:
        """
        Obtém todas as conversas.

        Returns:
            Lista de conversas
        """
        try:
            results = db.conn.execute(
                """
                SELECT id, title, type_id, created_at, updated_at, meta_data
                FROM conversations
                ORDER BY updated_at DESC
                """
            ).fetchall()

            return [
                cls(
                    title=row[1],
                    id=row[0],
                    type_id=row[2],
                    created_at=row[3].isoformat(),
                    updated_at=row[4].isoformat(),
                    meta_data=json.loads(row[5]),
                )
                for row in results
            ]
        except Exception as e:
            logger.error(f"Erro ao obter conversas: {e}")
            return []

    def get_messages(self) -> List[Message]:
        """
        Obtém todas as mensagens da conversa.

        Returns:
            Lista de mensagens
        """
        return self.messages
