from uuid import UUID

from app.domain.entities.telemetry_event import TelemetryEvent
from app.domain.repositories.telemetry_event_repository import (
    TelemetryEventRepository,
)


class InMemoryTelemetryEventRepository(TelemetryEventRepository):
    def __init__(self) -> None:
        self._events: dict[UUID, TelemetryEvent] = {}

    def save(self, event: TelemetryEvent) -> None:
        self._events[event.event_id] = event

    def find_by_id(self, event_id: UUID) -> TelemetryEvent | None:
        return self._events.get(event_id)
