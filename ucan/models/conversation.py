"""
Conversation model proxy module.

This module redirects imports to the actual conversation implementation in ucan.core.conversation.
"""

from ucan.core.conversation import Conversation

# Re-export the class
__all__ = ["Conversation"]
