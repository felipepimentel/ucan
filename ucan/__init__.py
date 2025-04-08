"""
UCAN - Chat com IA
"""

import importlib
import logging
from typing import Callable

# Define version first to avoid circular imports
__version__ = "0.1.0"

# Just get the logger without configuring it
logger = logging.getLogger("UCAN")

# Import after version definition
from .projects import ProjectManager


# Create a function that imports main only when needed to avoid circular imports
def main() -> None:
    """Entry point for the application. Imports the actual main function only when called."""
    # Dynamically import main to avoid circular imports
    from .main import main as _main

    _main()


__all__ = ["ProjectManager", "main"]
