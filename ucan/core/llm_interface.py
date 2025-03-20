"""
Interfaces para comunicação com Large Language Models (LLMs).
"""

from abc import ABC, abstractmethod
from typing import Optional

import requests
from requests.exceptions import RequestException, Timeout

from ucan.config.constants import DEFAULT_API_TIMEOUT, MAX_TOKENS
from ucan.config.settings import settings


class LLMInterface(ABC):
    """Interface base para todos os LLMs."""

    def __init__(self, model_name: str, api_key: Optional[str] = None) -> None:
        """
        Inicializa a interface do LLM.

        Args:
            model_name: Nome do modelo a ser utilizado
            api_key: Chave de API (opcional, pode ser carregada das configurações)
        """
        self.model_name = model_name
        self.api_key = api_key
        self.timeout = DEFAULT_API_TIMEOUT

    async def initialize(self) -> None:
        """Inicializa a interface do LLM."""
        pass

    @abstractmethod
    async def generate_response(
        self, content: str, max_tokens: int = MAX_TOKENS
    ) -> str:
        """
        Gera uma resposta para uma mensagem.

        Args:
            content: Conteúdo da mensagem
            max_tokens: Número máximo de tokens na resposta

        Returns:
            Resposta gerada pelo modelo
        """
        pass

    @abstractmethod
    def validate_api_key(self) -> bool:
        """
        Valida a chave de API.

        Returns:
            True se a chave é válida
        """
        pass


class OpenAIInterface(LLMInterface):
    """Interface para comunicação com a API da OpenAI."""

    def __init__(
        self, model_name: str = "gpt-3.5-turbo", api_key: Optional[str] = None
    ) -> None:
        """
        Inicializa a interface da OpenAI.

        Args:
            model_name: Nome do modelo a ser utilizado
            api_key: Chave de API da OpenAI
        """
        super().__init__(model_name, api_key or settings.OPENAI_API_KEY)
        self.api_url = "https://api.openai.com/v1/chat/completions"

    async def generate_response(
        self, content: str, max_tokens: int = MAX_TOKENS
    ) -> str:
        """
        Gera uma resposta usando a API da OpenAI.

        Args:
            content: Conteúdo da mensagem
            max_tokens: Número máximo de tokens na resposta

        Returns:
            Resposta gerada pelo modelo

        Raises:
            Exception: Se houver erro na comunicação com a API
        """
        if not self.api_key:
            raise Exception("Chave de API da OpenAI não configurada")

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            data = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": content}],
                "max_tokens": max_tokens,
            }

            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=self.timeout,
            )

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                raise Exception(f"Erro na API da OpenAI: {response.text}")

        except Timeout:
            raise Exception("Timeout na comunicação com a API da OpenAI")
        except RequestException as e:
            raise Exception(f"Erro na comunicação com a API da OpenAI: {str(e)}")
        except Exception as e:
            raise Exception(f"Erro ao gerar resposta: {str(e)}")

    def validate_api_key(self) -> bool:
        """
        Valida a chave de API da OpenAI.

        Returns:
            True se a chave é válida
        """
        if not self.api_key:
            return False

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            response = requests.get(
                "https://api.openai.com/v1/models",
                headers=headers,
                timeout=self.timeout,
            )

            return response.status_code == 200

        except Exception:
            return False


class AnthropicInterface(LLMInterface):
    """Interface para comunicação com a API da Anthropic."""

    def __init__(
        self, model_name: str = "claude-3-sonnet", api_key: Optional[str] = None
    ) -> None:
        """
        Inicializa a interface da Anthropic.

        Args:
            model_name: Nome do modelo a ser utilizado
            api_key: Chave de API da Anthropic
        """
        super().__init__(model_name, api_key or settings.ANTHROPIC_API_KEY)
        self.api_url = "https://api.anthropic.com/v1/messages"

    async def generate_response(
        self, content: str, max_tokens: int = MAX_TOKENS
    ) -> str:
        """
        Gera uma resposta usando a API da Anthropic.

        Args:
            content: Conteúdo da mensagem
            max_tokens: Número máximo de tokens na resposta

        Returns:
            Resposta gerada pelo modelo

        Raises:
            Exception: Se houver erro na comunicação com a API
        """
        if not self.api_key:
            raise Exception("Chave de API da Anthropic não configurada")

        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            }

            data = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": content}],
                "max_tokens": max_tokens,
            }

            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=self.timeout,
            )

            if response.status_code == 200:
                return response.json()["content"][0]["text"]
            else:
                raise Exception(f"Erro na API da Anthropic: {response.text}")

        except Timeout:
            raise Exception("Timeout na comunicação com a API da Anthropic")
        except RequestException as e:
            raise Exception(f"Erro na comunicação com a API da Anthropic: {str(e)}")
        except Exception as e:
            raise Exception(f"Erro ao gerar resposta: {str(e)}")

    def validate_api_key(self) -> bool:
        """
        Valida a chave de API da Anthropic.

        Returns:
            True se a chave é válida
        """
        if not self.api_key:
            return False

        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            }

            response = requests.get(
                "https://api.anthropic.com/v1/models",
                headers=headers,
                timeout=self.timeout,
            )

            return response.status_code == 200

        except Exception:
            return False


