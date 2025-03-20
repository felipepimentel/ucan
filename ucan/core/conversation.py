"""
Gerenciador de conversas e histórico de mensagens.
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ucan.config.settings import settings
from ucan.core.models import Message


class Conversation:
    """Gerencia uma conversa com um LLM, incluindo o histórico de mensagens."""

    def __init__(
        self,
        id: Optional[str] = None,
        title: str = "Nova Conversa",
        system_prompt: Optional[str] = None,
    ) -> None:
        """
        Inicializa uma nova conversa.

        Args:
            id: Identificador único da conversa (gera um novo se não fornecido)
            title: Título da conversa
            system_prompt: Prompt inicial do sistema (opcional)
        """
        self.id = id or str(uuid.uuid4())
        self.title = title
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.messages: List[Message] = []

        # Adiciona o prompt do sistema se fornecido
        if system_prompt:
            self.add_message("system", system_prompt)

    def add_message(self, role: str, content: str) -> Message:
        """
        Adiciona uma nova mensagem à conversa.

        Args:
            role: Papel do remetente (user, assistant, system)
            content: Conteúdo da mensagem

        Returns:
            A mensagem criada
        """
        message = Message(role=role, content=content)
        self.messages.append(message)
        self.updated_at = datetime.now().isoformat()
        return message

    def clear_messages(self) -> None:
        """Remove todas as mensagens, mantendo apenas o prompt do sistema se existir."""
        system_messages = [m for m in self.messages if m.role == "system"]
        self.messages = system_messages

    def to_dict(self) -> Dict:
        """Converte a conversa para um dicionário."""
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "messages": [message.to_dict() for message in self.messages],
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Conversation":
        """Cria uma conversa a partir de um dicionário."""
        conversation = cls(
            id=data.get("id"),
            title=data.get("title", "Conversa Importada"),
        )
        conversation.created_at = data.get("created_at", conversation.created_at)
        conversation.updated_at = data.get("updated_at", conversation.updated_at)
        conversation.messages = [
            Message.from_dict(msg) for msg in data.get("messages", [])
        ]
        return conversation

    def save(self) -> Path:
        """
        Salva a conversa em um arquivo JSON.

        Returns:
            Caminho do arquivo salvo
        """
        if not settings.SAVE_CHAT_HISTORY:
            return Path()

        conversations_dir = settings.CONVERSATIONS_DIR
        conversations_dir.mkdir(parents=True, exist_ok=True)

        # Cria um nome de arquivo seguro baseado no título e data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(
            c if c.isalnum() or c in " -_" else "_" for c in self.title
        )
        file_name = f"{safe_title}_{timestamp}.json"
        file_path = conversations_dir / file_name

        # Salva a conversa
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

        return file_path

    def export(self, export_path: Path) -> bool:
        """
        Exporta a conversa para um arquivo JSON.

        Args:
            export_path: Caminho para exportar a conversa

        Returns:
            True se a exportação foi bem sucedida, False caso contrário
        """
        try:
            # Garante que o diretório existe
            os.makedirs(os.path.dirname(str(export_path)), exist_ok=True)

            # Exporta a conversa
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=2)
            return True
        except Exception:
            return False

    @classmethod
    def import_from_file(cls, import_path: Path) -> Optional["Conversation"]:
        """
        Importa uma conversa de um arquivo JSON.

        Args:
            import_path: Caminho do arquivo a ser importado

        Returns:
            A conversa importada ou None se falhou
        """
        try:
            with open(import_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception:
            return None

    @classmethod
    def load(cls, conversation_id: str) -> Optional["Conversation"]:
        """
        Carrega uma conversa de um arquivo JSON.

        Args:
            conversation_id: ID da conversa a ser carregada

        Returns:
            A conversa carregada ou None se não encontrada
        """
        if not settings.SAVE_CHAT_HISTORY:
            return None

        conversations_dir = settings.CONVERSATIONS_DIR
        if not conversations_dir.exists():
            return None

        # Procura por arquivos que contenham o ID no nome
        for file_path in conversations_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("id") == conversation_id:
                        return cls.from_dict(data)
            except (json.JSONDecodeError, KeyError):
                continue

        return None

    @classmethod
    def list_all(cls) -> List[Dict]:
        """
        Lista todas as conversas salvas.

        Returns:
            Lista de dicionários com os metadados das conversas
        """
        if not settings.SAVE_CHAT_HISTORY:
            return []

        conversations_dir = settings.CONVERSATIONS_DIR
        if not conversations_dir.exists():
            return []

        conversations = []
        for file_path in conversations_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    conversations.append(data)
            except (json.JSONDecodeError, KeyError):
                continue

        # Ordena por data de atualização (mais recente primeiro)
        conversations.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return conversations

    @classmethod
    def delete(cls, conversation_id: str) -> bool:
        """
        Exclui uma conversa.

        Args:
            conversation_id: ID da conversa a ser excluída

        Returns:
            True se a conversa foi excluída com sucesso, False caso contrário
        """
        if not settings.SAVE_CHAT_HISTORY:
            return False

        conversations_dir = settings.CONVERSATIONS_DIR
        if not conversations_dir.exists():
            return False

        # Procura por arquivos que contenham o ID no nome
        for file_path in conversations_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("id") == conversation_id:
                        file_path.unlink()
                        return True
            except (json.JSONDecodeError, KeyError):
                continue

        return False
