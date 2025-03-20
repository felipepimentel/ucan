"""
Interfaces para comunicação com Large Language Models (LLMs).
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional

import requests
from requests.exceptions import RequestException, Timeout

from ucan.config.settings import settings


class LLMInterface(ABC):
    """Interface base para todos os LLMs."""

    def __init__(self, config: Optional[Dict] = None) -> None:
        """
        Inicializa a interface do LLM.

        Args:
            config: Configuração do provedor (opcional, carregada das configurações)
        """
        if config is None:
            config = settings.get_provider_config()

        self.provider = config.get("provider", "")
        self.model_name = config.get("model", "")
        self.api_key = config.get("api_key", "")
        self.timeout = config.get("timeout", 30)
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 1000)

    async def initialize(self) -> None:
        """Inicializa a interface do LLM."""
        pass

    @abstractmethod
    async def generate_response(
        self, content: str, max_tokens: Optional[int] = None
    ) -> str:
        """
        Gera uma resposta para uma mensagem.

        Args:
            content: Conteúdo da mensagem
            max_tokens: Número máximo de tokens na resposta (opcional)

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

    def __init__(self, config: Optional[Dict] = None) -> None:
        """
        Inicializa a interface da OpenAI.

        Args:
            config: Configuração do provedor (opcional)
        """
        super().__init__(config)
        self.api_url = "https://api.openai.com/v1/chat/completions"

    async def generate_response(
        self, content: str, max_tokens: Optional[int] = None
    ) -> str:
        """
        Gera uma resposta usando a API da OpenAI.

        Args:
            content: Conteúdo da mensagem
            max_tokens: Número máximo de tokens na resposta (opcional)

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
                "max_tokens": max_tokens or self.max_tokens,
                "temperature": self.temperature,
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
        """Valida a chave de API e o modelo configurado.

        Returns:
            bool: True se a chave de API e o modelo são válidos, False caso contrário.
        """
        if not self.api_key or not self.model_name:
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

    def __init__(self, config: Optional[Dict] = None) -> None:
        """
        Inicializa a interface da Anthropic.

        Args:
            config: Configuração do provedor (opcional)
        """
        super().__init__(config)
        self.api_url = "https://api.anthropic.com/v1/messages"

    async def generate_response(
        self, content: str, max_tokens: Optional[int] = None
    ) -> str:
        """
        Gera uma resposta usando a API da Anthropic.

        Args:
            content: Conteúdo da mensagem
            max_tokens: Número máximo de tokens na resposta (opcional)

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
                "max_tokens": max_tokens or self.max_tokens,
                "temperature": self.temperature,
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
        """Valida a chave de API e o modelo configurado.

        Returns:
            bool: True se a chave de API e o modelo são válidos, False caso contrário.
        """
        if not self.api_key or not self.model_name:
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


class OpenRouterInterface(LLMInterface):
    """Interface para comunicação com a API do OpenRouter."""

    def __init__(self, config: Optional[Dict] = None) -> None:
        """
        Inicializa a interface do OpenRouter.

        Args:
            config: Configuração do provedor (opcional)
        """
        super().__init__(config)
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

    async def generate_response(
        self, content: str, max_tokens: Optional[int] = None
    ) -> str:
        """
        Gera uma resposta usando a API do OpenRouter.

        Args:
            content: Conteúdo da mensagem
            max_tokens: Número máximo de tokens na resposta (opcional)

        Returns:
            Resposta gerada pelo modelo

        Raises:
            Exception: Se houver erro na comunicação com a API
        """
        if not self.api_key:
            raise Exception("Chave de API do OpenRouter não configurada")

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://ucan.ai",  # URL do projeto
                "X-Title": "UCAN",  # Nome do projeto
            }

            data = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": content}],
                "max_tokens": max_tokens or self.max_tokens,
                "temperature": self.temperature,
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
                raise Exception(f"Erro na API do OpenRouter: {response.text}")

        except Timeout:
            raise Exception("Timeout na comunicação com a API do OpenRouter")
        except RequestException as e:
            raise Exception(f"Erro na comunicação com a API do OpenRouter: {str(e)}")
        except Exception as e:
            raise Exception(f"Erro ao gerar resposta: {str(e)}")

    def validate_api_key(self) -> bool:
        """Valida a chave de API e o modelo configurado.

        Returns:
            bool: True se a chave de API e o modelo são válidos, False caso contrário.
        """
        if not self.api_key or not self.model_name:
            return False
        try:
            response = requests.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=self.timeout,
            )
            return response.status_code == 200
        except Exception:
            return False