class LocalLLMInterface(LLMInterface):
    """Interface para comunicação com um LLM local."""

    def __init__(
        self, model_name: str = "llama2", api_url: Optional[str] = None
    ) -> None:
        """
        Inicializa a interface do LLM local.

        Args:
            model_name: Nome do modelo a ser utilizado
            api_url: URL da API local
        """
        super().__init__(model_name)
        self.api_url = api_url or settings.LOCAL_LLM_URL

    async def generate_response(
        self, content: str, max_tokens: int = MAX_TOKENS
    ) -> str:
        """
        Gera uma resposta usando o LLM local.

        Args:
            content: Conteúdo da mensagem
            max_tokens: Número máximo de tokens na resposta

        Returns:
            Resposta gerada pelo modelo

        Raises:
            Exception: Se houver erro na comunicação com a API
        """
        try:
            data = {
                "model": self.model_name,
                "prompt": content,
                "max_tokens": max_tokens,
            }

            response = requests.post(
                f"{self.api_url}/v1/completions",
                json=data,
                timeout=self.timeout,
            )

            if response.status_code == 200:
                return response.json()["choices"][0]["text"]
            else:
                raise Exception(f"Erro na API local: {response.text}")

        except Timeout:
            raise Exception("Timeout na comunicação com a API local")
        except RequestException as e:
            raise Exception(f"Erro na comunicação com a API local: {str(e)}")
        except Exception as e:
            raise Exception(f"Erro ao gerar resposta: {str(e)}")

    def validate_api_key(self) -> bool:
        """
        Valida a conexão com o LLM local.

        Returns:
            True se a conexão é válida
        """
        if not self.api_url:
            return False

        try:
            response = requests.get(
                f"{self.api_url}/health",
                timeout=self.timeout,
            )

            return response.status_code == 200

        except Exception:
            return False


class MockLLMInterface(LLMInterface):
    """Interface simulada para testes."""

    def __init__(self) -> None:
        """Inicializa a interface simulada."""
        super().__init__("mock")

    async def initialize(self) -> None:
        """Inicializa a interface simulada."""
        pass

    async def generate_response(
        self, content: str, max_tokens: int = MAX_TOKENS
    ) -> str:
        """
        Gera uma resposta simulada.

        Args:
            content: Conteúdo da mensagem
            max_tokens: Número máximo de tokens na resposta

        Returns:
            Resposta simulada
        """
        return "Esta é uma resposta simulada para teste."

    def validate_api_key(self) -> bool:
        """
        Valida a chave de API simulada.

        Returns:
            True, pois é uma interface simulada
        """
        return True


def get_llm_interface() -> LLMInterface:
    """
    Retorna uma interface LLM apropriada com base nas configurações.

    Returns:
        Interface LLM configurada
    """
    # Se não houver chaves de API configuradas, retorna a interface mock
    if not settings.get("OPENAI_API_KEY") and not settings.get("ANTHROPIC_API_KEY"):
        return MockLLMInterface()

    # Tenta criar uma interface OpenAI
    if settings.get("OPENAI_API_KEY"):
        interface = OpenAIInterface(api_key=settings.get("OPENAI_API_KEY"))
        if interface.validate_api_key():
            return interface

    # Tenta criar uma interface Anthropic
    if settings.get("ANTHROPIC_API_KEY"):
        interface = AnthropicInterface(api_key=settings.get("ANTHROPIC_API_KEY"))
        if interface.validate_api_key():
            return interface

    # Se nenhuma interface válida for encontrada, retorna a interface mock
    return MockLLMInterface()
