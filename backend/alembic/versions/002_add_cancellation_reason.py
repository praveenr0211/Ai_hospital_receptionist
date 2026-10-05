"""002_add_cancellation_reason

Revision ID: 002_add_cancellation_reason
Revises: 001_initial_schema
Create Date: 2026-09-25 10:20:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_add_cancellation_reason'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('appointments', sa.Column('cancellation_reason', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('appointments', 'cancellation_reason')
