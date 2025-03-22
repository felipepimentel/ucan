"""
Módulo de configuração e gerenciamento do banco de dados.
"""

import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from ucan.config.constants import DATABASE_URL

logger = logging.getLogger(__name__)

# Create declarative base
Base = declarative_base()

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


# Create database instance
db = Database()
