from uuid import UUID

from app.domain.entities.log import Log
from app.domain.repositories.log_repository import LogRepository


class InMemoryLogRepository(LogRepository):
    def __init__(self) -> None:
        self._logs: dict[UUID, Log] = {}

    def save(self, log: Log) -> None:
        self._logs[log.log_id] = log

    def find_by_id(self, log_id: UUID) -> Log | None:
        return self._logs.get(log_id)
