"""
Diálogo de configurações da aplicação.
"""

from typing import Optional

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ucan.config.settings import settings
from ucan.core.utils import clear_cache, logger
from ucan.ui.styles import style_manager


class SettingsDialog(QDialog):
    """Diálogo de configurações da aplicação."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Inicializa o diálogo de configurações.

        Args:
            parent: Widget pai
        """
        super().__init__(parent)
        self.setWindowTitle("Configurações")
        self.resize(600, 400)
        self.setup_ui()

    def setup_ui(self) -> None:
        """Configura a interface do diálogo."""
        layout = QVBoxLayout(self)

        # Abas para diferentes categorias de configurações
        tab_widget = QTabWidget()

        # Aba API
        api_tab = QWidget()
        tab_widget.addTab(api_tab, "API")
        self.setup_api_tab(api_tab)

        # Aba Interface
        interface_tab = QWidget()
        tab_widget.addTab(interface_tab, "Interface")
        self.setup_interface_tab(interface_tab)

        # Aba Avançado
        advanced_tab = QWidget()
        tab_widget.addTab(advanced_tab, "Avançado")
        self.setup_advanced_tab(advanced_tab)

        layout.addWidget(tab_widget)

        # Botões de ação
        button_layout = QHBoxLayout()

        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        save_button = QPushButton("Salvar")
        save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)

    def setup_api_tab(self, tab: QWidget) -> None:
        """
        Configura a aba de configurações de API.

        Args:
            tab: Widget da aba
        """
        layout = QVBoxLayout(tab)

        # Configurações da OpenAI
        openai_group = QGroupBox("OpenAI")
        openai_layout = QFormLayout(openai_group)

        self.openai_api_key = QLineEdit()
        self.openai_api_key.setEchoMode(QLineEdit.Password)
        if settings.OPENAI_API_KEY:
            self.openai_api_key.setText(settings.OPENAI_API_KEY)
            self.openai_api_key.setPlaceholderText("API key já configurada")
        else:
            self.openai_api_key.setPlaceholderText("Digite sua chave de API da OpenAI")

        openai_layout.addRow("Chave de API:", self.openai_api_key)
        layout.addWidget(openai_group)

        # Configurações da Anthropic
        anthropic_group = QGroupBox("Anthropic")
        anthropic_layout = QFormLayout(anthropic_group)

        self.anthropic_api_key = QLineEdit()
        self.anthropic_api_key.setEchoMode(QLineEdit.Password)
        if settings.ANTHROPIC_API_KEY:
            self.anthropic_api_key.setText(settings.ANTHROPIC_API_KEY)
            self.anthropic_api_key.setPlaceholderText("API key já configurada")
        else:
            self.anthropic_api_key.setPlaceholderText(
                "Digite sua chave de API da Anthropic"
            )

        anthropic_layout.addRow("Chave de API:", self.anthropic_api_key)
        layout.addWidget(anthropic_group)

        # Configurações para modelos locais
        local_group = QGroupBox("LLM Local")
        local_layout = QFormLayout(local_group)

        self.local_llm_url = QLineEdit(settings.LOCAL_LLM_URL)
        local_layout.addRow("URL:", self.local_llm_url)

        layout.addWidget(local_group)

        # Espaçador para empurrar os widgets para cima
        layout.addStretch()

    def setup_interface_tab(self, tab: QWidget) -> None:
        """
        Configura a aba de configurações de interface.

        Args:
            tab: Widget da aba
        """
        layout = QVBoxLayout(tab)

        # Configurações de tema
        theme_group = QGroupBox("Tema")
        theme_layout = QFormLayout(theme_group)

        self.dark_mode = QCheckBox("Modo escuro")
        self.dark_mode.setChecked(style_manager.dark_mode)
        theme_layout.addRow("", self.dark_mode)

        self.custom_theme = QCheckBox("Usar tema personalizado")
        self.custom_theme.setChecked(settings.CUSTOM_THEME)
        theme_layout.addRow("", self.custom_theme)

        layout.addWidget(theme_group)

        # Configurações de fonte
        font_group = QGroupBox("Fonte")
        font_layout = QFormLayout(font_group)

        self.font_size = QComboBox()
        for size in range(8, 21, 1):
            self.font_size.addItem(str(size))

        # Selecionando o tamanho atual
        index = self.font_size.findText(str(settings.FONT_SIZE))
        if index >= 0:
            self.font_size.setCurrentIndex(index)

        font_layout.addRow("Tamanho:", self.font_size)
        layout.addWidget(font_group)

        # Configurações gerais da interface
        general_group = QGroupBox("Geral")
        general_layout = QFormLayout(general_group)

        self.save_chat_history = QCheckBox("Salvar histórico de conversas")
        self.save_chat_history.setChecked(settings.SAVE_CHAT_HISTORY)
        general_layout.addRow("", self.save_chat_history)

        layout.addWidget(general_group)

        # Espaçador para empurrar os widgets para cima
        layout.addStretch()

    def setup_advanced_tab(self, tab: QWidget) -> None:
        """
        Configura a aba de configurações avançadas.

        Args:
            tab: Widget da aba
        """
        layout = QVBoxLayout(tab)

        # Configurações de depuração
        debug_group = QGroupBox("Depuração")
        debug_layout = QFormLayout(debug_group)

        self.debug_mode = QCheckBox("Habilitar modo de depuração")
        self.debug_mode.setChecked(settings.DEBUG_MODE)
        debug_layout.addRow("", self.debug_mode)

        layout.addWidget(debug_group)

        # Configurações de cache
        cache_group = QGroupBox("Cache")
        cache_layout = QFormLayout(cache_group)

        self.cache_dir = QLineEdit(str(settings.CACHE_DIR))
        cache_layout.addRow("Diretório:", self.cache_dir)

        clear_cache_button = QPushButton("Limpar Cache")
        clear_cache_button.clicked.connect(self.clear_cache)
        cache_layout.addRow("", clear_cache_button)

        layout.addWidget(cache_group)

        # Espaçador para empurrar os widgets para cima
        layout.addStretch()

    def save_settings(self) -> None:
        """Salva as configurações atualizadas."""
        # Atualizar configurações no objeto settings
        # API
        new_settings = {}
        new_settings["OPENAI_API_KEY"] = (
            self.openai_api_key.text() or settings.OPENAI_API_KEY
        )
        new_settings["ANTHROPIC_API_KEY"] = (
            self.anthropic_api_key.text() or settings.ANTHROPIC_API_KEY
        )
        new_settings["LOCAL_LLM_URL"] = self.local_llm_url.text()

        # Interface
        new_settings["CUSTOM_THEME"] = self.custom_theme.isChecked()
        new_settings["FONT_SIZE"] = int(self.font_size.currentText())
        new_settings["SAVE_CHAT_HISTORY"] = self.save_chat_history.isChecked()

        # Avançado
        new_settings["DEBUG_MODE"] = self.debug_mode.isChecked()
        new_settings["CACHE_DIR"] = self.cache_dir.text()

        # Atualiza o arquivo .env
        try:
            with open(settings.ENV_PATH, "r") as f:
                lines = f.readlines()

            # Atualiza as linhas existentes
            updated_lines = []
            for line in lines:
                if "=" not in line or line.startswith("#"):
                    updated_lines.append(line)
                    continue

                key, _ = line.split("=", 1)
                key = key.strip()

                if key in new_settings:
                    value = new_settings[key]
                    if key in [
                        "OPENAI_API_KEY",
                        "ANTHROPIC_API_KEY",
                        "HF_API_KEY",
                        "LOCAL_LLM_URL",
                        "CACHE_DIR",
                    ]:
                        updated_lines.append(f"{key}={value}\n")
                    elif key in ["DEBUG_MODE", "CUSTOM_THEME", "SAVE_CHAT_HISTORY"]:
                        updated_lines.append(f"{key}={str(value)}\n")
                    elif key in ["FONT_SIZE"]:
                        updated_lines.append(f"{key}={value}\n")
                    else:
                        updated_lines.append(line)
                else:
                    updated_lines.append(line)

            with open(settings.ENV_PATH, "w") as f:
                f.writelines(updated_lines)

            # Atualiza o objeto settings
            for key, value in new_settings.items():
                setattr(settings, key, value)

            # Atualiza o tema
            style_manager.dark_mode = self.dark_mode.isChecked()
            style_manager.custom_theme = self.custom_theme.isChecked()

            logger.info("Configurações salvas com sucesso")
            self.accept()
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")
            QMessageBox.critical(
                self, "Erro", f"Não foi possível salvar as configurações: {str(e)}"
            )

    def clear_cache(self) -> None:
        """Limpa o cache da aplicação."""
        result = clear_cache()
        if result:
            QMessageBox.information(
                self, "Cache Limpo", "O cache da aplicação foi limpo com sucesso."
            )
        else:
            QMessageBox.warning(
                self, "Erro", "Não foi possível limpar o cache da aplicação."
            )
