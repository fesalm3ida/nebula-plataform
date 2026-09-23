from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.domain.entities.telemetry_event import TelemetryEvent


class TelemetryEventRepository(ABC):
    @abstractmethod
    def save(self, event: TelemetryEvent) -> None:
        """Persist a TelemetryEvent."""

    @abstractmethod
    def find_by_id(self, event_id: UUID) -> TelemetryEvent | None:
        """Find a TelemetryEvent by its unique identifier."""

    def list_events(
        self,
        *,
        device_id: UUID | None = None,
        event_type: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[TelemetryEvent]:
        """Eventos mais recentes primeiro, com filtros opcionais."""
        raise NotImplementedError

    def count_by_type(
        self,
        *,
        since: datetime | None = None,
        device_id: UUID | None = None,
    ) -> dict[str, int]:
        """Total de eventos por tipo (para os cartoes do monitor)."""
        raise NotImplementedError

    def count_per_hour(
        self,
        *,
        since: datetime,
        device_id: UUID | None = None,
    ) -> list[tuple[datetime, int]]:
        """Serie temporal (hora a hora) para o grafico do monitor."""
        raise NotImplementedError
