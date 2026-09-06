from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from app.domain.enums.telemetry_event_type import TelemetryEventType


@dataclass
class TelemetryEvent:
    """Evento de comportamento/experiência do usuário (ADR-022/023)."""

    session_id: UUID
    device_id: UUID
    event_type: TelemetryEventType
    payload: dict[str, Any]
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    received_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        self._validate_event_type(self.event_type)
        self._validate_payload(self.payload)
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
    def _validate_event_type(value: TelemetryEventType) -> None:
        if not isinstance(value, TelemetryEventType):
            raise ValueError(
                "event_type must be a valid TelemetryEventType"
            )

    @staticmethod
    def _validate_payload(value: dict[str, Any]) -> None:
        if not isinstance(value, dict):
            raise ValueError("payload must be a dictionary")

    @staticmethod
    def _validate_timestamp(
        value: datetime,
        field_name: str,
    ) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(
                f"{field_name} must include timezone information"
            )
