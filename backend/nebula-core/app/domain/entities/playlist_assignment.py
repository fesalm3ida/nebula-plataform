from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from app.domain.enums.playlist_assignment_status import (
    PlaylistAssignmentStatus,
)


@dataclass
class PlaylistAssignment:
    """Vínculo entre um Device e uma Playlist (entidade intermediária).

    Segue a ADR-021: o Device não referencia a Playlist diretamente; a
    associação ocorre através desta entidade, desacoplando o Device da
    origem do conteúdo.
    """

    device_id: UUID
    playlist_id: UUID
    assignment_id: UUID = field(default_factory=uuid4)
    status: PlaylistAssignmentStatus = PlaylistAssignmentStatus.ACTIVE
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        self._validate_timestamp(
            value=self.created_at,
            field_name="created_at",
        )
        self._validate_timestamp(
            value=self.updated_at,
            field_name="updated_at",
        )

        if self.updated_at < self.created_at:
            raise ValueError(
                "updated_at cannot be earlier than created_at"
            )

    @property
    def is_active(self) -> bool:
        return self.status == PlaylistAssignmentStatus.ACTIVE

    def revoke(self) -> None:
        if self.status == PlaylistAssignmentStatus.REVOKED:
            return

        self.status = PlaylistAssignmentStatus.REVOKED
        self._touch()

    def reactivate(self) -> None:
        if self.status == PlaylistAssignmentStatus.ACTIVE:
            return

        self.status = PlaylistAssignmentStatus.ACTIVE
        self._touch()

    def _touch(self) -> None:
        now = datetime.now(timezone.utc)

        if now <= self.updated_at:
            now = self.updated_at + timedelta(microseconds=1)

        self.updated_at = now

    @staticmethod
    def _validate_timestamp(
        value: datetime,
        field_name: str,
    ) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(
                f"{field_name} must include timezone information"
            )
