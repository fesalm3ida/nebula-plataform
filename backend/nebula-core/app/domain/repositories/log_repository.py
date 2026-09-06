from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.log import Log


class LogRepository(ABC):
    @abstractmethod
    def save(self, log: Log) -> None:
        """Persist a Log."""

    @abstractmethod
    def find_by_id(self, log_id: UUID) -> Log | None:
        """Find a Log by its unique identifier."""
