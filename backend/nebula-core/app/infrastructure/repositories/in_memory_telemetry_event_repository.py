from datetime import datetime
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

    def list_events(
        self,
        *,
        device_id: UUID | None = None,
        event_type: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[TelemetryEvent]:
        events = [
            event
            for event in self._events.values()
            if (device_id is None or event.device_id == device_id)
            and (
                event_type is None
                or event.event_type.value == event_type
            )
            and (since is None or event.occurred_at >= since)
        ]

        events.sort(key=lambda event: event.occurred_at, reverse=True)

        return events[:limit]

    def count_by_type(
        self,
        *,
        since: datetime | None = None,
        device_id: UUID | None = None,
    ) -> dict[str, int]:
        counts: dict[str, int] = {}

        for event in self._events.values():
            if device_id is not None and event.device_id != device_id:
                continue

            if since is not None and event.occurred_at < since:
                continue

            key = event.event_type.value
            counts[key] = counts.get(key, 0) + 1

        return counts

    def count_per_hour(
        self,
        *,
        since: datetime,
        device_id: UUID | None = None,
    ) -> list[tuple[datetime, int]]:
        buckets: dict[datetime, int] = {}

        for event in self._events.values():
            if device_id is not None and event.device_id != device_id:
                continue

            if event.occurred_at < since:
                continue

            hour = event.occurred_at.replace(
                minute=0,
                second=0,
                microsecond=0,
            )
            buckets[hour] = buckets.get(hour, 0) + 1

        return sorted(buckets.items())
