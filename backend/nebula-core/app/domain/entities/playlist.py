from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from app.domain.enums.playlist_format import PlaylistFormat
from app.domain.enums.playlist_status import PlaylistStatus


@dataclass
class Playlist:
    name: str
    format: PlaylistFormat
    source_url: str
    playlist_id: UUID = field(default_factory=uuid4)
    status: PlaylistStatus = PlaylistStatus.ACTIVE
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        self.name = self._normalize_required_text(
            value=self.name,
            field_name="name",
        )
        self.source_url = self._normalize_required_text(
            value=self.source_url,
            field_name="source_url",
        )

        self._validate_format()
        self._validate_status()
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
    def is_available_for_provisioning(self) -> bool:
        return self.status == PlaylistStatus.ACTIVE

    def update_name(self, name: str) -> None:
        normalized_name = self._normalize_required_text(
            value=name,
            field_name="name",
        )

        if normalized_name == self.name:
            return

        self.name = normalized_name
        self._touch()

    def update_source_url(self, source_url: str) -> None:
        normalized_source_url = self._normalize_required_text(
            value=source_url,
            field_name="source_url",
        )

        if normalized_source_url == self.source_url:
            return

        self.source_url = normalized_source_url
        self._touch()

    def activate(self) -> None:
        if self.status == PlaylistStatus.ACTIVE:
            return

        self.status = PlaylistStatus.ACTIVE
        self._touch()

    def disable(self) -> None:
        if self.status == PlaylistStatus.DISABLED:
            return

        self.status = PlaylistStatus.DISABLED
        self._touch()

    def _touch(self) -> None:
        now = datetime.now(timezone.utc)

        if now <= self.updated_at:
            now = self.updated_at + timedelta(microseconds=1)

        self.updated_at = now

    def _validate_format(self) -> None:
        if not isinstance(self.format, PlaylistFormat):
            raise ValueError("format must be a valid PlaylistFormat")

    def _validate_status(self) -> None:
        if not isinstance(self.status, PlaylistStatus):
            raise ValueError("status must be a valid PlaylistStatus")

    @staticmethod
    def _normalize_required_text(
        value: str,
        field_name: str,
    ) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string")

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(f"{field_name} cannot be empty")

        return normalized_value

    @staticmethod
    def _validate_timestamp(
        value: datetime,
        field_name: str,
    ) -> None:
        if not isinstance(value, datetime):
            raise ValueError(f"{field_name} must be a datetime")

        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(
                f"{field_name} must include timezone information"
            )
