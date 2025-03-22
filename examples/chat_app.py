"""
Exemplo de uso da aplicação UCAN.
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from ucan.config.theme_manager import theme_manager
from ucan.core.app_controller import AppController
from ucan.ui.main_window import MainWindow


def main():
    """Função principal do exemplo."""
    try:
        # Inicializa o controlador
        controller = AppController()

        # Cria e exibe a janela principal
        window = MainWindow(controller)

        # Aplica o tema padrão
        theme_manager.apply_theme()

        # Inicia o loop principal
        window.run()

        # Limpa recursos
        window.cleanup()

    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
