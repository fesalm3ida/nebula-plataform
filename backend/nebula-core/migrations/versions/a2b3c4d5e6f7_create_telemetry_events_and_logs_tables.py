"""create telemetry_events and logs tables

Revision ID: a2b3c4d5e6f7
Revises: 7f9a1b2c3d4e
Create Date: 2026-09-06 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a2b3c4d5e6f7'
down_revision: Union[str, Sequence[str], None] = '7f9a1b2c3d4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('telemetry_events',
    sa.Column('event_id', sa.UUID(), nullable=False),
    sa.Column('session_id', sa.UUID(), nullable=False),
    sa.Column('device_id', sa.UUID(), nullable=False),
    sa.Column('event_type', sa.String(length=64), nullable=False),
    sa.Column('payload', postgresql.JSONB(), nullable=False),
    sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('received_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['device_id'], ['devices.device_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['session_id'], ['sessions.session_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('event_id')
    )
    op.create_index(op.f('ix_telemetry_events_device_id'), 'telemetry_events', ['device_id'], unique=False)
    op.create_index(op.f('ix_telemetry_events_session_id'), 'telemetry_events', ['session_id'], unique=False)
    op.create_index('ix_telemetry_events_device_type', 'telemetry_events', ['device_id', 'event_type'], unique=False)
    op.create_table('logs',
    sa.Column('log_id', sa.UUID(), nullable=False),
    sa.Column('session_id', sa.UUID(), nullable=False),
    sa.Column('device_id', sa.UUID(), nullable=False),
    sa.Column('level', sa.String(length=32), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('received_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['device_id'], ['devices.device_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['session_id'], ['sessions.session_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('log_id')
    )
    op.create_index(op.f('ix_logs_device_id'), 'logs', ['device_id'], unique=False)
    op.create_index(op.f('ix_logs_session_id'), 'logs', ['session_id'], unique=False)
    op.create_index('ix_logs_device_level', 'logs', ['device_id', 'level'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_logs_device_level', table_name='logs')
    op.drop_index(op.f('ix_logs_session_id'), table_name='logs')
    op.drop_index(op.f('ix_logs_device_id'), table_name='logs')
    op.drop_table('logs')
    op.drop_index('ix_telemetry_events_device_type', table_name='telemetry_events')
    op.drop_index(op.f('ix_telemetry_events_session_id'), table_name='telemetry_events')
    op.drop_index(op.f('ix_telemetry_events_device_id'), table_name='telemetry_events')
    op.drop_table('telemetry_events')
