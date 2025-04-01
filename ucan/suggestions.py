import logging
from typing import List, Tuple

import emoji

logger = logging.getLogger("UCAN")


class SuggestionsManager:
    def __init__(self, db):
        self.db = db
        self.commands = {
            "/clear": "Limpa o chat",
            "/help": "Mostra ajuda",
            "/export": "Exporta a conversa",
            "/theme": "Alterna tema claro/escuro",
            "/new": "Nova conversa",
            "/template": "Gerencia templates",
        }
        self.emoji_shortcuts = {
            ":)": "😊",
            ":(": "😢",
            ":D": "😃",
            ";)": "😉",
            "<3": "❤️",
            ":+1:": "👍",
            ":thumbsup:": "👍",
            ":smile:": "😊",
            ":laugh:": "😄",
            ":sad:": "😢",
            ":cry:": "😭",
            ":heart:": "❤️",
            ":fire:": "🔥",
            ":check:": "✅",
            ":x:": "❌",
            ":star:": "⭐",
        }

    def get_suggestions(
        self, current_text: str, cursor_position: int
    ) -> List[Tuple[str, str]]:
        """Get suggestions based on current text and cursor position"""
        try:
            # Get text up to cursor
            text_before_cursor = current_text[:cursor_position]
            last_word = (
                text_before_cursor.split()[-1] if text_before_cursor.split() else ""
            )

            suggestions = []

            # Command suggestions
            if last_word.startswith("/"):
                suggestions.extend(self._get_command_suggestions(last_word))

            # Emoji suggestions
            elif last_word.startswith(":"):
                suggestions.extend(self._get_emoji_suggestions(last_word))

            # Message suggestions
            else:
                suggestions.extend(self._get_message_suggestions(text_before_cursor))

            return suggestions[:5]  # Limit to 5 suggestions

        except Exception as e:
            logger.error(f"Error getting suggestions: {str(e)}")
            return []

    def _get_command_suggestions(self, prefix: str) -> List[Tuple[str, str]]:
        """Get command suggestions"""
        return [
            (cmd, desc)
            for cmd, desc in self.commands.items()
            if cmd.startswith(prefix.lower())
        ]

    def _get_emoji_suggestions(self, prefix: str) -> List[Tuple[str, str]]:
        """Get emoji suggestions"""
        # First check shortcuts
        shortcut_suggestions = [
            (shortcut, emoji_char)
            for shortcut, emoji_char in self.emoji_shortcuts.items()
            if shortcut.lower().startswith(prefix.lower())
        ]

        # Then check emoji names
        emoji_suggestions = []
        if len(prefix) > 1:
            search_term = prefix[1:].lower()  # Remove the initial ":"
            emoji_suggestions = [
                (f":{name}:", char)
                for name, char in emoji.EMOJI_DATA.items()
                if search_term in name.lower()
            ]

        return shortcut_suggestions + emoji_suggestions[:10]

    def _get_message_suggestions(self, text: str) -> List[Tuple[str, str]]:
        """Get message suggestions based on history"""
        try:
            # Get similar messages from history
            similar_messages = self.db.search_similar_messages(text)

            # Format suggestions
            suggestions = []
            for msg in similar_messages:
                preview = (
                    msg["content"][:50] + "..."
                    if len(msg["content"]) > 50
                    else msg["content"]
                )
                suggestions.append((msg["content"], f"Histórico: {preview}"))

            return suggestions

        except Exception as e:
            logger.error(f"Error getting message suggestions: {str(e)}")
            return []

    def replace_emoji_shortcuts(self, text: str) -> str:
        """Replace emoji shortcuts with actual emojis"""
        try:
            for shortcut, emoji_char in self.emoji_shortcuts.items():
                text = text.replace(shortcut, emoji_char)
            return text
        except Exception as e:
            logger.error(f"Error replacing emoji shortcuts: {str(e)}")
            return text
