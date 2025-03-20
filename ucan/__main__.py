#!/usr/bin/env python3
"""Arquivo principal de entrada para o aplicativo UCAN."""

import asyncio
import gc
import logging
import signal
import sys
import traceback
from pathlib import Path

import qasync
from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from ucan.config.constants import (
    APP_NAME,
    APP_VERSION,
    RESOURCES_DIR,
)
from ucan.config.settings import settings
from ucan.core.app_controller import AppController
from ucan.ui.main_window import MainWindow

# Configurar atributos Qt antes de criar a aplicação
QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

# Configuração de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def signal_handler(signum, frame):
    """Handle termination signals."""
    logger.info(f"Recebido sinal de término ({signum}). Encerrando aplicação...")
    app = QApplication.instance()
    if app:
        app.quit()


def setup_logging() -> None:
    """Configura o sistema de logging."""
    # Configurar o logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(
        logging.DEBUG if settings.get("DEBUG", False) else logging.INFO
    )

    # Criar diretório de logs se não existir
    log_dir = Path(settings.get("LOG_DIR", "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)

    # Handler para arquivo
    file_handler = logging.FileHandler(
        log_dir / f"{APP_NAME.lower()}.log",
        encoding="utf-8",
    )
    file_handler.setLevel(
        logging.DEBUG if settings.get("DEBUG", False) else logging.INFO
    )
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Handler para console em modo de desenvolvimento
    if settings.get("DEBUG", False):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter("%(levelname)s - %(name)s - %(message)s")
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)


def handle_exception(exc_type, exc_value, exc_traceback) -> None:
    """
    Trata exceções não capturadas.

    Args:
        exc_type: Tipo da exceção
        exc_value: Valor da exceção
        exc_traceback: Traceback da exceção
    """
    # Ignorar KeyboardInterrupt
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # Registrar erro
    logger.error(
        "Uncaught exception",
        exc_info=(exc_type, exc_value, exc_traceback),
    )

    # Mostrar diálogo de erro
    error_dialog = QMessageBox()
    error_dialog.setIcon(QMessageBox.Critical)
    error_dialog.setWindowTitle(f"{APP_NAME} - Erro")
    error_dialog.setText("Ocorreu um erro inesperado.")
    error_dialog.setInformativeText(str(exc_value))
    error_dialog.setDetailedText(
        "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    )
    error_dialog.exec_()


def cleanup_qapp() -> None:
    """Limpa a instância existente do QApplication."""
    app = QApplication.instance()
    if app is not None:
        try:
            app.quit()
            app.deleteLater()
            del app
            gc.collect()
            logger.debug("Aplicação Qt limpa com sucesso")
        except Exception as e:
            logger.error(f"Erro ao limpar aplicação Qt: {e}")


async def async_init(window) -> None:
    """Inicializa os componentes assíncronos."""
    try:
        await window.controller.initialize()
    except Exception as e:
        logger.error(f"Erro ao inicializar controlador: {e}")
        raise


def load_styles() -> str:
    """
    Carrega os estilos CSS da aplicação.

    Returns:
        Estilos CSS combinados
    """
    styles_dir = Path(__file__).parent / "ui" / "styles"
    styles = []

    try:
        for css_file in styles_dir.glob("*.css"):
            with open(css_file, "r", encoding="utf-8") as f:
                styles.append(f.read())
    except Exception as e:
        logging.error("Erro ao carregar estilos: %s", e)
        return ""

    return "\n".join(styles)


async def main() -> None:
    """Função principal do aplicativo."""
    logger.info(f"Iniciando {APP_NAME} v{APP_VERSION}")

    # Registra handlers para sinais de término
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        # Configurar logging
        setup_logging()

        # Limpar instância anterior do QApplication
        cleanup_qapp()

        # Criar nova aplicação Qt
        app = QApplication.instance() or QApplication(sys.argv)
        app.setApplicationName(APP_NAME)
        app.setApplicationVersion(APP_VERSION)

        # Configurar ícone da aplicação
        app_icon = QIcon(str(RESOURCES_DIR / "icons" / "app_icon.svg"))
        app.setWindowIcon(app_icon)

        # Configurar estilo
        styles = load_styles()
        if styles:
            app.setStyleSheet(styles)
        logger.debug("Aplicação Qt configurada")

        # Configurar loop de eventos assíncrono
        loop = qasync.QEventLoop(app)
        qasync.asyncio.set_event_loop(loop)

        # Criar controlador
        controller = AppController()
        logger.debug("Controlador criado")

        # Criar janela principal
        window = MainWindow(controller)
        window.show()
        logger.debug("Janela principal criada e exibida")

        # Inicializar componentes assíncronos
        loop.run_until_complete(async_init(window))
        logger.debug("Controlador inicializado")

        # Executar aplicação
        with loop:
            sys.exit(loop.run_forever())
    except Exception as e:
        logger.error(f"Erro ao iniciar aplicação: {e}", exc_info=True)
        cleanup_qapp()  # Ensure cleanup on error
        sys.exit(1)
    finally:
        logger.info("Aplicação encerrada")


if __name__ == "__main__":
    # Configurar tratamento de exceções
    sys.excepthook = handle_exception

    # Executar aplicação
    try:
        asyncio.run(main())
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao iniciar aplicação: {e}", exc_info=True)
        cleanup_qapp()  # Ensure cleanup on error
        sys.exit(1)
