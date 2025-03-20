"""
Modelos de dados para a aplicação UCAN.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict


@dataclass
class Message:
    """Representa uma mensagem em uma conversa."""

    role: str
    content: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """
        Converte a mensagem para um dicionário.

        Returns:
            Dicionário com os dados da mensagem
        """
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Message":
        """
        Cria uma mensagem a partir de um dicionário.

        Args:
            data: Dicionário com os dados da mensagem

        Returns:
            Mensagem criada
        """
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            role=data["role"],
            content=data["content"],
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            metadata=data.get("metadata", {}),
        )
