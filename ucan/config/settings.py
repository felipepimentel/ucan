"""
Configurações carregadas de variáveis de ambiente.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv

from ucan.config.constants import ROOT_DIR

# Carrega variáveis de ambiente do arquivo .env
ENV_PATH = ROOT_DIR / ".env"
load_dotenv(ENV_PATH)


class Settings:
    """Gerencia as configurações da aplicação carregadas de variáveis de ambiente."""

    ROOT_DIR: Path = ROOT_DIR

    # Configurações principais do LLM
    UCAN_API_KEY: str = os.getenv("UCAN_API_KEY", "")
    UCAN_PROVIDER: str = os.getenv("UCAN_PROVIDER", "")
    UCAN_MODEL: str = os.getenv("UCAN_MODEL", "")
    UCAN_ENV: str = os.getenv("UCAN_ENV", "development")
    UCAN_DEBUG: bool = os.getenv("UCAN_DEBUG", "False").lower() == "true"

    # Configurações de fallback
    UCAN_FALLBACK_PROVIDER: str = os.getenv("UCAN_FALLBACK_PROVIDER", "")
    UCAN_FALLBACK_MODEL: str = os.getenv("UCAN_FALLBACK_MODEL", "")
    UCAN_FALLBACK_API_KEY: str = os.getenv("UCAN_FALLBACK_API_KEY", "")

    # Configurações de provedores
    UCAN_PROVIDER__ENABLED_PROVIDERS: List[str] = json.loads(
        os.getenv(
            "UCAN_PROVIDER__ENABLED_PROVIDERS",
            '["openai", "anthropic", "openrouter", "stackspot", "local"]',
        )
    )
    UCAN_PROVIDER__RATE_LIMITS: Dict[str, int] = json.loads(
        os.getenv(
            "UCAN_PROVIDER__RATE_LIMITS",
            '{"openai": 60, "anthropic": 60, "openrouter": 60, "stackspot": 60}',
        )
    )

    # Configurações do agente
    UCAN_AGENT__MODEL_TYPE: str = os.getenv("UCAN_AGENT__MODEL_TYPE", "")
    UCAN_AGENT__TEMPERATURE: float = float(os.getenv("UCAN_AGENT__TEMPERATURE", "0.7"))
    UCAN_AGENT__MAX_TOKENS: int = int(os.getenv("UCAN_AGENT__MAX_TOKENS", "1000"))
    UCAN_AGENT__TIMEOUT: int = int(os.getenv("UCAN_AGENT__TIMEOUT", "30"))

    # Configurações de memória
    UCAN_MEMORY__IMPORTANCE_THRESHOLD: float = float(
        os.getenv("UCAN_MEMORY__IMPORTANCE_THRESHOLD", "0.5")
    )
    UCAN_MEMORY__VECTOR_STORE_TYPE: str = os.getenv(
        "UCAN_MEMORY__VECTOR_STORE_TYPE", "faiss"
    )
    UCAN_MEMORY__EMBEDDING_SIZE: int = int(
        os.getenv("UCAN_MEMORY__EMBEDDING_SIZE", "512")
    )
    UCAN_MEMORY__CACHE_TTL: int = int(os.getenv("UCAN_MEMORY__CACHE_TTL", "3600"))
    UCAN_MEMORY__MAX_SHORT_TERM_MEMORIES: int = int(
        os.getenv("UCAN_MEMORY__MAX_SHORT_TERM_MEMORIES", "100")
    )
    UCAN_MEMORY__TEXT_CHUNK_SIZE: int = int(
        os.getenv("UCAN_MEMORY__TEXT_CHUNK_SIZE", "1000")
    )
    UCAN_MEMORY__TEXT_OVERLAP: int = int(os.getenv("UCAN_MEMORY__TEXT_OVERLAP", "100"))

    # Configurações de aplicação
    LOG_LEVEL: str = os.getenv("UCAN_LOG_LEVEL", "INFO")
    LOG_DIR: Path = Path(os.getenv("LOG_DIR", str(ROOT_DIR / "logs")))
    CACHE_DIR: Path = Path(os.getenv("CACHE_DIR", str(ROOT_DIR / ".cache")))
    CONVERSATIONS_DIR: Path = Path(
        os.getenv("CONVERSATIONS_DIR", str(ROOT_DIR / "conversations"))
    )

    # Configurações de interface
    DARK_THEME: bool = os.getenv("DARK_THEME", "True").lower() == "true"
    CUSTOM_THEME: bool = os.getenv("CUSTOM_THEME", "True").lower() == "true"
    FONT_SIZE: int = int(os.getenv("FONT_SIZE", "12"))
    SAVE_CHAT_HISTORY: bool = os.getenv("SAVE_CHAT_HISTORY", "True").lower() == "true"

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        Obtém o valor de uma configuração.

        Args:
            key: Nome da configuração
            default: Valor padrão caso a configuração não exista

        Returns:
            Valor da configuração ou o valor padrão
        """
        return getattr(cls, key, default)

    @classmethod
    def has_api_key(cls) -> bool:
        """Verifica se há uma chave de API configurada."""
        return bool(cls.UCAN_API_KEY or cls.UCAN_FALLBACK_API_KEY)

    @classmethod
    def get_provider_config(cls) -> Dict[str, Any]:
        """Retorna a configuração do provedor atual."""
        provider = cls.UCAN_PROVIDER or cls.UCAN_FALLBACK_PROVIDER
        model = cls.UCAN_MODEL or cls.UCAN_FALLBACK_MODEL
        api_key = cls.UCAN_API_KEY or cls.UCAN_FALLBACK_API_KEY

        if not provider or not model or not api_key:
            return {}

        return {
            "provider": provider,
            "model": model,
            "api_key": api_key,
            "timeout": cls.UCAN_AGENT__TIMEOUT,
            "temperature": cls.UCAN_AGENT__TEMPERATURE,
            "max_tokens": cls.UCAN_AGENT__MAX_TOKENS,
        }

    @classmethod
    def create_default_env_file(cls) -> None:
        """Cria um arquivo .env com as configurações padrão."""
        if ENV_PATH.exists():
            return

        with open(ENV_PATH, "w", encoding="utf-8") as f:
            f.write(
                """# UCAN Configuration
UCAN_API_KEY=
UCAN_PROVIDER=openai
UCAN_MODEL=gpt-4-turbo-preview
UCAN_ENV=development
UCAN_DEBUG=true

# UCAN API Keys (for LLM)
UCAN_FALLBACK_PROVIDER=openrouter
UCAN_FALLBACK_MODEL=openai/gpt-4-turbo
UCAN_FALLBACK_API_KEY=

# Provider Configuration
UCAN_PROVIDER__ENABLED_PROVIDERS='["openai", "anthropic", "openrouter", "stackspot", "local"]'
UCAN_PROVIDER__RATE_LIMITS='{"openai": 60, "anthropic": 60, "openrouter": 60, "stackspot": 60}'

# Agent Configuration
UCAN_AGENT__MODEL_TYPE=openai/gpt-4-turbo
UCAN_AGENT__TEMPERATURE=0.7
UCAN_AGENT__MAX_TOKENS=1000
UCAN_AGENT__TIMEOUT=30

# Memory Configuration
UCAN_MEMORY__IMPORTANCE_THRESHOLD=0.5
UCAN_MEMORY__VECTOR_STORE_TYPE=faiss
UCAN_MEMORY__EMBEDDING_SIZE=512
UCAN_MEMORY__CACHE_TTL=3600
UCAN_MEMORY__MAX_SHORT_TERM_MEMORIES=100
UCAN_MEMORY__TEXT_CHUNK_SIZE=1000
UCAN_MEMORY__TEXT_OVERLAP=100

# Interface Configuration
WINDOW_WIDTH=1200
WINDOW_HEIGHT=800
WINDOW_MIN_WIDTH=800
WINDOW_MIN_HEIGHT=600
CHAT_WIDTH=800
CHAT_HEIGHT=600
CHAT_MIN_WIDTH=400
CHAT_MIN_HEIGHT=300
SIDEBAR_WIDTH=300

# Cache Configuration
CACHE_ENABLED=true
CACHE_DIR=".cache"
CACHE_MAX_SIZE=1024  # MB
CACHE_TTL=86400  # 24 horas

# Log Configuration
UCAN_LOG_LEVEL=INFO
LOG_DIR="logs"
LOG_MAX_SIZE=10  # MB
LOG_BACKUP_COUNT=5

# Conversation Configuration
CONVERSATIONS_DIR="conversations"
MAX_MESSAGE_LENGTH=4000
MAX_CONTEXT_LENGTH=8000

# Theme Configuration
DARK_THEME=true
CUSTOM_THEME=true
FONT_SIZE=12
SAVE_CHAT_HISTORY=true
"""
            )


# Cria arquivo .env padrão se não existir
Settings.create_default_env_file()


# Instância única de configurações para uso em toda a aplicação
settings = Settings()
