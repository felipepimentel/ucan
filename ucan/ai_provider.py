import logging
import random
from typing import List, Optional

logger = logging.getLogger("UCAN")


class AIProvider:
    """Provedor de IA para o chat"""

    def __init__(self):
        """Inicializa o provedor de IA"""
        self.responses = [
            "Entendi! Vou ajudar você com isso.",
            "Interessante! Pode me contar mais?",
            "Hmm, deixa eu pensar...",
            "Que legal! Vamos explorar essa ideia.",
            "Ótima pergunta! Vou tentar responder da melhor forma possível.",
            "Isso é muito interessante! Vamos discutir mais sobre isso.",
            "Entendo seu ponto de vista. Aqui está o que penso...",
            "Que tal considerarmos uma abordagem diferente?",
            "Vou pesquisar mais sobre isso e te dar uma resposta mais completa.",
            "Excelente observação! Vamos analisar em detalhes.",
        ]

        self.file_responses = [
            "Analisando o arquivo... parece ser um {type} interessante!",
            "Recebi seu arquivo! Vou dar uma olhada nesse {type}.",
            "Legal! Vou processar esse {type} e te dar um feedback.",
            "Ótimo! Vou analisar esse {type} e te ajudar com ele.",
            "Arquivo recebido! Vou examinar esse {type} com atenção.",
        ]

    def generate_response(
        self,
        message: str,
        context: Optional[List[tuple]] = None,
        message_type: str = "general",
    ) -> str:
        """
        Gera uma resposta para uma mensagem

        Args:
            message: A mensagem do usuário
            context: Lista de tuplas (role, content) com o histórico
            message_type: Tipo de mensagem (general, file, code)

        Returns:
            str: Resposta gerada
        """
        try:
            # Por enquanto, apenas retorna uma resposta aleatória
            response = random.choice(self.responses)
            logger.info(f"Resposta gerada: {response}")
            return response
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {str(e)}")
            return (
                "Desculpe, não consegui processar sua mensagem. Pode tentar novamente?"
            )

    def analyze_file(self, file_path: str, file_type: str) -> str:
        """
        Analisa um arquivo

        Args:
            file_path: Caminho do arquivo
            file_type: Tipo do arquivo (.pdf, .txt, etc)

        Returns:
            str: Análise do arquivo
        """
        try:
            # Remove o ponto do tipo
            type_name = file_type[1:] if file_type.startswith(".") else file_type

            # Por enquanto, apenas retorna uma resposta aleatória
            response = random.choice(self.file_responses).format(type=type_name.upper())
            logger.info(f"Análise de arquivo gerada: {response}")
            return response
        except Exception as e:
            logger.error(f"Erro ao analisar arquivo: {str(e)}")
            return "Desculpe, não consegui analisar o arquivo. Pode tentar novamente?"

    def analyze_code(self, code: str) -> str:
        """
        Analisa um trecho de código

        Args:
            code: Código para analisar

        Returns:
            str: Análise do código
        """
        try:
            return self.generate_response("", message_type="code")
        except Exception as e:
            logger.error(f"Erro ao analisar código: {str(e)}")
            return "Desculpe, não consegui analisar este código."
