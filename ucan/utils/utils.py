"""
Funções utilitárias gerais.
"""

import logging
from pathlib import Path

from ucan.config.constants import RESOURCES_DIR

# Configure the logger
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def get_file_path(file_name: str) -> Path:
    """
    Retorna o caminho completo para um arquivo no diretório de dados.

    Args:
        file_name: Nome do arquivo

    Returns:
        Caminho completo do arquivo
    """
    if isinstance(file_name, str):
        path = Path(file_name)
        if not path.is_absolute():
            path = RESOURCES_DIR / path
        return path.resolve()
    return file_name.resolve()
