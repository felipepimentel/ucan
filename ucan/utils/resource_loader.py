"""
Utilitários para carregamento de recursos.

Este módulo contém funções para carregar recursos como ícones, imagens e estilos.
"""

import logging
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap

from ucan.config.constants import BASE_DIR, ICONS_DIR, RESOURCES_DIR

logger = logging.getLogger(__name__)


def ensure_resource_dirs():
    """Garante que os diretórios de recursos existam."""
    try:
        RESOURCES_DIR.mkdir(parents=True, exist_ok=True)
        ICONS_DIR.mkdir(parents=True, exist_ok=True)

        # Copia os ícones do pacote para o diretório de recursos se necessário
        package_icons = Path(__file__).parent.parent / "resources" / "icons"
        if package_icons.exists():
            import shutil

            for icon in package_icons.glob("*.svg"):
                target = ICONS_DIR / icon.name
                if not target.exists():
                    shutil.copy2(icon, target)
    except Exception as e:
        logger.warning(f"Erro ao criar diretórios de recursos: {e}")


def load_icon(icon_name: str, size: int = 24, fallback: str = None) -> QPixmap:
    """
    Carrega um ícone como QPixmap de forma segura.

    Args:
        icon_name: Nome do arquivo do ícone (com ou sem extensão .svg)
        size: Tamanho desejado para o ícone
        fallback: Nome de um ícone alternativo para usar caso o principal não seja encontrado

    Returns:
        Imagem do ícone como QPixmap ou um pixmap vazio se não for possível carregar
    """
    ensure_resource_dirs()

    # Adicionar extensão .svg se não estiver presente
    if not icon_name.endswith(".svg"):
        icon_name = f"{icon_name}.svg"

    # Lista de caminhos possíveis para o ícone, em ordem de prioridade
    icon_paths = [
        ICONS_DIR / icon_name,  # Primeiro procura no diretório de ícones do usuário
        BASE_DIR / "resources" / "icons" / icon_name,  # Depois no diretório do projeto
        Path(__file__).parent.parent
        / "resources"
        / "icons"
        / icon_name,  # Por fim no pacote
    ]

    # Tentar carregar o ícone do primeiro caminho válido
    for icon_path in icon_paths:
        try:
            if icon_path.exists():
                pixmap = QPixmap(str(icon_path))
                if not pixmap.isNull():
                    return pixmap.scaled(
                        size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
        except Exception as e:
            logger.debug(f"Erro ao carregar ícone {icon_path}: {e}")
            continue

    # Se não conseguiu carregar o ícone principal e tem fallback, tenta o fallback
    if fallback and fallback != icon_name:
        return load_icon(fallback, size)

    # Se tudo falhar, retorna um pixmap vazio
    logger.warning(f"Não foi possível carregar o ícone: {icon_name}")
    return QPixmap()


def get_icon(icon_name: str, fallback: str = None) -> QIcon:
    """
    Carrega um ícone como QIcon de forma segura.

    Args:
        icon_name: Nome do arquivo do ícone
        fallback: Nome de um ícone alternativo para usar caso o principal não seja encontrado

    Returns:
        Objeto QIcon
    """
    pixmap = load_icon(icon_name, fallback=fallback)
    return QIcon(pixmap)


def load_stylesheet(name: str) -> str:
    """
    Carrega um arquivo de estilo CSS.

    Args:
        name: Nome do arquivo de estilo (sem extensão)

    Returns:
        Conteúdo do arquivo CSS ou string vazia se não encontrado
    """
    ensure_resource_dirs()

    # Lista de caminhos possíveis para o arquivo CSS
    css_paths = [
        RESOURCES_DIR / "styles" / f"{name}.css",  # Diretório de estilos do usuário
        BASE_DIR / "resources" / "styles" / f"{name}.css",  # Diretório do projeto
        Path(__file__).parent.parent / "resources" / "styles" / f"{name}.css",  # Pacote
    ]

    for css_path in css_paths:
        try:
            if css_path.exists():
                with open(css_path, "r", encoding="utf-8") as f:
                    return f.read()
        except Exception as e:
            logger.debug(f"Erro ao carregar estilo {css_path}: {e}")
            continue

    logger.warning(f"Não foi possível carregar o arquivo de estilo: {name}")
    return ""
