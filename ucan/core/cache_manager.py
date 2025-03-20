"""
Gerenciador de cache para otimização de performance.
"""

import json
import logging
import lzma
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set

from ucan.config.settings import settings
from ucan.core.models import Message

logger = logging.getLogger(__name__)

class CacheManager:
    """Gerenciador de cache para otimização de performance."""

    def __init__(self) -> None:
        """Inicializa o gerenciador de cache."""
        self.cache_dir = settings.CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.conversation_cache: Dict[str, Dict] = {}
        self.message_cache: Dict[str, List[Message]] = {}
        self.loaded_conversations: Set[str] = set()
        self.cache_ttl = timedelta(hours=24)
        self._setup_cache_dirs()

    def _setup_cache_dirs(self) -> None:
        """Configura os diretórios de cache."""
        (self.cache_dir / "conversations").mkdir(exist_ok=True)
        (self.cache_dir / "messages").mkdir(exist_ok=True)
        (self.cache_dir / "offline").mkdir(exist_ok=True)

    def get_conversation_cache_path(self, conversation_id: str) -> Path:
        """Retorna o caminho do cache para uma conversa."""
        return self.cache_dir / "conversations" / f"{conversation_id}.xz"

    def get_messages_cache_path(self, conversation_id: str) -> Path:
        """Retorna o caminho do cache para mensagens de uma conversa."""
        return self.cache_dir / "messages" / f"{conversation_id}.xz"

    def cache_conversation(self, conversation_id: str, data: Dict) -> None:
        """
        Armazena uma conversa em cache.

        Args:
            conversation_id: ID da conversa
            data: Dados da conversa
        """
        try:
            cache_path = self.get_conversation_cache_path(conversation_id)
            with lzma.open(cache_path, "wt", encoding="utf-8") as f:
                json.dump({
                    "data": data,
                    "timestamp": datetime.utcnow().isoformat(),
                }, f)
            self.conversation_cache[conversation_id] = data
            self.loaded_conversations.add(conversation_id)
        except Exception as e:
            logger.error(f"Erro ao armazenar conversa em cache: {e}")

    def cache_messages(self, conversation_id: str, messages: List[Message]) -> None:
        """
        Armazena mensagens em cache.

        Args:
            conversation_id: ID da conversa
            messages: Lista de mensagens
        """
        try:
            cache_path = self.get_messages_cache_path(conversation_id)
            with lzma.open(cache_path, "wt", encoding="utf-8") as f:
                json.dump({
                    "messages": [msg.to_dict() for msg in messages],
                    "timestamp": datetime.utcnow().isoformat(),
                }, f)
            self.message_cache[conversation_id] = messages
        except Exception as e:
            logger.error(f"Erro ao armazenar mensagens em cache: {e}")

    def get_cached_conversation(self, conversation_id: str) -> Optional[Dict]:
        """
        Obtém uma conversa do cache.

        Args:
            conversation_id: ID da conversa

        Returns:
            Dados da conversa ou None se não encontrada/expirada
        """
        # Primeiro tenta memória
        if conversation_id in self.conversation_cache:
            return self.conversation_cache[conversation_id]

        # Depois tenta arquivo
        try:
            cache_path = self.get_conversation_cache_path(conversation_id)
            if not cache_path.exists():
                return None

            with lzma.open(cache_path, "rt", encoding="utf-8") as f:
                cached = json.load(f)
                timestamp = datetime.fromisoformat(cached["timestamp"])
                
                # Verifica TTL
                if datetime.utcnow() - timestamp > self.cache_ttl:
                    return None

                self.conversation_cache[conversation_id] = cached["data"]
                return cached["data"]
        except Exception as e:
            logger.error(f"Erro ao ler conversa do cache: {e}")
            return None

    def get_cached_messages(self, conversation_id: str) -> Optional[List[Message]]:
        """
        Obtém mensagens do cache.

        Args:
            conversation_id: ID da conversa

        Returns:
            Lista de mensagens ou None se não encontrada/expirada
        """
        # Primeiro tenta memória
        if conversation_id in self.message_cache:
            return self.message_cache[conversation_id]

        # Depois tenta arquivo
        try:
            cache_path = self.get_messages_cache_path(conversation_id)
            if not cache_path.exists():
                return None

            with lzma.open(cache_path, "rt", encoding="utf-8") as f:
                cached = json.load(f)
                timestamp = datetime.fromisoformat(cached["timestamp"])
                
                # Verifica TTL
                if datetime.utcnow() - timestamp > self.cache_ttl:
                    return None

                messages = [Message(**msg) for msg in cached["messages"]]
                self.message_cache[conversation_id] = messages
                return messages
        except Exception as e:
            logger.error(f"Erro ao ler mensagens do cache: {e}")
            return None

    def clear_conversation_cache(self, conversation_id: str) -> None:
        """
        Limpa o cache de uma conversa.

        Args:
            conversation_id: ID da conversa
        """
        try:
            if conversation_id in self.conversation_cache:
                del self.conversation_cache[conversation_id]
            if conversation_id in self.loaded_conversations:
                self.loaded_conversations.remove(conversation_id)
            
            cache_path = self.get_conversation_cache_path(conversation_id)
            if cache_path.exists():
                cache_path.unlink()
        except Exception as e:
            logger.error(f"Erro ao limpar cache da conversa: {e}")

    def clear_messages_cache(self, conversation_id: str) -> None:
        """
        Limpa o cache de mensagens de uma conversa.

        Args:
            conversation_id: ID da conversa
        """
        try:
            if conversation_id in self.message_cache:
                del self.message_cache[conversation_id]
            
            cache_path = self.get_messages_cache_path(conversation_id)
            if cache_path.exists():
                cache_path.unlink()
        except Exception as e:
            logger.error(f"Erro ao limpar cache de mensagens: {e}")

    def clear_all_cache(self) -> None:
        """Limpa todo o cache."""
        try:
            self.conversation_cache.clear()
            self.message_cache.clear()
            self.loaded_conversations.clear()
            
            for cache_dir in ["conversations", "messages", "offline"]:
                for cache_file in (self.cache_dir / cache_dir).glob("*.xz"):
                    cache_file.unlink()
        except Exception as e:
            logger.error(f"Erro ao limpar todo o cache: {e}")

    def prepare_offline_cache(self, conversation_ids: List[str]) -> None:
        """
        Prepara cache offline para um conjunto de conversas.

        Args:
            conversation_ids: Lista de IDs de conversas para cachear
        """
        try:
            offline_dir = self.cache_dir / "offline"
            offline_dir.mkdir(exist_ok=True)

            for conv_id in conversation_ids:
                # Cache da conversa
                if conv_data := self.get_cached_conversation(conv_id):
                    offline_path = offline_dir / f"conv_{conv_id}.xz"
                    with lzma.open(offline_path, "wt", encoding="utf-8") as f:
                        json.dump(conv_data, f)

                # Cache das mensagens
                if messages := self.get_cached_messages(conv_id):
                    offline_path = offline_dir / f"msgs_{conv_id}.xz"
                    with lzma.open(offline_path, "wt", encoding="utf-8") as f:
                        json.dump([msg.to_dict() for msg in messages], f)
        except Exception as e:
            logger.error(f"Erro ao preparar cache offline: {e}")

    def load_offline_cache(self) -> None:
        """Carrega cache offline para memória."""
        try:
            offline_dir = self.cache_dir / "offline"
            if not offline_dir.exists():
                return

            # Carrega conversas
            for conv_file in offline_dir.glob("conv_*.xz"):
                try:
                    conv_id = conv_file.stem[5:]  # Remove 'conv_' prefix
                    with lzma.open(conv_file, "rt", encoding="utf-8") as f:
                        self.conversation_cache[conv_id] = json.load(f)
                except Exception as e:
                    logger.error(f"Erro ao carregar conversa offline {conv_file}: {e}")

            # Carrega mensagens
            for msg_file in offline_dir.glob("msgs_*.xz"):
                try:
                    conv_id = msg_file.stem[5:]  # Remove 'msgs_' prefix
                    with lzma.open(msg_file, "rt", encoding="utf-8") as f:
                        messages_data = json.load(f)
                        self.message_cache[conv_id] = [Message(**msg) for msg in messages_data]
                except Exception as e:
                    logger.error(f"Erro ao carregar mensagens offline {msg_file}: {e}")
        except Exception as e:
            logger.error(f"Erro ao carregar cache offline: {e}")

# Instância global do gerenciador de cache
cache_manager = CacheManager() 