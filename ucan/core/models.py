"""
Modelos SQLAlchemy para o UCAN.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from ucan.core.database import Base


class ConversationType(Base):
    """Modelo para tipos de conversação."""

    __tablename__ = "conversation_types"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    meta_data = Column(JSON)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    conversations = relationship("Conversation", back_populates="type")
    knowledge_bases = relationship(
        "KnowledgeBase",
        primaryjoin="and_(ConversationType.id==KnowledgeBase.scope_id, "
        "KnowledgeBase.scope=='type')",
    )


class Conversation(Base):
    """Modelo para conversas."""

    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title = Column(String(255), nullable=False)
    type_id = Column(String(36), ForeignKey("conversation_types.id"))
    meta_data = Column(JSON)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    type = relationship("ConversationType", back_populates="conversations")
    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )
    knowledge_bases = relationship(
        "KnowledgeBase",
        primaryjoin="and_(Conversation.id==KnowledgeBase.scope_id, "
        "KnowledgeBase.scope=='conversation')",
    )


class Message(Base):
    """Modelo para mensagens."""

    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    meta_data = Column(JSON)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")


class KnowledgeBase(Base):
    """Modelo para bases de conhecimento."""

    __tablename__ = "knowledge_bases"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    scope = Column(String(50), nullable=False)  # global, type, conversation
    scope_id = Column(String(36))
    meta_data = Column(JSON)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    items = relationship(
        "KnowledgeItem", back_populates="base", cascade="all, delete-orphan"
    )


class KnowledgeItem(Base):
    """Modelo para itens de conhecimento."""

    __tablename__ = "knowledge_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    base_id = Column(String(36), ForeignKey("knowledge_bases.id"), nullable=False)
    content_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    meta_data = Column(JSON)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    base = relationship("KnowledgeBase", back_populates="items")
