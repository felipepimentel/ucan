"""Initial database schema

Revision ID: 001
Revises: None
Create Date: 2024-03-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create conversation_types table
    op.create_table(
        'conversation_types',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('metadata', sa.JSON),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('type_id', sa.String(36), sa.ForeignKey('conversation_types.id')),
        sa.Column('metadata', sa.JSON),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('conversation_id', sa.String(36), sa.ForeignKey('conversations.id'), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('metadata', sa.JSON),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )

    # Create knowledge_bases table
    op.create_table(
        'knowledge_bases',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('scope', sa.String(50), nullable=False),  # global, type, conversation
        sa.Column('scope_id', sa.String(36)),  # ID of the type or conversation if scoped
        sa.Column('metadata', sa.JSON),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )

    # Create knowledge_items table
    op.create_table(
        'knowledge_items',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('base_id', sa.String(36), sa.ForeignKey('knowledge_bases.id'), nullable=False),
        sa.Column('content_type', sa.String(50), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('metadata', sa.JSON),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )


def downgrade() -> None:
    op.drop_table('knowledge_items')
    op.drop_table('knowledge_bases')
    op.drop_table('messages')
    op.drop_table('conversations')
    op.drop_table('conversation_types') 