"""
Módulo de gerenciamento de bases de conhecimento.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

from ucan.core.database import db

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """Gerenciador de bases de conhecimento."""

    def __init__(
        self,
        name: str,
        description: str,
        scope: str = "global",
        type_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        id: Optional[str] = None,
        meta_data: Optional[Dict] = None,
    ) -> None:
        """
        Inicializa uma base de conhecimento.

        Args:
            name: Nome da base
            description: Descrição da base
            scope: Escopo ('global', 'type', 'conversation')
            type_id: ID do tipo de conversa (opcional)
            conversation_id: ID da conversa (opcional)
            id: ID da base (opcional)
            meta_data: Metadados adicionais (opcional)
        """
        self.name = name
        self.description = description
        self.scope = scope
        self.type_id = type_id
        self.conversation_id = conversation_id
        self.meta_data = meta_data or {}
        self.id = id

        if not self.id:
            self.id = self._create()

    def _create(self) -> str:
        """
        Cria a base de conhecimento no banco de dados.

        Returns:
            ID da base criada
        """
        return db.create_knowledge_base(
            self.name,
            self.description,
            self.scope,
            self.type_id,
            self.conversation_id,
            self.meta_data,
        )

    def add_file(
        self, file_path: Union[str, Path], meta_data: Optional[Dict] = None
    ) -> str:
        """
        Adiciona um arquivo à base de conhecimento.

        Args:
            file_path: Caminho do arquivo
            meta_data: Metadados adicionais (opcional)

        Returns:
            ID do item criado
        """
        file_path = Path(file_path)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            return db.add_knowledge_item(
                self.id,
                file_path.name,
                file_path.suffix.lstrip("."),
                content,
                meta_data=meta_data,
            )
        except Exception as e:
            logger.error(f"Erro ao adicionar arquivo {file_path}: {e}")
            raise

    def add_content(
        self,
        content: str,
        file_name: str,
        file_type: str,
        meta_data: Optional[Dict] = None,
    ) -> str:
        """
        Adiciona conteúdo diretamente à base de conhecimento.

        Args:
            content: Conteúdo a ser adicionado
            file_name: Nome do arquivo
            file_type: Tipo do arquivo
            meta_data: Metadados adicionais (opcional)

        Returns:
            ID do item criado
        """
        try:
            return db.add_knowledge_item(
                self.id,
                file_name,
                file_type,
                content,
                meta_data=meta_data,
            )
        except Exception as e:
            logger.error(f"Erro ao adicionar conteúdo: {e}")
            raise

    def get_items(self, with_embeddings: bool = False) -> List[Dict]:
        """
        Obtém os itens da base de conhecimento.

        Args:
            with_embeddings: Se deve incluir os vetores de embedding

        Returns:
            Lista de itens
        """
        return db.get_knowledge_items(self.id, with_embeddings)

    @classmethod
    def get_bases(
        cls,
        scope: Optional[str] = None,
        type_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> List["KnowledgeBase"]:
        """
        Obtém bases de conhecimento com filtros opcionais.

        Args:
            scope: Filtrar por escopo
            type_id: Filtrar por tipo de conversa
            conversation_id: Filtrar por conversa

        Returns:
            Lista de bases de conhecimento
        """
        bases_data = db.get_knowledge_bases(scope, type_id, conversation_id)
        return [
            cls(
                name=data["name"],
                description=data["description"],
                scope=data["scope"],
                type_id=data["type_id"],
                conversation_id=data["conversation_id"],
                id=data["id"],
                meta_data=data["meta_data"],
            )
            for data in bases_data
        ]

    @classmethod
    def get_global_bases(cls) -> List["KnowledgeBase"]:
        """
        Obtém todas as bases de conhecimento globais.

        Returns:
            Lista de bases de conhecimento globais
        """
        return cls.get_bases(scope="global")

    @classmethod
    def get_type_bases(cls, type_id: str) -> List["KnowledgeBase"]:
        """
        Obtém bases de conhecimento de um tipo específico.

        Args:
            type_id: ID do tipo de conversa

        Returns:
            Lista de bases de conhecimento do tipo
        """
        return cls.get_bases(scope="type", type_id=type_id)

    @classmethod
    def get_conversation_bases(cls, conversation_id: str) -> List["KnowledgeBase"]:
        """
        Obtém bases de conhecimento de uma conversa específica.

        Args:
            conversation_id: ID da conversa

        Returns:
            Lista de bases de conhecimento da conversa
        """
        return cls.get_bases(scope="conversation", conversation_id=conversation_id)
