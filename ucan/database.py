import logging
import os
from datetime import datetime

from tinydb import Query, TinyDB

logger = logging.getLogger("UCAN")


class Database:
    """Classe para gerenciar o banco de dados"""

    def __init__(self):
        """Inicializa o banco de dados"""
        # Cria diretório se não existir
        db_dir = os.path.expanduser("~/.ucan")
        os.makedirs(db_dir, exist_ok=True)

        # Inicializa o banco de dados
        db_path = os.path.join(db_dir, "ucan.json")
        self.db = TinyDB(db_path)
        self.messages = self.db.table("messages")

        logger.info("Banco de dados inicializado com sucesso")

    def save_message(self, sender, receiver, content):
        """Salva uma mensagem no banco de dados"""
        try:
            self.messages.insert({
                "sender": sender,
                "receiver": receiver,
                "content": content,
                "timestamp": datetime.now().isoformat(),
            })
        except Exception as e:
            logger.error(f"Erro ao salvar mensagem: {str(e)}")
            raise

    def get_messages(self, contact):
        """Obtém mensagens de uma conversa"""
        try:
            # Obtém todas as mensagens da conversa
            messages = self.messages.search(
                (Query().sender == "Você") & (Query().receiver == contact)
                | (Query().sender == contact) & (Query().receiver == "Você")
            )

            # Ordena por timestamp
            messages.sort(key=lambda x: x["timestamp"])

            return messages
        except Exception as e:
            logger.error(f"Erro ao obter mensagens: {str(e)}")
            raise
