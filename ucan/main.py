"""
Módulo principal da aplicação UCAN.
"""

import logging
import sys

from ucan.config.constants import CONFIG_DIR
from ucan.core.app_controller import AppController
from ucan.ui.main_window import MainWindow

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(CONFIG_DIR / "ucan.log"),
    ],
)

logger = logging.getLogger(__name__)


def main():
    """Função principal da aplicação."""
    try:
        # Inicializa o controlador
        controller = AppController()

        # Cria e exibe a janela principal
        window = MainWindow(controller)

        # Inicia o loop principal
        window.run()

        # Limpa recursos
        window.cleanup()

    except Exception as e:
        logger.error(f"Erro fatal na aplicação: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
