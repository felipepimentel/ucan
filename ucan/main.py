import logging
import os
import sys
from tkinter import messagebox

from .ui import ChatApp

logger = logging.getLogger("UCAN")


def setup_logging():
    """Configura o sistema de logging"""
    try:
        # Cria diretório de logs
        log_dir = os.path.expanduser("~/.ucan/logs")
        os.makedirs(log_dir, exist_ok=True)

        # Configura logging
        log_file = os.path.join(log_dir, "ucan.log")
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
        )
    except Exception as e:
        print(f"Erro ao configurar logging: {str(e)}")
        sys.exit(1)


def main():
    """Função principal da aplicação"""
    try:
        # Configura o logger
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler("ucan.log"),
                logging.StreamHandler(),
            ],
        )
        logger = logging.getLogger("UCAN")

        # Inicia a aplicação
        app = ChatApp()
        app.mainloop()

    except Exception as e:
        logger.error(f"Erro ao iniciar aplicação: {str(e)}")
        messagebox.showerror(
            "Erro",
            "Não foi possível iniciar a aplicação. Verifique o arquivo de log para mais detalhes.",
        )


if __name__ == "__main__":
    main()

__all__ = ["main"]
