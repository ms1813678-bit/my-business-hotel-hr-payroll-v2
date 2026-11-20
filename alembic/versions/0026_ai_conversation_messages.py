"""Persist local AI conversation history.

Revision ID: 0026_ai_conversation_messages
Revises: 0025_manual_attendance_evidence
Create Date: 2026-11-20
"""
from alembic import op
import sqlalchemy as sa


revision = "0026_ai_conversation_messages"
down_revision = "0025_manual_attendance_evidence"
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    if "ai_conversation_messages" not in inspector.get_table_names():
        op.create_table(
            "ai_conversation_messages",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("actor", sa.String(length=80), nullable=False),
            sa.Column("role", sa.String(length=20), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            ),
        )
    indexes = {
        item["name"]
        for item in sa.inspect(op.get_bind()).get_indexes("ai_conversation_messages")
    }
    if "ix_ai_conversation_messages_actor" not in indexes:
        op.create_index(
            "ix_ai_conversation_messages_actor",
            "ai_conversation_messages",
            ["actor"],
            unique=False,
        )


def downgrade():
    # Conversation history is operational data; do not silently destroy it.
    # This migration intentionally retains the table on downgrade.
    pass
