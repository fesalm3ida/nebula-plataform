from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.domain.enums.log_level import LogLevel


@dataclass
class Log:
    """Registro de diagnóstico técnico (ADR-022)."""

    session_id: UUID
    device_id: UUID
    level: LogLevel
    message: str
    log_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    received_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        self._validate_level(self.level)
        self._validate_message(self.message)
        self._validate_timestamp(
            self.occurred_at,
            "occurred_at",
        )
        self._validate_timestamp(
            self.received_at,
            "received_at",
        )

        if self.received_at < self.occurred_at:
            raise ValueError(
                "received_at cannot be earlier than occurred_at"
            )

    @staticmethod
    def _validate_level(value: LogLevel) -> None:
        if not isinstance(value, LogLevel):
            raise ValueError("level must be a valid LogLevel")

    @staticmethod
    def _validate_message(value: str) -> None:
        if not isinstance(value, str):
            raise ValueError("message must be a string")

        if not value.strip():
            raise ValueError("message cannot be empty")

    @staticmethod
    def _validate_timestamp(
        value: datetime,
        field_name: str,
    ) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(
                f"{field_name} must include timezone information"
            )
