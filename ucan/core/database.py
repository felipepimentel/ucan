"""
Módulo de gerenciamento de banco de dados usando DuckDB.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional

import duckdb

from ucan.config.settings import settings

logger = logging.getLogger(__name__)


class Database:
    """Gerenciador de banco de dados usando DuckDB."""

    def __init__(self) -> None:
        """Inicializa o banco de dados."""
        self.db_path = settings.ROOT_DIR / ".ucan" / "database.duckdb"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = duckdb.connect(str(self.db_path))
        self._init_tables()

    def _init_tables(self) -> None:
        """Inicializa as tabelas do banco de dados."""
        # Drop existing tables in reverse order of dependencies
        self.conn.execute("DROP TABLE IF EXISTS conversation_knowledge")
        self.conn.execute("DROP TABLE IF EXISTS knowledge_items")
        self.conn.execute("DROP TABLE IF EXISTS knowledge_bases")
        self.conn.execute("DROP TABLE IF EXISTS messages")
        self.conn.execute("DROP TABLE IF EXISTS conversations")
        self.conn.execute("DROP TABLE IF EXISTS conversation_types")
        self.conn.execute("DROP TABLE IF EXISTS settings")

        # Create tables in order of dependencies

        # Tabela de configurações (independent)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key VARCHAR PRIMARY KEY,
                value JSON NOT NULL,
                updated_at TIMESTAMP NOT NULL
            )
        """)

        # Tabela de tipos de conversa (independent)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS conversation_types (
                id VARCHAR PRIMARY KEY,
                name VARCHAR NOT NULL,
                description TEXT,
                created_at TIMESTAMP NOT NULL,
                metadata JSON
            )
        """)

        # Tabela de conversas (depends on conversation_types)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id VARCHAR PRIMARY KEY,
                title VARCHAR NOT NULL,
                type_id VARCHAR,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                metadata JSON,
                FOREIGN KEY (type_id) REFERENCES conversation_types(id)
            )
        """)

        # Tabela de mensagens (depends on conversations)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id VARCHAR PRIMARY KEY,
                conversation_id VARCHAR NOT NULL,
                role VARCHAR NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                metadata JSON,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)

        # Tabela de bases de conhecimento (depends on conversation_types and conversations)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_bases (
                id VARCHAR PRIMARY KEY,
                name VARCHAR NOT NULL,
                description TEXT,
                scope VARCHAR NOT NULL CHECK (scope IN ('global', 'type', 'conversation')),
                type_id VARCHAR,
                conversation_id VARCHAR,
                created_at TIMESTAMP NOT NULL,
                metadata JSON,
                FOREIGN KEY (type_id) REFERENCES conversation_types(id),
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)

        # Tabela de itens de conhecimento (depends on knowledge_bases)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_items (
                id VARCHAR PRIMARY KEY,
                knowledge_base_id VARCHAR NOT NULL,
                file_name VARCHAR NOT NULL,
                file_type VARCHAR NOT NULL,
                content TEXT NOT NULL,
                embedding_vector BLOB,
                created_at TIMESTAMP NOT NULL,
                metadata JSON,
                FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id)
            )
        """)

        # Índices
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_conversation_id 
            ON messages(conversation_id)
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_updated_at 
            ON conversations(updated_at)
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_knowledge_bases_scope 
            ON knowledge_bases(scope)
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_knowledge_items_base_id 
            ON knowledge_items(knowledge_base_id)
        """)

    def save_conversation(
        self, conversation_id: str, title: str, metadata: Optional[Dict] = None
    ) -> None:
        """
        Salva uma conversa no banco de dados.

        Args:
            conversation_id: ID da conversa
            title: Título da conversa
            metadata: Metadados adicionais (opcional)
        """
        now = datetime.utcnow()
        try:
            # Primeiro tenta atualizar
            rows_updated = self.conn.execute(
                """
                UPDATE conversations 
                SET title = ?, updated_at = ?, metadata = ?
                WHERE id = ?
                """,
                [title, now, json.dumps(metadata or {}), conversation_id],
            ).fetchone()[0]

            # Se nenhuma linha foi atualizada, insere nova conversa
            if rows_updated == 0:
                self.conn.execute(
                    """
                    INSERT INTO conversations (id, title, created_at, updated_at, metadata)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    [conversation_id, title, now, now, json.dumps(metadata or {})],
                )
        except Exception as e:
            logger.error(f"Erro ao salvar conversa: {e}")
            raise

    def save_message(
        self,
        message_id: str,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None,
    ) -> None:
        """
        Salva uma mensagem no banco de dados.

        Args:
            message_id: ID da mensagem
            conversation_id: ID da conversa
            role: Papel do remetente (user, assistant, system)
            content: Conteúdo da mensagem
            metadata: Metadados adicionais (opcional)
        """
        self.conn.execute(
            """
            INSERT INTO messages (id, conversation_id, role, content, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            [
                message_id,
                conversation_id,
                role,
                content,
                datetime.utcnow(),
                json.dumps(metadata or {}),
            ],
        )

        # Atualiza o timestamp da conversa
        self.conn.execute(
            """
            UPDATE conversations
            SET updated_at = ?
            WHERE id = ?
        """,
            [datetime.utcnow(), conversation_id],
        )

    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """
        Obtém uma conversa do banco de dados.

        Args:
            conversation_id: ID da conversa

        Returns:
            Dados da conversa ou None se não encontrada
        """
        result = self.conn.execute(
            """
            SELECT id, title, created_at, updated_at, metadata
            FROM conversations
            WHERE id = ?
        """,
            [conversation_id],
        ).fetchone()

        if not result:
            return None

        return {
            "id": result[0],
            "title": result[1],
            "created_at": result[2],
            "updated_at": result[3],
            "metadata": json.loads(result[4]),
        }

    def get_messages(self, conversation_id: str) -> List[Dict]:
        """
        Obtém todas as mensagens de uma conversa.

        Args:
            conversation_id: ID da conversa

        Returns:
            Lista de mensagens
        """
        results = self.conn.execute(
            """
            SELECT id, role, content, created_at, metadata
            FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at ASC
        """,
            [conversation_id],
        ).fetchall()

        return [
            {
                "id": row[0],
                "role": row[1],
                "content": row[2],
                "created_at": row[3],
                "metadata": json.loads(row[4]),
            }
            for row in results
        ]

    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """
        Obtém as conversas mais recentes.

        Args:
            limit: Número máximo de conversas para retornar

        Returns:
            Lista de conversas
        """
        results = self.conn.execute(
            """
            SELECT id, title, created_at, updated_at, metadata
            FROM conversations
            ORDER BY updated_at DESC
            LIMIT ?
        """,
            [limit],
        ).fetchall()

        return [
            {
                "id": row[0],
                "title": row[1],
                "created_at": row[2],
                "updated_at": row[3],
                "metadata": json.loads(row[4]),
            }
            for row in results
        ]

    def save_setting(self, key: str, value: any) -> None:
        """
        Salva uma configuração no banco de dados.

        Args:
            key: Chave da configuração
            value: Valor da configuração
        """
        self.conn.execute(
            """
            INSERT INTO settings (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT (key) DO UPDATE SET
                value = excluded.value,
                updated_at = excluded.updated_at
        """,
            [key, json.dumps(value), datetime.utcnow()],
        )

    def get_setting(self, key: str, default: any = None) -> any:
        """
        Obtém uma configuração do banco de dados.

        Args:
            key: Chave da configuração
            default: Valor padrão se a configuração não existir

        Returns:
            Valor da configuração
        """
        result = self.conn.execute(
            """
            SELECT value
            FROM settings
            WHERE key = ?
        """,
            [key],
        ).fetchone()

        if not result:
            return default

        return json.loads(result[0])

    def close(self) -> None:
        """Fecha a conexão com o banco de dados."""
        self.conn.close()

    def create_knowledge_base(
        self,
        name: str,
        description: str,
        scope: str,
        type_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> str:
        """
        Cria uma nova base de conhecimento.

        Args:
            name: Nome da base
            description: Descrição da base
            scope: Escopo ('global', 'type', 'conversation')
            type_id: ID do tipo de conversa (opcional)
            conversation_id: ID da conversa (opcional)
            metadata: Metadados adicionais (opcional)

        Returns:
            ID da base de conhecimento criada
        """
        base_id = str(uuid.uuid4())
        self.conn.execute(
            """
            INSERT INTO knowledge_bases (
                id, name, description, scope, type_id, 
                conversation_id, created_at, metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                base_id,
                name,
                description,
                scope,
                type_id,
                conversation_id,
                datetime.utcnow(),
                json.dumps(metadata or {}),
            ],
        )
        return base_id

    def add_knowledge_item(
        self,
        base_id: str,
        file_name: str,
        file_type: str,
        content: str,
        embedding_vector: Optional[bytes] = None,
        metadata: Optional[Dict] = None,
    ) -> str:
        """
        Adiciona um item à base de conhecimento.

        Args:
            base_id: ID da base de conhecimento
            file_name: Nome do arquivo
            file_type: Tipo do arquivo
            content: Conteúdo do arquivo
            embedding_vector: Vetor de embedding do conteúdo (opcional)
            metadata: Metadados adicionais (opcional)

        Returns:
            ID do item criado
        """
        item_id = str(uuid.uuid4())
        self.conn.execute(
            """
            INSERT INTO knowledge_items (
                id, knowledge_base_id, file_name, file_type,
                content, embedding_vector, created_at, metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                item_id,
                base_id,
                file_name,
                file_type,
                content,
                embedding_vector,
                datetime.utcnow(),
                json.dumps(metadata or {}),
            ],
        )
        return item_id

    def get_knowledge_bases(
        self,
        scope: Optional[str] = None,
        type_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> List[Dict]:
        """
        Obtém bases de conhecimento com filtros opcionais.

        Args:
            scope: Filtrar por escopo
            type_id: Filtrar por tipo de conversa
            conversation_id: Filtrar por conversa

        Returns:
            Lista de bases de conhecimento
        """
        query = """
            SELECT id, name, description, scope, type_id,
                   conversation_id, created_at, metadata
            FROM knowledge_bases
            WHERE 1=1
        """
        params = []

        if scope:
            query += " AND scope = ?"
            params.append(scope)
        if type_id:
            query += " AND type_id = ?"
            params.append(type_id)
        if conversation_id:
            query += " AND conversation_id = ?"
            params.append(conversation_id)

        results = self.conn.execute(query, params).fetchall()
        return [
            {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "scope": row[3],
                "type_id": row[4],
                "conversation_id": row[5],
                "created_at": row[6],
                "metadata": json.loads(row[7]),
            }
            for row in results
        ]

    def get_knowledge_items(
        self, base_id: str, with_embeddings: bool = False
    ) -> List[Dict]:
        """
        Obtém itens de uma base de conhecimento.

        Args:
            base_id: ID da base de conhecimento
            with_embeddings: Se deve incluir os vetores de embedding

        Returns:
            Lista de itens
        """
        fields = """
            id, knowledge_base_id, file_name, file_type,
            content, created_at, metadata
        """
        if with_embeddings:
            fields += ", embedding_vector"

        results = self.conn.execute(
            f"""
            SELECT {fields}
            FROM knowledge_items
            WHERE knowledge_base_id = ?
            ORDER BY created_at DESC
            """,
            [base_id],
        ).fetchall()

        items = []
        for row in results:
            item = {
                "id": row[0],
                "knowledge_base_id": row[1],
                "file_name": row[2],
                "file_type": row[3],
                "content": row[4],
                "created_at": row[5],
                "metadata": json.loads(row[6]),
            }
            if with_embeddings:
                item["embedding_vector"] = row[7]
            items.append(item)

        return items


# Instância global do banco de dados
db = Database()
