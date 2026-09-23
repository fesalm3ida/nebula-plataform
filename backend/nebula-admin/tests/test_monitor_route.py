from uuid import uuid4

from fastapi.testclient import TestClient

from app.application.ports.nebula_core_gateway import (
    CoreLogEntry,
    CoreTelemetryEvent,
)
from app.application.security.admin_token_service import AdminTokenService
from tests.conftest import FakeNebulaCoreGateway, admin_token_value


def auth_headers(service: AdminTokenService) -> dict[str, str]:
    return {"Authorization": f"Bearer {admin_token_value(service)}"}


def seed(gateway: FakeNebulaCoreGateway) -> None:
    gateway._telemetry.append(
        CoreTelemetryEvent(
            event_id=uuid4(),
            device_id=uuid4(),
            session_id=uuid4(),
            event_type="playback_started",
            payload={"channel": "Record News"},
            occurred_at="2026-09-23T06:00:00Z",
        )
    )
    gateway._telemetry.append(
        CoreTelemetryEvent(
            event_id=uuid4(),
            device_id=uuid4(),
            session_id=uuid4(),
            event_type="buffer_underrun",
            payload={},
            occurred_at="2026-09-23T06:05:00Z",
        )
    )
    gateway._logs.append(
        CoreLogEntry(
            log_id=uuid4(),
            device_id=uuid4(),
            session_id=uuid4(),
            level="error",
            message="falha ao abrir o stream",
            occurred_at="2026-09-23T06:06:00Z",
        )
    )


def test_should_return_monitor_summary(
    client: TestClient,
    admin_token_service: AdminTokenService,
    fake_core_gateway: FakeNebulaCoreGateway,
) -> None:
    seed(fake_core_gateway)

    response = client.get(
        "/admin/monitor/summary?hours=24",
        headers=auth_headers(admin_token_service),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total_events"] == 2
    assert body["events_by_type"]["playback_started"] == 1
    assert body["total_logs"] == 1
    assert body["logs_by_level"]["error"] == 1


def test_should_filter_telemetry_by_type(
    client: TestClient,
    admin_token_service: AdminTokenService,
    fake_core_gateway: FakeNebulaCoreGateway,
) -> None:
    seed(fake_core_gateway)

    response = client.get(
        "/admin/monitor/telemetry?event_type=buffer_underrun",
        headers=auth_headers(admin_token_service),
    )

    assert response.status_code == 200

    events = response.json()["events"]

    assert len(events) == 1
    assert events[0]["event_type"] == "buffer_underrun"


def test_should_list_logs(
    client: TestClient,
    admin_token_service: AdminTokenService,
    fake_core_gateway: FakeNebulaCoreGateway,
) -> None:
    seed(fake_core_gateway)

    response = client.get(
        "/admin/monitor/logs?level=error",
        headers=auth_headers(admin_token_service),
    )

    assert response.status_code == 200
    assert response.json()["logs"][0]["message"] == "falha ao abrir o stream"


def test_should_require_admin_for_monitor(client: TestClient) -> None:
    assert client.get("/admin/monitor/summary").status_code == 401
    assert client.get("/admin/monitor/telemetry").status_code == 401
    assert client.get("/admin/monitor/logs").status_code == 401
