from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.domain.entities.log import Log


class LogRepository(ABC):
    @abstractmethod
    def save(self, log: Log) -> None:
        """Persist a Log."""

    @abstractmethod
    def find_by_id(self, log_id: UUID) -> Log | None:
        """Find a Log by its unique identifier."""

    def list_logs(
        self,
        *,
        device_id: UUID | None = None,
        level: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[Log]:
        """Logs mais recentes primeiro, com filtros opcionais."""
        raise NotImplementedError

    def count_by_level(
        self,
        *,
        since: datetime | None = None,
        device_id: UUID | None = None,
    ) -> dict[str, int]:
        """Total de logs por nivel."""
        raise NotImplementedError
