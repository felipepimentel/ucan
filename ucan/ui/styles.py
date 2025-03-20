"""
Estilos e temas para a interface do usuário.
"""

from PySide6.QtCore import QObject

from ucan.config.settings import settings


class StyleManager(QObject):
    """Gerencia estilos e temas da aplicação."""

    def __init__(self) -> None:
        """Inicializa o gerenciador de estilos."""
        super().__init__()
        self.dark_mode = settings.get("DARK_THEME", True)
        self.custom_theme = settings.get("CUSTOM_THEME", True)

    def get_theme_stylesheet(self) -> str:
        """
        Retorna o stylesheet do tema atual.

        Returns:
            str: Stylesheet CSS
        """
        return """
            /* Global Styles */
            * {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
                    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
            }

            QWidget {
                background-color: #1a1b26;
                color: #a9b1d6;
            }

            /* Main Window */
            QMainWindow {
                background-color: #1a1b26;
            }

            /* Menu Bar */
            QMenuBar {
                background-color: #24283b;
                color: #a9b1d6;
                border-bottom: 1px solid #32344a;
                padding: 4px;
            }

            QMenuBar::item {
                background-color: transparent;
                padding: 4px 8px;
                border-radius: 4px;
            }

            QMenuBar::item:selected {
                background-color: #414868;
            }

            QMenu {
                background-color: #24283b;
                border: 1px solid #32344a;
                border-radius: 6px;
                padding: 4px;
            }

            QMenu::item {
                padding: 8px 24px;
                border-radius: 4px;
            }

            QMenu::item:selected {
                background-color: #414868;
            }

            /* Dialog */
            QDialog {
                background-color: #1a1b26;
                border: 1px solid #32344a;
                border-radius: 8px;
            }

            /* Buttons */
            QPushButton {
                background-color: #7aa2f7;
                color: #1a1b26;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #89b4fa;
            }

            QPushButton:pressed {
                background-color: #6c91e4;
            }

            QPushButton:disabled {
                background-color: #414868;
                color: #565f89;
            }

            /* Scrollbar Styling */
            QScrollBar:vertical {
                border: none;
                background: #1a1b26;
                width: 8px;
                margin: 0;
            }

            QScrollBar::handle:vertical {
                background: #414868;
                border-radius: 4px;
                min-height: 20px;
            }

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }

            /* Messages Area */
            #messagesArea {
                background-color: #1a1b26;
                border: none;
            }

            #messagesArea QScrollBar:vertical {
                width: 6px;
                margin: 0;
            }

            #messagesArea QScrollBar::handle:vertical {
                background: #414868;
                border-radius: 3px;
                min-height: 30px;
            }

            #messagesArea QScrollBar::add-line:vertical,
            #messagesArea QScrollBar::sub-line:vertical {
                height: 0;
            }

            #messagesArea QScrollBar::add-page:vertical,
            #messagesArea QScrollBar::sub-page:vertical {
                background: none;
            }

            #messagesWidget {
                background-color: transparent;
                padding: 12px;
            }

            /* Message Container */
            #messageContainer {
                background-color: #24283b;
                border-radius: 12px;
                border: 1px solid #32344a;
                margin: 4px 0;
                max-width: 85%;
                transition: all 0.2s ease-in-out;
            }

            #messageContainer:hover {
                border-color: #414868;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            }

            #message_assistant #messageContainer {
                background-color: #1f2335;
                margin-right: auto;
                margin-left: 32px;
            }

            #message_user #messageContainer {
                background-color: #2a2e44;
                margin-left: auto;
                margin-right: 32px;
            }

            /* Message Header */
            #messageHeader {
                background-color: transparent;
                min-height: 24px;
                padding: 4px 0;
            }

            #roleContainer {
                background-color: transparent;
                padding: 2px 4px;
                border-radius: 4px;
            }

            #message_assistant #roleContainer {
                background-color: rgba(122, 162, 247, 0.1);
            }

            #message_user #roleContainer {
                background-color: rgba(247, 118, 142, 0.1);
            }

            #roleIcon {
                min-width: 20px;
                min-height: 20px;
                margin-right: 4px;
            }

            #roleName {
                font-weight: 600;
                font-size: 13px;
            }

            #message_assistant #roleName {
                color: #7aa2f7;
            }

            #message_user #roleName {
                color: #f7768e;
            }

            #metaContainer {
                background-color: transparent;
                padding: 2px 4px;
            }

            #timestampLabel {
                color: #565f89;
                font-size: 11px;
            }

            #statusIcon {
                min-width: 14px;
                min-height: 14px;
                margin-left: 4px;
            }

            /* Message Content */
            #messageContent {
                color: #c0caf5;
                font-size: 14px;
                line-height: 1.5;
                padding: 4px 0;
            }

            #messageContent a {
                color: #7aa2f7;
                text-decoration: none;
            }

            #messageContent a:hover {
                text-decoration: underline;
            }

            #messageContent code {
                background-color: #1a1b26;
                padding: 2px 4px;
                border-radius: 4px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 13px;
            }

            #messageContent pre {
                background-color: #1a1b26;
                padding: 12px;
                border-radius: 8px;
                border: 1px solid #32344a;
                margin: 8px 0;
                overflow-x: auto;
            }

            #messageContent pre code {
                background-color: transparent;
                padding: 0;
                border-radius: 0;
                font-family: 'JetBrains Mono', monospace;
                font-size: 13px;
            }

            #messageContent blockquote {
                border-left: 4px solid #414868;
                margin: 8px 0;
                padding: 4px 12px;
                color: #9aa5ce;
            }

            #messageContent ul, #messageContent ol {
                margin: 8px 0;
                padding-left: 24px;
            }

            #messageContent li {
                margin: 4px 0;
            }

            #messageContent p {
                margin: 8px 0;
            }

            #messageContent h1, #messageContent h2, #messageContent h3,
            #messageContent h4, #messageContent h5, #messageContent h6 {
                color: #c0caf5;
                margin: 16px 0 8px 0;
                font-weight: 600;
            }

            #messageContent h1 { font-size: 24px; }
            #messageContent h2 { font-size: 20px; }
            #messageContent h3 { font-size: 18px; }
            #messageContent h4 { font-size: 16px; }
            #messageContent h5 { font-size: 14px; }
            #messageContent h6 { font-size: 13px; }

            #messageContent table {
                border-collapse: collapse;
                margin: 8px 0;
                width: 100%;
            }

            #messageContent th, #messageContent td {
                border: 1px solid #32344a;
                padding: 8px;
                text-align: left;
            }

            #messageContent th {
                background-color: #1f2335;
                font-weight: 600;
            }

            #messageContent tr:nth-child(even) {
                background-color: #1a1b26;
            }

            #messageContent tr:hover {
                background-color: #24283b;
            }

            #messageContent img {
                max-width: 100%;
                border-radius: 8px;
                margin: 8px 0;
            }

            #messageContent hr {
                border: none;
                border-top: 1px solid #32344a;
                margin: 16px 0;
            }

            /* Input Container */
            #inputContainer {
                background-color: #24283b;
                border-top: 1px solid #32344a;
                padding: 8px;
            }

            /* Input Widget */
            #inputWidget {
                background-color: transparent;
            }

            /* Input Text */
            #inputText {
                background-color: #1f2335;
                color: #c0caf5;
                border: 1px solid #32344a;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                line-height: 1.5;
                min-height: 36px;
                max-height: 120px;
            }

            #inputText:hover {
                border-color: #414868;
                background-color: #1a1b26;
            }

            #inputText:focus {
                border-color: #7aa2f7;
                background-color: #1a1b26;
            }

            #inputText::placeholder {
                color: #565f89;
                font-style: italic;
            }

            /* Send Button */
            #sendButton {
                background-color: #7aa2f7;
                border-radius: 8px;
                padding: 8px;
                margin: 0;
                min-width: 36px;
                min-height: 36px;
            }

            #sendButton:hover {
                background-color: #89b4fa;
            }

            #sendButton:pressed {
                background-color: #6c91e4;
            }

            #sendButton:disabled {
                background-color: #414868;
                opacity: 0.7;
            }

            /* Character Counter */
            #charCounter {
                color: #565f89;
                font-size: 11px;
                padding: 0 4px;
            }

            #charCounter[warning="true"] {
                color: #f7768e;
            }

            /* Counter Label */
            #counterLabel {
                color: #565f89;
                font-size: 11px;
                margin-top: 2px;
            }

            /* Date Separator */
            #dateSeparator {
                background-color: transparent;
                margin: 8px 0;
            }

            #separatorLine {
                background-color: #32344a;
                max-height: 1px;
            }

            #separatorText {
                color: #565f89;
                font-size: 12px;
                padding: 0 12px;
                font-weight: 500;
            }

            /* Conversation List */
            #conversationList {
                background-color: #24283b;
                border-right: 1px solid #32344a;
                min-width: 260px;
                max-width: 300px;
            }

            #conversationHeader {
                background-color: transparent;
                padding: 12px 16px;
                border-bottom: 1px solid #32344a;
            }

            #conversationTitle {
                color: #c0caf5;
                font-size: 16px;
                font-weight: 600;
            }

            #conversationSearch {
                margin: 8px 12px;
                padding: 6px 10px;
                background-color: #1a1b26;
                border: 1px solid #32344a;
                border-radius: 6px;
                color: #a9b1d6;
                font-size: 13px;
            }

            #conversationSearch:focus {
                border-color: #7aa2f7;
            }

            #conversationItem {
                padding: 10px 12px;
                border-radius: 6px;
                margin: 2px 6px;
            }

            #conversationItem:hover {
                background-color: #2a2e44;
            }

            #conversationItem[selected="true"] {
                background-color: #414868;
            }

            #conversationItemTitle {
                color: #c0caf5;
                font-weight: 600;
                font-size: 13px;
                margin-bottom: 2px;
            }

            #conversationItemPreview {
                color: #565f89;
                font-size: 12px;
                line-height: 1.3;
            }

            #conversationItemTime {
                color: #565f89;
                font-size: 11px;
                margin-top: 2px;
            }

            #conversationItemBadge {
                background-color: #f7768e;
                color: #1a1b26;
                border-radius: 8px;
                padding: 1px 5px;
                font-size: 11px;
                font-weight: 600;
                min-width: 16px;
                text-align: center;
            }

            #charCounter {
                color: #565f89;
                font-size: 11px;
                padding: 0 4px;
            }

            /* Format Bar */
            #formatBar {
                background-color: transparent;
                border-bottom: 1px solid #32344a;
                padding: 4px 0;
            }

            #formatBar QToolTip {
                background-color: #24283b;
                color: #c0caf5;
                border: 1px solid #32344a;
                border-radius: 4px;
                padding: 4px 8px;
            }
        """

    def get_stylesheet(self) -> str:
        """
        Retorna a folha de estilos da aplicação.
        Mantido para compatibilidade.

        Returns:
            Folha de estilos CSS
        """
        return self.get_theme_stylesheet()

    def toggle_theme(self) -> None:
        """Alterna entre os temas claro e escuro."""
        self.dark_mode = not self.dark_mode


# Instância única do gerenciador de estilos para uso em toda a aplicação
style_manager = StyleManager()
