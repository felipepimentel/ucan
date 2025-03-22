"""
Testes para o controlador da aplicação.
"""

from datetime import datetime
from uuid import UUID

from ucan.core.app_controller import AppController, Conversation, Message


def test_create_message():
    """Testa a criação de uma mensagem."""
    message = Message.create("user", "Hello")
    assert isinstance(message.id, UUID)
    assert message.role == "user"
    assert message.content == "Hello"
    assert isinstance(message.timestamp, datetime)


def test_create_conversation():
    """Testa a criação de uma conversa."""
    conversation = Conversation.create("Test")
    assert isinstance(conversation.id, UUID)
    assert conversation.title == "Test"
    assert conversation.messages == []
    assert isinstance(conversation.created_at, datetime)
    assert isinstance(conversation.updated_at, datetime)


def test_app_controller_init():
    """Testa a inicialização do controlador."""
    controller = AppController()
    assert controller._conversations == []
    assert controller._current_conversation is None


def test_create_new_conversation():
    """Testa a criação de uma nova conversa."""
    controller = AppController()
    controller.create_new_conversation()
    assert len(controller._conversations) == 1
    assert controller._current_conversation is not None
    assert controller._current_conversation.title == "Nova Conversa"


def test_select_conversation():
    """Testa a seleção de uma conversa."""
    controller = AppController()
    controller.create_new_conversation()
    conversation = controller._conversations[0]
    controller.select_conversation(conversation.id)
    assert controller._current_conversation == conversation


def test_send_message():
    """Testa o envio de uma mensagem."""
    controller = AppController()
    controller.create_new_conversation()
    controller.send_message("Hello")
    conversation = controller._current_conversation
    assert (
        len(conversation.messages) == 2
    )  # Mensagem do usuário + resposta do assistente
    assert conversation.messages[0].role == "user"
    assert conversation.messages[0].content == "Hello"
    assert conversation.messages[1].role == "assistant"
