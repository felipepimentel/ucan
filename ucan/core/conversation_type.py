"""
Módulo de gerenciamento de tipos de conversa.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from ucan.core.database import db
from ucan.core.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)


class ConversationType:
    """Representa um tipo de conversa."""

    def __init__(
        self,
        name: str,
        description: str,
        id: Optional[str] = None,
        meta_data: Optional[Dict] = None,
    ) -> None:
        """
        Inicializa um tipo de conversa.

        Args:
            name: Nome do tipo
            description: Descrição do tipo
            id: ID do tipo (opcional)
            meta_data: Metadados adicionais (opcional)
        """
        self.name = name
        self.description = description
        self.meta_data = meta_data or {}
        self.id = id

        if not self.id:
            self.id = self._create()

    def _create(self) -> str:
        """
        Cria o tipo de conversa no banco de dados.

        Returns:
            ID do tipo criado
        """
        type_id = str(uuid.uuid4())
        db.conn.execute(
            """
            INSERT INTO conversation_types (id, name, description, created_at, meta_data)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                type_id,
                self.name,
                self.description,
                datetime.utcnow(),
                json.dumps(self.meta_data),
            ],
        )
        return type_id

    def create_knowledge_base(
        self, name: str, description: str, meta_data: Optional[Dict] = None
    ) -> KnowledgeBase:
        """
        Cria uma nova base de conhecimento para este tipo.

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
            scope="type",
            type_id=self.id,
            meta_data=meta_data,
        )

    def get_knowledge_bases(self) -> List[KnowledgeBase]:
        """
        Obtém todas as bases de conhecimento deste tipo.

        Returns:
            Lista de bases de conhecimento
        """
        return KnowledgeBase.get_type_bases(self.id)

    @classmethod
    def get_all(cls) -> List["ConversationType"]:
        """
        Obtém todos os tipos de conversa.

        Returns:
            Lista de tipos de conversa
        """
        results = db.conn.execute(
            """
            SELECT id, name, description, meta_data
            FROM conversation_types
            ORDER BY name
            """
        ).fetchall()

        return [
            cls(
                name=row[1],
                description=row[2],
                id=row[0],
                meta_data=json.loads(row[3]),
            )
            for row in results
        ]

    @classmethod
    def get_by_id(cls, type_id: str) -> Optional["ConversationType"]:
        """
        Obtém um tipo de conversa pelo ID.

        Args:
            type_id: ID do tipo

        Returns:
            Tipo de conversa ou None se não encontrado
        """
        result = db.conn.execute(
            """
            SELECT id, name, description, meta_data
            FROM conversation_types
            WHERE id = ?
            """,
            [type_id],
        ).fetchone()

        if not result:
            return None

        return cls(
            name=result[1],
            description=result[2],
            id=result[0],
            meta_data=json.loads(result[3]),
        )
