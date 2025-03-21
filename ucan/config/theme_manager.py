"""
Theme manager proxy module.

This module redirects imports to the actual theme_manager implementation in ucan.ui.theme_manager.
"""

from ucan.ui.theme_manager import Theme, ThemeManager, theme_manager

# Re-export the classes and instances
__all__ = ["Theme", "ThemeManager", "theme_manager"]
