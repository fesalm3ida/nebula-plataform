from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.base import Base


class PlaylistAssignmentModel(Base):
    __tablename__ = "playlist_assignments"

    assignment_id: Mapped[UUID] = mapped_column(
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

    playlist_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "playlists.playlist_id",
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

    playlist: Mapped["PlaylistModel"] = relationship(
        back_populates="assignments",
    )

    device: Mapped["DeviceModel"] = relationship()

    __table_args__ = (
        Index(
            "ix_playlist_assignments_device_status",
            "device_id",
            "status",
        ),
    )

    def __repr__(self) -> str:
        return (
            "PlaylistAssignmentModel("
            f"assignment_id={self.assignment_id!r}, "
            f"device_id={self.device_id!r}, "
            f"playlist_id={self.playlist_id!r}, "
            f"status={self.status!r}"
            ")"
        )


from app.infrastructure.persistence.models.device_model import DeviceModel
from app.infrastructure.persistence.models.playlist_model import PlaylistModel
