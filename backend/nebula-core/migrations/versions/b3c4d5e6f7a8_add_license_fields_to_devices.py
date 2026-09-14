"""add license fields to devices

Revision ID: b3c4d5e6f7a8
Revises: a2b3c4d5e6f7
Create Date: 2026-09-14

Adiciona o licenciamento ao Device: primeira ativacao concede um trial de
7 dias; depois disso o Device expira ate receber uma licenca anual ou
vitalicia.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "b3c4d5e6f7a8"
down_revision: Union[str, None] = "a2b3c4d5e6f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "devices",
        sa.Column(
            "activated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "devices",
        sa.Column(
            "license_type",
            sa.String(length=32),
            nullable=True,
        ),
    )

    op.add_column(
        "devices",
        sa.Column(
            "license_expires_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("devices", "license_expires_at")
    op.drop_column("devices", "license_type")
    op.drop_column("devices", "activated_at")
