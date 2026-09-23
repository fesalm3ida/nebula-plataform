from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.domain.entities.log import Log
from app.domain.entities.telemetry_event import TelemetryEvent
from app.domain.enums.log_level import LogLevel
from app.domain.enums.telemetry_event_type import TelemetryEventType
from app.infrastructure.repositories.in_memory_log_repository import (
    InMemoryLogRepository,
)
from app.infrastructure.repositories.in_memory_telemetry_event_repository import (
    InMemoryTelemetryEventRepository,
)
from app.main import app


client = TestClient(app)


def admin_headers() -> dict[str, str]:
    return {"X-Admin-Token": get_settings().admin_api_key}


def now() -> datetime:
    return datetime.now(timezone.utc)


def save_event(
    repository: InMemoryTelemetryEventRepository,
    event_type: TelemetryEventType,
    *,
    minutes_ago: int = 1,
    device_id=None,
) -> TelemetryEvent:
    event = TelemetryEvent(
        session_id=uuid4(),
        device_id=device_id or uuid4(),
        event_type=event_type,
        payload={"source": "test"},
        occurred_at=now() - timedelta(minutes=minutes_ago),
        received_at=now() - timedelta(minutes=minutes_ago),
    )
    repository.save(event)

    return event


def save_log(
    repository: InMemoryLogRepository,
    level: LogLevel,
    *,
    minutes_ago: int = 1,
    message: str = "mensagem",
) -> Log:
    log = Log(
        session_id=uuid4(),
        device_id=uuid4(),
        level=level,
        message=message,
        occurred_at=now() - timedelta(minutes=minutes_ago),
        received_at=now() - timedelta(minutes=minutes_ago),
    )
    repository.save(log)

    return log


def test_should_return_monitor_summary(
    telemetry_event_repository: InMemoryTelemetryEventRepository,
    log_repository: InMemoryLogRepository,
) -> None:
    save_event(
        telemetry_event_repository,
        TelemetryEventType.PLAYBACK_STARTED,
    )
    save_event(
        telemetry_event_repository,
        TelemetryEventType.PLAYBACK_STARTED,
    )
    save_event(
        telemetry_event_repository,
        TelemetryEventType.BUFFER_UNDERRUN,
    )
    save_log(log_repository, LogLevel.ERROR)
    save_log(log_repository, LogLevel.INFO)

    response = client.get(
        "/observability/summary?hours=24",
        headers=admin_headers(),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total_events"] == 3
    assert body["events_by_type"]["playback_started"] == 2
    assert body["events_by_type"]["buffer_underrun"] == 1
    assert body["total_logs"] == 2
    assert body["logs_by_level"]["error"] == 1
    assert sum(point["count"] for point in body["events_per_hour"]) == 3


def test_should_ignore_events_outside_the_window(
    telemetry_event_repository: InMemoryTelemetryEventRepository,
) -> None:
    save_event(
        telemetry_event_repository,
        TelemetryEventType.PLAYBACK_STARTED,
        minutes_ago=5,
    )
    save_event(
        telemetry_event_repository,
        TelemetryEventType.PLAYBACK_STARTED,
        minutes_ago=60 * 48,
    )

    response = client.get(
        "/observability/summary?hours=24",
        headers=admin_headers(),
    )

    assert response.json()["total_events"] == 1


def test_should_list_telemetry_events_with_filters(
    telemetry_event_repository: InMemoryTelemetryEventRepository,
) -> None:
    save_event(
        telemetry_event_repository,
        TelemetryEventType.PLAYBACK_ERROR,
    )
    save_event(
        telemetry_event_repository,
        TelemetryEventType.PLAYBACK_STARTED,
    )

    response = client.get(
        "/observability/telemetry?event_type=playback_error",
        headers=admin_headers(),
    )

    assert response.status_code == 200

    events = response.json()["events"]

    assert len(events) == 1
    assert events[0]["event_type"] == "playback_error"
    assert events[0]["payload"] == {"source": "test"}


def test_should_list_logs_with_level_filter(
    log_repository: InMemoryLogRepository,
) -> None:
    save_log(log_repository, LogLevel.ERROR, message="falhou o stream")
    save_log(log_repository, LogLevel.INFO, message="tudo certo")

    response = client.get(
        "/observability/logs?level=error",
        headers=admin_headers(),
    )

    assert response.status_code == 200

    logs = response.json()["logs"]

    assert len(logs) == 1
    assert logs[0]["message"] == "falhou o stream"


def test_should_require_admin_for_monitor_routes() -> None:
    assert client.get("/observability/summary").status_code == 401
    assert client.get("/observability/telemetry").status_code == 401
    assert client.get("/observability/logs").status_code == 401
