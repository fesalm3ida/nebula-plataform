from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.domain.entities.telemetry_event import TelemetryEvent
from app.domain.repositories.telemetry_event_repository import (
    TelemetryEventRepository,
)


@dataclass(frozen=True)
class ListTelemetryEventsCommand:
    device_id: UUID | None = None
    event_type: str | None = None
    hours: int = 24
    limit: int = 100


class ListTelemetryEventsUseCase:
    def __init__(self, repository: TelemetryEventRepository) -> None:
        self._repository = repository

    def execute(
        self,
        command: ListTelemetryEventsCommand,
    ) -> list[TelemetryEvent]:
        since = datetime.now(timezone.utc) - timedelta(hours=command.hours)

        return self._repository.list_events(
            device_id=command.device_id,
            event_type=command.event_type,
            since=since,
            limit=command.limit,
        )
