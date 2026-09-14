"""add activation code to devices

Revision ID: c4d5e6f7a8b9
Revises: b3c4d5e6f7a8
Create Date: 2026-09-14

Codigo curto de ativacao (6 digitos) exibido pelo Player e usado pelo
usuario para entrar no portal web junto com o MAC Address.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "c4d5e6f7a8b9"
down_revision: Union[str, None] = "b3c4d5e6f7a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "devices",
        sa.Column(
            "activation_code",
            sa.String(length=6),
            nullable=True,
        ),
    )

    # Preenche os devices existentes com um codigo aleatorio.
    op.execute(
        "UPDATE devices "
        "SET activation_code = "
        "lpad((floor(random() * 1000000))::int::text, 6, '0') "
        "WHERE activation_code IS NULL"
    )

    op.alter_column("devices", "activation_code", nullable=False)


def downgrade() -> None:
    op.drop_column("devices", "activation_code")
