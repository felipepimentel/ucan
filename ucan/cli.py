#!/usr/bin/env python3
"""Script de linha de comando para o aplicativo UCAN."""

import argparse
import sys

from ucan.config.constants import APP_NAME, APP_VERSION
from ucan.utils.utils import logger


def parse_args():
    """Analisa os argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} - Uma interface para LLMs"
    )
    parser.add_argument(
        "--version", action="version", version=f"{APP_NAME} v{APP_VERSION}"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Ativa o modo de depuração"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Nível de log (padrão: INFO)",
    )
    return parser.parse_args()


def main():
    """Função principal do CLI."""
    args = parse_args()

    # Configura o nível de log
    if args.debug:
        logger.setLevel("DEBUG")
    else:
        logger.setLevel(args.log_level)

    # Importa aqui para evitar import circular
    from ucan.__main__ import main as app_main

    # Roda a aplicação
    try:
        return app_main()
    except KeyboardInterrupt:
        logger.info("Aplicação encerrada pelo usuário")
        return 0
    except Exception as e:
        logger.critical(f"Erro fatal: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
