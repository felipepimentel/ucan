"""
Módulo de mensagens do chat.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Optional


class MessageType(Enum):
    """Tipos de mensagem."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message:
    """Classe que representa uma mensagem."""

    def __init__(
        self,
        content: str,
        type: MessageType,
        timestamp: Optional[datetime] = None,
        message_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        """
        Inicializa uma mensagem.

        Args:
            content: Conteúdo da mensagem
            type: Tipo da mensagem (user, assistant, system)
            timestamp: Data/hora da mensagem (opcional)
            message_id: ID da mensagem (opcional)
            metadata: Metadados adicionais (opcional)
        """
        self.content = content
        self.type = type
        self.timestamp = timestamp or datetime.utcnow()
        self.id = message_id or str(uuid.uuid4())
        self.metadata = metadata or {}

    def to_dict(self) -> Dict:
        """
        Converte a mensagem para dicionário.

        Returns:
            Dicionário com os dados da mensagem
        """
        return {
            "id": self.id,
            "content": self.content,
            "type": self.type.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Message":
        """
        Cria uma mensagem a partir de um dicionário.

        Args:
            data: Dicionário com os dados da mensagem

        Returns:
            Nova instância de Message
        """
        return cls(
            content=data["content"],
            type=MessageType(data["type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            message_id=data["id"],
            metadata=data.get("metadata", {}),
        )
