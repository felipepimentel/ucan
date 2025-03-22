"""
Configurações globais dos testes.
"""

from pathlib import Path

import pytest


@pytest.fixture
def test_dir():
    """Retorna o diretório de testes."""
    return Path(__file__).parent


@pytest.fixture
def resources_dir():
    """Retorna o diretório de recursos."""
    return Path(__file__).parent.parent / "resources"


@pytest.fixture
def config_dir():
    """Retorna o diretório de configuração."""
    return Path(__file__).parent.parent / "config"
