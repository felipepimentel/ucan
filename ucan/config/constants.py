"""
Constantes da aplicação.
"""

import os
from pathlib import Path
from typing import List

# Diretórios
ROOT_DIR = Path(__file__).parent.parent
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
RESOURCES_DIR = BASE_DIR / "resources"
ICONS_DIR = RESOURCES_DIR / "icons"
CONFIG_DIR = ROOT_DIR / "config"

# Garante que os diretórios existem
RESOURCES_DIR.mkdir(parents=True, exist_ok=True)
ICONS_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# Arquivo de configuração
CONFIG_FILE = BASE_DIR / "config.json"

# Arquivo de log
LOG_FILE = BASE_DIR / "logs" / "ucan.log"

# Versão da aplicação
VERSION = "0.1.0"

# Configurações da aplicação
SUPPORTED_LANGUAGES: List[str] = ["pt-BR", "en-US"]
DEFAULT_LANGUAGE: str = "pt-BR"

# Configurações de chat
MAX_MESSAGE_LENGTH: int = 2000
MAX_CONTEXT_LENGTH: int = 8000
MAX_TOKENS: int = 4000

# Configurações de interface
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600
WINDOW_DEFAULT_WIDTH = 1200
WINDOW_DEFAULT_HEIGHT = 800

# Configurações de interface
WINDOW_WIDTH: int = 1200
WINDOW_HEIGHT: int = 800
WINDOW_MIN_WIDTH: int = 800
WINDOW_MIN_HEIGHT: int = 600
WINDOW_TITLE: str = "UCAN - Universal Chat Assistant Network"

# Configurações de chat
MESSAGE_CHUNK_SIZE: int = 1000

# Configurações de interface
CHAT_WIDTH: int = 800
CHAT_HEIGHT: int = 600
CHAT_MIN_WIDTH: int = 400
CHAT_MIN_HEIGHT: int = 300
SIDEBAR_WIDTH: int = 300

# Modelos de IA disponíveis
AI_MODELS: List[str] = [
    "gpt-3.5-turbo",
    "gpt-4",
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
]

# Modelo padrão
DEFAULT_AI_MODEL: str = "gpt-3.5-turbo"

# Mensagens do sistema
WELCOME_MESSAGE: str = "Olá! Como posso ajudar você hoje?"
ERROR_MESSAGE: str = "Ocorreu um erro ao processar sua solicitação."
LOADING_MESSAGE: str = "Processando..."

# Diretórios
CONVERSATIONS_DIR: str = "conversations"
LOGS_DIR: str = "logs"
CACHE_DIR: str = "cache"

# Novas constantes adicionadas
PADDING_SMALL: int = 4
PADDING_NORMAL: int = 8
PADDING_LARGE: int = 16

# Configurações de tema
DARK_THEME: bool = True

# Cores
PRIMARY_COLOR: str = "#2563eb"  # Azul principal
SECONDARY_COLOR: str = "#1e40af"  # Azul escuro
ACCENT_COLOR: str = "#2563eb"
ACCENT_COLOR_LIGHT: str = "#3b82f6"
ACCENT_COLOR_DARK: str = "#1d4ed8"
BACKGROUND_COLOR: str = "#1e1e1e"
BACKGROUND_COLOR_LIGHT: str = "#2d2d2d"
TEXT_COLOR: str = "#ffffff"
TEXT_COLOR_SECONDARY: str = "#a0a0a0"
BORDER_COLOR: str = "#404040"
HOVER_COLOR: str = "#3b82f6"  # Mesmo que o accent
ERROR_COLOR: str = "#ef4444"  # Vermelho
SUCCESS_COLOR: str = "#22c55e"  # Verde
MUTED_COLOR: str = "#64748b"  # Cinza médio

# Configurações de fonte
FONT_FAMILY: str = "Segoe UI"
FONT_SIZE_SMALL: int = 12
FONT_SIZE_NORMAL: int = 14
FONT_SIZE_LARGE: int = 16
FONT_SIZE_XLARGE: int = 21
FONT_WEIGHT_NORMAL: int = 400
FONT_WEIGHT_MEDIUM: int = 500
FONT_WEIGHT_BOLD: int = 600

# Configurações de sombra
SHADOW_SMALL: str = "0 2px 4px rgba(0, 0, 0, 0.1)"
SHADOW_NORMAL: str = "0 4px 6px rgba(0, 0, 0, 0.1)"
SHADOW_LARGE: str = "0 10px 15px rgba(0, 0, 0, 0.1)"

# Configurações de layout
SPACING_TINY: int = 4
SPACING_SMALL: int = 8
SPACING_NORMAL: int = 12
SPACING_MEDIUM: int = 16
SPACING_LARGE: int = 24
SPACING_XLARGE: int = 32
BORDER_RADIUS_SMALL: int = 2
BORDER_RADIUS: int = 4
BORDER_RADIUS_LARGE: int = 8
BORDER_WIDTH: int = 1

# Configurações de aplicação
APP_NAME: str = "UCAN"
APP_VERSION: str = "0.1.0"
APP_DESCRIPTION: str = (
    "Um aplicativo para interação com modelos de linguagem de última geração."
)
APP_AUTHOR: str = "UCAN Team"

# Configurações de aplicação
DEFAULT_MODEL: str = "gpt-3.5-turbo"
DEFAULT_TEMPERATURE: float = 0.7
DEFAULT_API_TIMEOUT: int = 60
