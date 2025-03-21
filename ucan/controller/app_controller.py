"""
App controller proxy module.

This module redirects imports to the actual app_controller implementation in ucan.core.app_controller.
"""

from ucan.core.app_controller import AppController

# Re-export the class
__all__ = ["AppController"]
