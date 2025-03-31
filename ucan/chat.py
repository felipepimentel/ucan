import json
import random
from datetime import datetime
from typing import Dict, List, Optional

from .constants import BOT_RESPONSES, COMMON_REACTIONS


class Chat:
    """Classe que gerencia a lógica do chat"""

    def __init__(self, history_file: str):
        self.history_file = history_file
        self.messages = self.load_history()
        self.current_contact = "ChatBot"
        self.typing = False

    def load_history(self) -> List[Dict]:
        """Carrega o histórico de mensagens"""
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_history(self):
        """Salva o histórico de mensagens"""
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.messages, f, ensure_ascii=False, indent=2)

    def add_message(
        self,
        message: str,
        is_user: bool = True,
        timestamp: Optional[str] = None,
        avatar: Optional[str] = None,
    ) -> Dict:
        """Adiciona uma nova mensagem ao histórico"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        msg = {
            "message": message,
            "is_user": is_user,
            "timestamp": timestamp,
            "avatar": avatar,
        }
        self.messages.append(msg)
        self.save_history()
        return msg

    def get_bot_response(self, message: str) -> str:
        """Gera uma resposta do bot baseada na mensagem do usuário"""
        # Verificar se a mensagem contém palavras-chave
        message = message.lower()
        for keyword, response in BOT_RESPONSES.items():
            if keyword in message:
                return response

        # Se não encontrar palavras-chave, retorna uma resposta aleatória
        return random.choice(list(BOT_RESPONSES.values()))

    def get_reactions(self) -> List[str]:
        """Retorna as reações disponíveis"""
        return COMMON_REACTIONS

    def clear_history(self):
        """Limpa o histórico de mensagens"""
        self.messages = []
        self.save_history()

    def get_messages_by_contact(self, contact: str) -> List[Dict]:
        """Retorna as mensagens de um contato específico"""
        return [msg for msg in self.messages if msg.get("contact") == contact]

    def set_current_contact(self, contact: str):
        """Define o contato atual"""
        self.current_contact = contact

    def set_typing(self, is_typing: bool):
        """Define o status de digitação"""
        self.typing = is_typing

    def is_typing(self) -> bool:
        """Retorna o status de digitação"""
        return self.typing
