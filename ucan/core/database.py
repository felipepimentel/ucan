"""
Módulo de configuração e gerenciamento do banco de dados.
"""

import logging
from contextlib import contextmanager
from typing import Dict, Generator, List, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ucan.config.constants import DATABASE_URL
from ucan.core.base import Base
from ucan.core.models import Conversation, Message

logger = logging.getLogger(__name__)

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Database:
    """Classe para gerenciar operações do banco de dados."""

    def __init__(self):
        """Inicializa o banco de dados."""
        self.engine = engine
        self.SessionLocal = SessionLocal

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Contexto para obter uma sessão do banco de dados.
        Garante que a sessão seja fechada após o uso.

        Yields:
            Session: Sessão do banco de dados
        """
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def init(self) -> None:
        """
        Inicializa o banco de dados.
        Cria todas as tabelas se não existirem.
        """
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Banco de dados inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de dados: {e}")
            raise

    def close(self) -> None:
        """Fecha a conexão com o banco de dados."""
        try:
            self.engine.dispose()
            logger.info("Conexão com o banco de dados fechada")
        except Exception as e:
            logger.error(f"Erro ao fechar conexão com banco de dados: {e}")
            raise

    def get_conversations(self) -> List[Dict]:
        """
        Obtém todas as conversas do banco de dados.

        Returns:
            Lista de conversas
        """
        with self.get_session() as session:
            conversations = session.query(Conversation).all()
            return [conv.to_dict() for conv in conversations]

    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """
        Obtém uma conversa específica do banco de dados.

        Args:
            conversation_id: ID da conversa

        Returns:
            Dados da conversa ou None se não encontrada
        """
        with self.get_session() as session:
            conversation = (
                session.query(Conversation).filter_by(id=conversation_id).first()
            )
            return conversation.to_dict() if conversation else None

    def save_conversation(
        self, conversation_id: str, title: str, meta_data: Dict
    ) -> None:
        """
        Salva ou atualiza uma conversa no banco de dados.

        Args:
            conversation_id: ID da conversa
            title: Título da conversa
            meta_data: Metadados da conversa
        """
        with self.get_session() as session:
            conversation = (
                session.query(Conversation).filter_by(id=conversation_id).first()
            )
            if conversation:
                conversation.title = title
                conversation.meta_data = meta_data
            else:
                conversation = Conversation(
                    id=conversation_id,
                    title=title,
                    meta_data=meta_data,
                )
                session.add(conversation)
            session.commit()

    def get_messages(self, conversation_id: str) -> List[Dict]:
        """
        Obtém todas as mensagens de uma conversa.

        Args:
            conversation_id: ID da conversa

        Returns:
            Lista de mensagens
        """
        with self.get_session() as session:
            messages = (
                session.query(Message)
                .filter_by(conversation_id=conversation_id)
                .order_by(Message.created_at)
                .all()
            )
            return [msg.to_dict() for msg in messages]

    def save_message(
        self,
        message_id: str,
        conversation_id: str,
        role: str,
        content: str,
        meta_data: Dict,
    ) -> None:
        """
        Salva uma mensagem no banco de dados.

        Args:
            message_id: ID da mensagem
            conversation_id: ID da conversa
            role: Papel do remetente
            content: Conteúdo da mensagem
            meta_data: Metadados da mensagem
        """
        with self.get_session() as session:
            message = Message(
                id=message_id,
                conversation_id=conversation_id,
                role=role,
                content=content,
                meta_data=meta_data,
            )
            session.add(message)
            session.commit()


# Create database instance
db = Database()
