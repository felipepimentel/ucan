#!/usr/bin/env python3
"""
Ponto de entrada principal da aplicação.
"""

import sys

from PySide6.QtWidgets import QApplication

from ucan.controller import AppController
from ucan.ui.main_window import MainWindow


def main():
    """Função principal da aplicação."""
    app = QApplication(sys.argv)
    app.setApplicationName("UCAN")
    app.setApplicationVersion("0.1.0")

    # Criar controlador e janela principal
    controller = AppController()
    window = MainWindow(controller)
    window.show()

    # Iniciar loop de eventos
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
