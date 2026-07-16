from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.base import Base


class SessionModel(Base):
    __tablename__ = "sessions"

    session_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        nullable=False,
    )

    device_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "devices.device_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    device: Mapped["DeviceModel"] = relationship(
        back_populates="sessions",
    )

    __table_args__ = (
        Index(
            "ix_sessions_device_status",
            "device_id",
            "status",
        ),
        Index(
            "ix_sessions_status_last_seen",
            "status",
            "last_seen",
        ),
    )

    def __repr__(self) -> str:
        return (
            "SessionModel("
            f"session_id={self.session_id!r}, "
            f"device_id={self.device_id!r}, "
            f"status={self.status!r}"
            ")"
        )


from app.infrastructure.persistence.models.device_model import DeviceModel
