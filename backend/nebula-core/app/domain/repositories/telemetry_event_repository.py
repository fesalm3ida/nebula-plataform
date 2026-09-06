from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.telemetry_event import TelemetryEvent


class TelemetryEventRepository(ABC):
    @abstractmethod
    def save(self, event: TelemetryEvent) -> None:
        """Persist a TelemetryEvent."""

    @abstractmethod
    def find_by_id(self, event_id: UUID) -> TelemetryEvent | None:
        """Find a TelemetryEvent by its unique identifier."""
