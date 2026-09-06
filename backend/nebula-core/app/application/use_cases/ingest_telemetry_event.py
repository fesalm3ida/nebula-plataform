from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from app.application.exceptions import (
    SessionNotActiveError,
    SessionNotFoundError,
    SessionOwnershipError,
)
from app.domain.entities.telemetry_event import TelemetryEvent
from app.domain.enums.session_status import SessionStatus
from app.domain.enums.telemetry_event_type import TelemetryEventType
from app.domain.repositories.session_repository import SessionRepository
from app.domain.repositories.telemetry_event_repository import (
    TelemetryEventRepository,
)


@dataclass(frozen=True)
class IngestTelemetryEventCommand:
    device_id: UUID
    session_id: UUID
    event_type: TelemetryEventType
    payload: dict[str, Any]
    occurred_at: datetime | None = None


@dataclass(frozen=True)
class IngestTelemetryEventResult:
    event_id: UUID
    occurred_at: datetime
    received_at: datetime


class IngestTelemetryEventUseCase:
    def __init__(
        self,
        telemetry_event_repository: TelemetryEventRepository,
        session_repository: SessionRepository,
    ) -> None:
        self._telemetry_event_repository = telemetry_event_repository
        self._session_repository = session_repository

    def execute(
        self,
        command: IngestTelemetryEventCommand,
    ) -> IngestTelemetryEventResult:
        session = self._session_repository.find_by_id(command.session_id)

        if session is None:
            raise SessionNotFoundError(
                f"Session {command.session_id} does not exist."
            )

        if session.device_id != command.device_id:
            raise SessionOwnershipError(
                "Session does not belong to the authenticated Device."
            )

        if session.status != SessionStatus.ACTIVE:
            raise SessionNotActiveError(
                "Session is not active."
            )

        event = TelemetryEvent(
            session_id=command.session_id,
            device_id=command.device_id,
            event_type=command.event_type,
            payload=command.payload,
            occurred_at=command.occurred_at
            or datetime.now(timezone.utc),
        )

        self._telemetry_event_repository.save(event)

        return IngestTelemetryEventResult(
            event_id=event.event_id,
            occurred_at=event.occurred_at,
            received_at=event.received_at,
        )
