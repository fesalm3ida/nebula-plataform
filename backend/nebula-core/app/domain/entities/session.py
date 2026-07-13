from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.domain.enums.session_status import SessionStatus


@dataclass
class Session:
    device_id: UUID
    expires_at: datetime
    session_id: UUID = field(default_factory=uuid4)
    status: SessionStatus = SessionStatus.ACTIVE
    started_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    last_seen: datetime | None = None
    ended_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.started_at.tzinfo is None:
            raise ValueError("Session start time must be timezone-aware.")

        if self.expires_at.tzinfo is None:
            raise ValueError("Session expiration must be timezone-aware.")

        if self.expires_at <= self.started_at:
            raise ValueError(
                "Session expiration must be later than its start time."
            )

        if self.last_seen is None:
            self.last_seen = self.started_at
        elif self.last_seen.tzinfo is None:
            raise ValueError(
                "Session last_seen must be timezone-aware."
            )

        if self.last_seen < self.started_at:
            raise ValueError(
                "Session last_seen cannot be earlier than its start time."
            )

    def touch(self, now: datetime | None = None) -> None:
        if self.status != SessionStatus.ACTIVE:
            raise ValueError("Only an active Session can receive a heartbeat.")

        reference_time = now or datetime.now(timezone.utc)

        if reference_time.tzinfo is None:
            raise ValueError(
                "Session heartbeat time must be timezone-aware."
            )

        if reference_time < self.last_seen:
            raise ValueError(
                "Session heartbeat time cannot be earlier than last_seen."
            )

        self.last_seen = reference_time

    def end(self) -> None:
        if self.status != SessionStatus.ACTIVE:
            raise ValueError("Only an active Session can be ended.")

        self.status = SessionStatus.ENDED
        self.ended_at = datetime.now(timezone.utc)

    def expire(self) -> None:
        if self.status != SessionStatus.ACTIVE:
            raise ValueError("Only an active Session can expire.")

        self.status = SessionStatus.EXPIRED
        self.ended_at = datetime.now(timezone.utc)

    def is_expired(self, now: datetime | None = None) -> bool:
        reference_time = now or datetime.now(timezone.utc)

        if reference_time.tzinfo is None:
            raise ValueError(
                "Session expiration reference must be timezone-aware."
            )

        return reference_time >= self.expires_at
