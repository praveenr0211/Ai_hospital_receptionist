"""003_extend_calls_for_voice

Revision ID: 003_extend_calls_for_voice
Revises: 002_add_cancellation_reason
Create Date: 2026-09-25 15:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '003_extend_calls_for_voice'
down_revision: Union[str, None] = '002_add_cancellation_reason'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('calls', sa.Column('provider', sa.String(50), nullable=True, server_default='exotel'))
    op.add_column('calls', sa.Column('provider_call_id', sa.String(100), nullable=True))
    op.add_column('calls', sa.Column('stream_id', sa.String(100), nullable=True))
    op.add_column('calls', sa.Column('session_id', sa.String(100), nullable=True))
    op.add_column('calls', sa.Column('call_status', sa.String(50), nullable=True, server_default='completed'))
    op.add_column('calls', sa.Column('answered_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('calls', sa.Column('transfer_requested', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('calls', sa.Column('transfer_reason', sa.String(255), nullable=True))
    op.add_column('calls', sa.Column('failure_reason', sa.String(255), nullable=True))
    op.add_column('calls', sa.Column('recording_url', sa.String(500), nullable=True))
    op.add_column('calls', sa.Column('transcript', sa.Text(), nullable=True))

    op.create_index(op.f('ix_calls_provider_call_id'), 'calls', ['provider_call_id'], unique=False)
    op.create_index(op.f('ix_calls_session_id'), 'calls', ['session_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_calls_session_id'), table_name='calls')
    op.drop_index(op.f('ix_calls_provider_call_id'), table_name='calls')
    op.drop_column('calls', 'transcript')
    op.drop_column('calls', 'recording_url')
    op.drop_column('calls', 'failure_reason')
    op.drop_column('calls', 'transfer_reason')
    op.drop_column('calls', 'transfer_requested')
    op.drop_column('calls', 'answered_at')
    op.drop_column('calls', 'call_status')
    op.drop_column('calls', 'session_id')
    op.drop_column('calls', 'stream_id')
    op.drop_column('calls', 'provider_call_id')
    op.drop_column('calls', 'provider')
