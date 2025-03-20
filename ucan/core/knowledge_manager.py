"""
Módulo de gerenciamento global de bases de conhecimento.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from ucan.core.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)


class KnowledgeManager:
    """Gerenciador global de bases de conhecimento."""

    @classmethod
    def create_global_base(
        cls, name: str, description: str, metadata: Optional[Dict] = None
    ) -> KnowledgeBase:
        """
        Cria uma nova base de conhecimento global.

        Args:
            name: Nome da base
            description: Descrição da base
            metadata: Metadados adicionais (opcional)

        Returns:
            Base de conhecimento criada
        """
        return KnowledgeBase(
            name=name,
            description=description,
            scope="global",
            metadata=metadata,
        )

    @classmethod
    def get_global_bases(cls) -> List[KnowledgeBase]:
        """
        Obtém todas as bases de conhecimento globais.

        Returns:
            Lista de bases de conhecimento globais
        """
        return KnowledgeBase.get_global_bases()

    @classmethod
    def add_files_to_base(
        cls,
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
        item_ids = []
        for file_path in files:
            try:
                item_id = base.add_file(file_path, metadata)
                item_ids.append(item_id)
            except Exception as e:
                logger.error(f"Erro ao adicionar arquivo {file_path}: {e}")
        return item_ids

    @classmethod
    def add_directory_to_base(
        cls,
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
        directory = Path(directory)
        if not directory.is_dir():
            raise ValueError(f"{directory} não é um diretório")

        if recursive:
            files = list(directory.rglob(pattern))
        else:
            files = list(directory.glob(pattern))

        return cls.add_files_to_base(base, files, metadata)

    @classmethod
    def get_knowledge_items(
        cls, base_id: str, with_embeddings: bool = False
    ) -> List[Dict]:
        """
        Obtém itens de uma base de conhecimento.

        Args:
            base_id: ID da base de conhecimento
            with_embeddings: Se deve incluir os vetores de embedding

        Returns:
            Lista de itens
        """
        return KnowledgeBase.get_items(base_id, with_embeddings)

    @classmethod
    def search_knowledge_items(
        cls,
        query: str,
        base_ids: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[Dict]:
        """
        Pesquisa itens nas bases de conhecimento.

        Args:
            query: Texto para pesquisar
            base_ids: Lista de IDs das bases para pesquisar (opcional)
            limit: Número máximo de resultados

        Returns:
            Lista de itens encontrados
        """
        # TODO: Implementar pesquisa semântica usando embeddings
        return []

    @classmethod
    def get_item_content(cls, item_id: str) -> Optional[str]:
        """
        Obtém o conteúdo de um item.

        Args:
            item_id: ID do item

        Returns:
            Conteúdo do item ou None se não encontrado
        """
        # TODO: Implementar recuperação de conteúdo
        return None
