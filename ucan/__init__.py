"""
UCAN - Chat com IA
"""

import logging

from .main import main
from .projects import ProjectManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

__version__ = "0.1.0"

__all__ = ["main", "ProjectManager"]
