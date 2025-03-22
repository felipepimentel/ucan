"""
Módulo do assistente.
"""

import logging
from typing import Dict, List

from ucan.core.knowledge_base import KnowledgeBase
from ucan.core.knowledge_manager import KnowledgeManager

logger = logging.getLogger(__name__)


class Assistant:
    """Assistente de chat."""

    def __init__(self, llm_interface=None):
        """
        Inicializa o assistente.

        Args:
            llm_interface: Interface com o modelo de linguagem (opcional)
        """
        self._knowledge_bases: List[KnowledgeBase] = []
        self.llm = llm_interface

    def set_knowledge_bases(self, bases: List[KnowledgeBase]):
        """
        Define as bases de conhecimento a serem usadas.

        Args:
            bases: Lista de bases de conhecimento
        """
        self._knowledge_bases = bases

    def get_response(self, message: str) -> str:
        """
        Obtém uma resposta para uma mensagem.

        Args:
            message: Mensagem do usuário

        Returns:
            Resposta do assistente
        """
        try:
            # Pesquisa nas bases de conhecimento
            base_ids = [base.id for base in self._knowledge_bases]
            relevant_items = KnowledgeManager.search_knowledge_items(
                query=message,
                base_ids=base_ids,
                limit=5,
            )

            # Se encontrou itens relevantes, usa-os para gerar a resposta
            if relevant_items:
                context = self._build_context(relevant_items)
                return self._generate_response_with_context(message, context)

            # Se não encontrou itens relevantes, gera uma resposta padrão
            return self._generate_response_without_context(message)

        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            return "Desculpe, ocorreu um erro ao gerar a resposta."

    def _build_context(self, items: List[Dict]) -> str:
        """
        Constrói o contexto para a resposta a partir dos itens relevantes.

        Args:
            items: Lista de itens relevantes

        Returns:
            Contexto formatado
        """
        context_parts = []
        for item in items:
            content = KnowledgeManager.get_item_content(item["id"])
            if content:
                context_parts.append(f"[{item['file_name']}]\n{content}\n")
        return "\n".join(context_parts)

    def _generate_response_with_context(self, message: str, context: str) -> str:
        """
        Gera uma resposta usando o contexto das bases de conhecimento.

        Args:
            message: Mensagem do usuário
            context: Contexto das bases de conhecimento

        Returns:
            Resposta gerada
        """
        # TODO: Implementar geração de resposta usando LLM com o contexto
        return f"Resposta baseada no contexto: {context[:100]}..."

    def _generate_response_without_context(self, message: str) -> str:
        """
        Gera uma resposta sem usar bases de conhecimento.

        Args:
            message: Mensagem do usuário

        Returns:
            Resposta gerada
        """
        # TODO: Implementar geração de resposta usando LLM sem contexto
        return "Resposta sem contexto específico."
