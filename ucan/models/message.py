"""
Message model proxy module.

This module redirects imports to the actual message implementation in ucan.core.message.
"""

from ucan.core.message import Message, MessageType

# Re-export the classes
__all__ = ["Message", "MessageType"]
