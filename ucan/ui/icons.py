"""
Módulo para gerenciamento de ícones da interface.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PIL import Image
from PySide6.QtGui import QIcon

logger = logging.getLogger(__name__)

# Diretório de ícones
ICONS_DIR = Path(__file__).parent.parent.parent / "assets" / "icons"

# Cache de ícones carregados
_icon_cache: Dict[str, List[float]] = {}


def load_icon(name: str) -> QIcon:
    """
    Carrega um ícone pelo nome.

    Args:
        name: Nome do arquivo do ícone

    Returns:
        QIcon: Ícone carregado
    """
    icon_path = os.path.join(
        Path(__file__).parent.parent.parent, "assets", "icons", name
    )
    if os.path.exists(icon_path):
        return QIcon(icon_path)
    return QIcon.fromTheme(name.split(".")[0])  # Fallback para ícones do sistema


def find_icon(name: str) -> Optional[Path]:
    """
    Procura um arquivo de ícone com o nome especificado.

    Args:
        name: Nome do arquivo do ícone (sem extensão)

    Returns:
        Caminho do arquivo encontrado ou None
    """
    # Extensões suportadas em ordem de preferência
    extensions = [".svg", ".png", ".jpg", ".jpeg"]

    for ext in extensions:
        path = ICONS_DIR / f"{name}{ext}"
        if path.exists():
            return path

    return None


def create_placeholder_icon(size: Tuple[int, int]) -> List[float]:
    """
    Cria um ícone placeholder quando o ícone solicitado não é encontrado.

    Args:
        size: Tamanho do ícone (largura, altura)

    Returns:
        Lista de valores RGBA para a textura
    """
    # Criar imagem placeholder com um X vermelho
    img = Image.new("RGBA", size, (0, 0, 0, 0))

    # Desenhar um X vermelho
    from PIL import ImageDraw

    draw = ImageDraw.Draw(img)
    draw.line([(0, 0), size], fill=(255, 0, 0, 255), width=2)
    draw.line([(0, size[1]), (size[0], 0)], fill=(255, 0, 0, 255), width=2)

    # Converter para lista de floats [0-1]
    pixels = list(img.getdata())
    texture = []
    for r, g, b, a in pixels:
        texture.extend([r / 255, g / 255, b / 255, a / 255])

    return texture


def ensure_icons_dir():
    """Garante que o diretório de ícones existe."""
    os.makedirs(ICONS_DIR, exist_ok=True)
