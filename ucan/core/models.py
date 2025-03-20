"""
Modelos de dados para a aplicação UCAN.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional


@dataclass
class Message:
    """Representa uma mensagem em uma conversa."""

    role: str
    content: str
    id: Optional[str] = None
    timestamp: Optional[str] = None

    def __post_init__(self) -> None:
        """Inicializa campos opcionais."""
        if not self.id:
            self.id = str(
                hash(f"{self.role}{self.content}{datetime.now().isoformat()}")
            )
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Converte a mensagem para um dicionário."""
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Message":
        """Cria uma mensagem a partir de um dicionário."""
        return cls(
            id=data.get("id"),
            role=data["role"],
            content=data["content"],
            timestamp=data.get("timestamp"),
        )
