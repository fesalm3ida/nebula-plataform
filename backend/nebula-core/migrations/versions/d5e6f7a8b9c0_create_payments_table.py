"""create payments table

Revision ID: d5e6f7a8b9c0
Revises: c4d5e6f7a8b9
Create Date: 2026-09-14

Pagamentos de licenca (1 ano / vitalicia) feitos pelo usuario no portal.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "d5e6f7a8b9c0"
down_revision: Union[str, None] = "c4d5e6f7a8b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "payments",
        sa.Column(
            "payment_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "device_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("product", sa.String(length=32), nullable=False),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column(
            "provider_reference",
            sa.String(length=128),
            nullable=True,
        ),
        sa.Column(
            "provider_payment_id",
            sa.String(length=128),
            nullable=True,
        ),
        sa.Column(
            "checkout_url",
            sa.String(length=512),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "approved_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_payments_device_id",
        "payments",
        ["device_id"],
    )
    op.create_index(
        "ix_payments_status",
        "payments",
        ["status"],
    )
    op.create_index(
        "ix_payments_provider_reference",
        "payments",
        ["provider_reference"],
    )
    op.create_index(
        "ix_payments_provider_payment_id",
        "payments",
        ["provider_payment_id"],
    )
    op.create_index(
        "ix_payments_device_status",
        "payments",
        ["device_id", "status"],
    )


def downgrade() -> None:
    op.drop_table("payments")
