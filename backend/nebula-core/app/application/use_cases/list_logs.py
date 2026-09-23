from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.domain.entities.log import Log
from app.domain.repositories.log_repository import LogRepository


@dataclass(frozen=True)
class ListLogsCommand:
    device_id: UUID | None = None
    level: str | None = None
    hours: int = 24
    limit: int = 100


class ListLogsUseCase:
    def __init__(self, repository: LogRepository) -> None:
        self._repository = repository

    def execute(self, command: ListLogsCommand) -> list[Log]:
        since = datetime.now(timezone.utc) - timedelta(hours=command.hours)

        return self._repository.list_logs(
            device_id=command.device_id,
            level=command.level,
            since=since,
            limit=command.limit,
        )
