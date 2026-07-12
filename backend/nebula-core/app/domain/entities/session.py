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
    ended_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.expires_at.tzinfo is None:
            raise ValueError("Session expiration must be timezone-aware.")

        if self.expires_at <= self.started_at:
            raise ValueError(
                "Session expiration must be later than its start time."
            )

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
        return reference_time >= self.expires_at
