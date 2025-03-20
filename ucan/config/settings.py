"""
Configurações carregadas de variáveis de ambiente.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv

from ucan.config.constants import ROOT_DIR

# Carrega variáveis de ambiente do arquivo .env
ENV_PATH = ROOT_DIR / ".env"
load_dotenv(ENV_PATH)


class Settings:
    """Gerencia as configurações da aplicação carregadas de variáveis de ambiente."""

    ROOT_DIR: Path = ROOT_DIR

    # Configurações de API
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    HF_API_KEY: Optional[str] = os.getenv("HF_API_KEY")
    LOCAL_LLM_URL: str = os.getenv("LOCAL_LLM_URL", "http://localhost:11434")

    # Configurações de aplicação
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
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
    def has_api_keys(cls) -> bool:
        """Verifica se pelo menos uma chave de API está configurada."""
        return any([cls.OPENAI_API_KEY, cls.ANTHROPIC_API_KEY, cls.HF_API_KEY])

    @classmethod
    def get_api_keys(cls) -> Dict[str, Optional[str]]:
        """Retorna todas as chaves de API configuradas."""
        return {
            "openai": cls.OPENAI_API_KEY,
            "anthropic": cls.ANTHROPIC_API_KEY,
            "huggingface": cls.HF_API_KEY,
        }

    @classmethod
    def create_default_env_file(cls) -> None:
        """Cria um arquivo .env com as configurações padrão."""
        if ENV_PATH.exists():
            return

        with open(ENV_PATH, "w", encoding="utf-8") as f:
            f.write(
                """# Configurações de desenvolvimento
DEBUG=true
LOG_LEVEL=DEBUG

# Configurações de tema
DARK_THEME=true
THEME_COLOR="#2563eb"

# Configurações de LLM
DEFAULT_LLM_MODEL="gpt-3.5-turbo"
DEFAULT_LLM_TEMPERATURE=0.7
DEFAULT_LLM_MAX_TOKENS=4000
DEFAULT_LLM_API_TIMEOUT=60

# Configurações de interface
WINDOW_WIDTH=1200
WINDOW_HEIGHT=800
WINDOW_MIN_WIDTH=800
WINDOW_MIN_HEIGHT=600
CHAT_WIDTH=800
CHAT_HEIGHT=600
CHAT_MIN_WIDTH=400
CHAT_MIN_HEIGHT=300
SIDEBAR_WIDTH=300

# Configurações de cache
CACHE_ENABLED=true
CACHE_DIR="cache"
CACHE_MAX_SIZE=1024  # MB
CACHE_TTL=86400  # 24 horas

# Configurações de log
LOG_DIR="logs"
LOG_MAX_SIZE=10  # MB
LOG_BACKUP_COUNT=5

# Configurações de conversas
CONVERSATIONS_DIR="conversations"
MAX_MESSAGE_LENGTH=4000
MAX_CONTEXT_LENGTH=8000
"""
            )


# Cria arquivo .env padrão se não existir
Settings.create_default_env_file()


# Instância única de configurações para uso em toda a aplicação
settings = Settings()
