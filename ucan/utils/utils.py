"""
Funções utilitárias gerais.
"""

import logging
from pathlib import Path

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
    return Path(file_name).resolve()
