"""
Testes para o gerenciador de temas.
"""

from ucan.config.theme_manager import Theme, ThemeManager


def test_theme_creation():
    """Testa a criação de um tema."""
    theme = Theme(
        window_bg=(26, 27, 38),
        text=(192, 202, 245),
        border=(42, 43, 54),
        button=(65, 72, 104),
        button_hovered=(86, 95, 137),
        button_active=(122, 162, 247),
        accent=(122, 162, 247),
    )
    assert theme.window_bg == (26, 27, 38)
    assert theme.text == (192, 202, 245)
    assert theme.border == (42, 43, 54)
    assert theme.button == (65, 72, 104)
    assert theme.button_hovered == (86, 95, 137)
    assert theme.button_active == (122, 162, 247)
    assert theme.accent == (122, 162, 247)


def test_theme_manager_init():
    """Testa a inicialização do gerenciador de temas."""
    manager = ThemeManager()
    assert manager._current_theme == "default"
    assert "default" in manager._themes


def test_get_theme():
    """Testa a obtenção de um tema."""
    manager = ThemeManager()
    theme = manager.get_theme("default")
    assert isinstance(theme, Theme)
    assert theme.window_bg == (26, 27, 38)


def test_get_nonexistent_theme():
    """Testa a obtenção de um tema inexistente."""
    manager = ThemeManager()
    theme = manager.get_theme("nonexistent")
    assert theme == manager.get_theme("default")


def test_add_theme():
    """Testa a adição de um tema."""
    manager = ThemeManager()
    new_theme = Theme(
        window_bg=(30, 30, 30),
        text=(200, 200, 200),
        border=(50, 50, 50),
        button=(70, 70, 70),
        button_hovered=(90, 90, 90),
        button_active=(120, 120, 120),
        accent=(120, 120, 120),
    )
    manager.add_theme("custom", new_theme)
    assert manager.get_theme("custom") == new_theme


def test_get_theme_ids():
    """Testa a obtenção dos IDs dos temas."""
    manager = ThemeManager()
    assert "default" in manager.get_theme_ids()

    new_theme = Theme(
        window_bg=(30, 30, 30),
        text=(200, 200, 200),
        border=(50, 50, 50),
        button=(70, 70, 70),
        button_hovered=(90, 90, 90),
        button_active=(120, 120, 120),
        accent=(120, 120, 120),
    )
    manager.add_theme("custom", new_theme)
    theme_ids = manager.get_theme_ids()
    assert "default" in theme_ids
    assert "custom" in theme_ids
