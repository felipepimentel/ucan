"""
Utilitários para manipulação de caminhos.
"""

from pathlib import Path


def get_resource_path(relative_path: str) -> Path:
    """
    Retorna o caminho absoluto para um recurso.

    Args:
        relative_path: Caminho relativo do recurso

    Returns:
        Caminho absoluto do recurso
    """
    return Path("ucan/resources") / relative_path
