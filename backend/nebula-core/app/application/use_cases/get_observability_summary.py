from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.domain.repositories.log_repository import LogRepository
from app.domain.repositories.telemetry_event_repository import (
    TelemetryEventRepository,
)


@dataclass(frozen=True)
class ObservabilitySummary:
    since: datetime
    total_events: int
    events_by_type: dict[str, int]
    events_per_hour: list[tuple[datetime, int]]
    total_logs: int
    logs_by_level: dict[str, int]


class GetObservabilitySummaryUseCase:
    """Resumo do monitor: totais, distribuicao e serie temporal."""

    def __init__(
        self,
        telemetry_repository: TelemetryEventRepository,
        log_repository: LogRepository,
    ) -> None:
        self._telemetry = telemetry_repository
        self._logs = log_repository

    def execute(self, hours: int = 24) -> ObservabilitySummary:
        since = datetime.now(timezone.utc) - timedelta(hours=hours)

        events_by_type = self._telemetry.count_by_type(since=since)
        logs_by_level = self._logs.count_by_level(since=since)

        return ObservabilitySummary(
            since=since,
            total_events=sum(events_by_type.values()),
            events_by_type=events_by_type,
            events_per_hour=self._telemetry.count_per_hour(since=since),
            total_logs=sum(logs_by_level.values()),
            logs_by_level=logs_by_level,
        )