class StackSpotAIInterface(LLMInterface):
    """Interface para comunicação com a API do StackSpot AI."""

    def __init__(self, config: Optional[Dict] = None) -> None:
        """
        Inicializa a interface do StackSpot AI.

        Args:
            config: Configuração do provedor (opcional)
        """
        super().__init__(config)
        self.api_url = "https://api.stackspot.com/v1/chat/completions"

    async def generate_response(
        self, content: str, max_tokens: Optional[int] = None
    ) -> str:
        """
        Gera uma resposta usando a API do StackSpot AI.

        Args:
            content: Conteúdo da mensagem
            max_tokens: Número máximo de tokens na resposta (opcional)

        Returns:
            Resposta gerada pelo modelo

        Raises:
            Exception: Se houver erro na comunicação com a API
        """
        if not self.api_key:
            raise Exception("Chave de API do StackSpot AI não configurada")

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            data = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": content}],
                "max_tokens": max_tokens or self.max_tokens,
                "temperature": self.temperature,
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
                raise Exception(f"Erro na API do StackSpot AI: {response.text}")

        except Timeout:
            raise Exception("Timeout na comunicação com a API do StackSpot AI")
        except RequestException as e:
            raise Exception(f"Erro na comunicação com a API do StackSpot AI: {str(e)}")
        except Exception as e:
            raise Exception(f"Erro ao gerar resposta: {str(e)}")

    def validate_api_key(self) -> bool:
        """Valida a chave de API e o modelo configurado.

        Returns:
            bool: True se a chave de API e o modelo são válidos, False caso contrário.
        """
        if not self.api_key or not self.model_name:
            return False
        try:
            response = requests.get(
                "https://api.stackspot.com/v1/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=self.timeout,
            )
            return response.status_code == 200
        except Exception:
            return False


class LocalLLMInterface(LLMInterface):
    """Interface para comunicação com um LLM local."""

    def __init__(self, config: Optional[Dict] = None) -> None:
        """
        Inicializa a interface do LLM local.

        Args:
            config: Configuração do provedor (opcional)
        """
        super().__init__(config)
        self.api_url = "http://localhost:11434"

    async def generate_response(
        self, content: str, max_tokens: Optional[int] = None
    ) -> str:
        """
        Gera uma resposta usando o LLM local.

        Args:
            content: Conteúdo da mensagem
            max_tokens: Número máximo de tokens na resposta (opcional)

        Returns:
            Resposta gerada pelo modelo

        Raises:
            Exception: Se houver erro na comunicação com a API
        """
        try:
            data = {
                "model": self.model_name,
                "prompt": content,
                "max_tokens": max_tokens or self.max_tokens,
                "temperature": self.temperature,
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
        """Valida a URL e o modelo configurado.

        Returns:
            bool: True se a URL e o modelo são válidos, False caso contrário.
        """
        if not self.model_name:
            return False
        try:
            response = requests.get(
                f"{self.api_url}/api/models",
                timeout=self.timeout,
            )
            return response.status_code == 200
        except Exception:
            return False


class MockLLMInterface(LLMInterface):
    """Interface simulada para testes."""

    def __init__(self) -> None:
        """Inicializa a interface simulada."""
        super().__init__({"provider": "mock", "model": "mock"})

    async def initialize(self) -> None:
        """Inicializa a interface simulada."""
        pass

    async def generate_response(
        self, content: str, max_tokens: Optional[int] = None
    ) -> str:
        """
        Gera uma resposta simulada.

        Args:
            content: Conteúdo da mensagem
            max_tokens: Número máximo de tokens na resposta (opcional)

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
    """Retorna uma interface LLM configurada.

    Returns:
        LLMInterface: Interface LLM configurada.
    """
    config = settings.get_provider_config()
    if not config:
        return MockLLMInterface()

    provider = config["provider"]
    interface_map = {
        "openai": OpenAIInterface,
        "anthropic": AnthropicInterface,
        "openrouter": OpenRouterInterface,
        "stackspot": StackSpotAIInterface,
        "local": LocalLLMInterface,
    }

    interface_class = interface_map.get(provider)
    if not interface_class:
        return MockLLMInterface()

    return interface_class(config)
