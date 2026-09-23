from datetime import datetime
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

    def list_logs(
        self,
        *,
        device_id: UUID | None = None,
        level: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[Log]:
        logs = [
            log
            for log in self._logs.values()
            if (device_id is None or log.device_id == device_id)
            and (level is None or log.level.value == level)
            and (since is None or log.occurred_at >= since)
        ]

        logs.sort(key=lambda log: log.occurred_at, reverse=True)

        return logs[:limit]

    def count_by_level(
        self,
        *,
        since: datetime | None = None,
        device_id: UUID | None = None,
    ) -> dict[str, int]:
        counts: dict[str, int] = {}

        for log in self._logs.values():
            if device_id is not None and log.device_id != device_id:
                continue

            if since is not None and log.occurred_at < since:
                continue

            key = log.level.value
            counts[key] = counts.get(key, 0) + 1

        return counts
