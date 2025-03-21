"""
Knowledge base model proxy module.

This module redirects imports to the actual knowledge_base implementation in ucan.core.knowledge_base.
"""

from ucan.core.knowledge_base import KnowledgeBase

# Re-export the class
__all__ = ["KnowledgeBase"]
