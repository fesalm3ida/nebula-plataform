from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Index, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.base import Base


class DeviceModel(Base):
    __tablename__ = "devices"

    device_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        nullable=False,
    )

    fingerprint: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
    )

    mac_address: Mapped[str] = mapped_column(
        String(17),
        nullable=False,
        unique=True,
    )

    platform: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    app_version: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    device_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    activation_code: Mapped[str] = mapped_column(
        String(6),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    activated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    license_type: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )

    license_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    sessions: Mapped[list["SessionModel"]] = relationship(
        back_populates="device",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        Index(
            "ix_devices_platform_status",
            "platform",
            "status",
        ),
    )

    def __repr__(self) -> str:
        return (
            "DeviceModel("
            f"device_id={self.device_id!r}, "
            f"platform={self.platform!r}, "
            f"status={self.status!r}"
            ")"
        )


from app.infrastructure.persistence.models.session_model import SessionModel
