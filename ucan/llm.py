import base64
import logging
from typing import Dict, List, Optional

logger = logging.getLogger("UCAN")


class LLMProvider:
    """Provedor de LLM (Language Model) unificado"""

    def __init__(self):
        """Inicializa o provedor de LLM"""
        self.base_url = "http://localhost:8000"  # Para futura implementação da API
        self.headers = {"Content-Type": "application/json"}
        self.message_history = []
        self.max_history = 50

        # Respostas temporárias (mock) - Remover quando implementar a API real
        self._mock_responses = [
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

        self._mock_file_responses = [
            "Analisando o arquivo... parece ser um {type} interessante!",
            "Recebi seu arquivo! Vou dar uma olhada nesse {type}.",
            "Legal! Vou processar esse {type} e te dar um feedback.",
            "Ótimo! Vou analisar esse {type} e te ajudar com ele.",
            "Arquivo recebido! Vou examinar esse {type} com atenção.",
        ]

    def get_response(
        self,
        message: str,
        context: Optional[List[Dict[str, str]]] = None,
        attachment: Optional[Dict] = None,
    ) -> str:
        """
        Obtém uma resposta do modelo de linguagem

        Args:
            message: A mensagem do usuário
            context: Lista de mensagens anteriores no formato [{"role": "user/assistant", "content": "msg"}]
            attachment: Dicionário com informações do arquivo anexado (opcional)

        Returns:
            str: Resposta gerada pelo modelo
        """
        try:
            # TODO: Implementar chamada real à API do modelo
            # Por enquanto, retorna uma resposta mock
            import random

            return random.choice(self._mock_responses)

        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {str(e)}")
            return (
                "Desculpe, não consegui processar sua mensagem. Pode tentar novamente?"
            )

    def analyze_file(self, file_path: str, file_type: str) -> str:
        """
        Analisa um arquivo usando o modelo

        Args:
            file_path: Caminho do arquivo
            file_type: Tipo do arquivo (.pdf, .txt, etc)

        Returns:
            str: Análise do arquivo
        """
        try:
            # TODO: Implementar análise real de arquivo
            # Por enquanto, retorna uma resposta mock
            import random

            type_name = file_type[1:] if file_type.startswith(".") else file_type
            return random.choice(self._mock_file_responses).format(
                type=type_name.upper()
            )

        except Exception as e:
            logger.error(f"Erro ao analisar arquivo: {str(e)}")
            return "Desculpe, não consegui analisar o arquivo. Pode tentar novamente?"

    def _prepare_api_request(
        self, message: str, attachment: Optional[Dict] = None
    ) -> Dict:
        """
        Prepara o payload para a requisição à API

        Args:
            message: Mensagem do usuário
            attachment: Informações do arquivo anexado (opcional)

        Returns:
            Dict: Payload da requisição
        """
        data = {
            "messages": self.message_history + [{"role": "user", "content": message}]
        }

        if attachment:
            with open(attachment["path"], "rb") as f:
                content = base64.b64encode(f.read()).decode()

            data["attachment"] = {
                "name": attachment["name"],
                "type": attachment["type"],
                "content": content,
            }

        return data

    def _update_history(self, user_message: str, assistant_response: str):
        """
        Atualiza o histórico de mensagens

        Args:
            user_message: Mensagem do usuário
            assistant_response: Resposta do assistente
        """
        self.message_history.extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_response},
        ])

        # Mantém o histórico dentro do limite
        if len(self.message_history) > self.max_history:
            self.message_history = self.message_history[-self.max_history :]
