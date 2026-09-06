"""create playlists and playlist_assignments tables

Revision ID: 7f9a1b2c3d4e
Revises: 661d86cc8063
Create Date: 2026-09-05 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f9a1b2c3d4e'
down_revision: Union[str, Sequence[str], None] = '661d86cc8063'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('playlists',
    sa.Column('playlist_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('format', sa.String(length=32), nullable=False),
    sa.Column('source_url', sa.String(length=2048), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('playlist_id')
    )
    op.create_index(op.f('ix_playlists_status'), 'playlists', ['status'], unique=False)
    op.create_table('playlist_assignments',
    sa.Column('assignment_id', sa.UUID(), nullable=False),
    sa.Column('device_id', sa.UUID(), nullable=False),
    sa.Column('playlist_id', sa.UUID(), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['device_id'], ['devices.device_id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['playlist_id'], ['playlists.playlist_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('assignment_id')
    )
    op.create_index(op.f('ix_playlist_assignments_device_id'), 'playlist_assignments', ['device_id'], unique=False)
    op.create_index(op.f('ix_playlist_assignments_playlist_id'), 'playlist_assignments', ['playlist_id'], unique=False)
    op.create_index(op.f('ix_playlist_assignments_status'), 'playlist_assignments', ['status'], unique=False)
    op.create_index('ix_playlist_assignments_device_status', 'playlist_assignments', ['device_id', 'status'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_playlist_assignments_device_status', table_name='playlist_assignments')
    op.drop_index(op.f('ix_playlist_assignments_status'), table_name='playlist_assignments')
    op.drop_index(op.f('ix_playlist_assignments_playlist_id'), table_name='playlist_assignments')
    op.drop_index(op.f('ix_playlist_assignments_device_id'), table_name='playlist_assignments')
    op.drop_table('playlist_assignments')
    op.drop_index(op.f('ix_playlists_status'), table_name='playlists')
    op.drop_table('playlists')
