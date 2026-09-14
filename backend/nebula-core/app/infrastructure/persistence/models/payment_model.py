from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Index, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.base import Base


class PaymentModel(Base):
    __tablename__ = "payments"

    payment_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        nullable=False,
    )

    device_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    product: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    amount_cents: Mapped[int] = mapped_column(
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
    )

    provider: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    provider_reference: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True,
    )

    provider_payment_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True,
    )

    checkout_url: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        Index("ix_payments_device_status", "device_id", "status"),
    )

    def __repr__(self) -> str:
        return (
            "PaymentModel("
            f"payment_id={self.payment_id!r}, "
            f"product={self.product!r}, "
            f"status={self.status!r}"
            ")"
        )
