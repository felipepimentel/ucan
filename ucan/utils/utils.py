"""
Funções utilitárias gerais.
"""

from pathlib import Path


def get_file_path(file_name: str) -> Path:
    """
    Retorna o caminho completo para um arquivo no diretório de dados.

    Args:
        file_name: Nome do arquivo

    Returns:
        Caminho completo do arquivo
    """
    return Path(file_name).resolve()
