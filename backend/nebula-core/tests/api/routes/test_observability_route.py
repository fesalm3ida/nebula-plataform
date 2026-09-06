from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.domain.entities.device import Device
from app.domain.entities.session import Session
from app.domain.enums.device_platform import DevicePlatform
from app.domain.value_objects.app_version import AppVersion
from app.domain.value_objects.device_fingerprint import DeviceFingerprint
from app.domain.value_objects.mac_address import MacAddress
from app.infrastructure.repositories.in_memory_device_repository import (
    InMemoryDeviceRepository,
)
from app.infrastructure.repositories.in_memory_log_repository import (
    InMemoryLogRepository,
)
from app.infrastructure.repositories.in_memory_session_repository import (
    InMemorySessionRepository,
)
from app.infrastructure.repositories.in_memory_telemetry_event_repository import (
    InMemoryTelemetryEventRepository,
)
from app.main import app


client = TestClient(app)


def make_device(
    *,
    fingerprint: str = "a" * 64,
    mac_address: str = "AA:BB:CC:DD:EE:FF",
    active: bool = True,
) -> Device:
    device = Device(
        fingerprint=DeviceFingerprint(fingerprint),
        mac_address=MacAddress(mac_address),
        platform=DevicePlatform.ANDROID_TV,
        app_version=AppVersion("0.3.0"),
    )

    if active:
        device.activate()

    return device


def make_session(
    device: Device,
    *,
    active: bool = True,
) -> Session:
    started_at = datetime.now(timezone.utc)
    session = Session(
        device_id=device.device_id,
        started_at=started_at,
        expires_at=started_at + timedelta(minutes=30),
    )

    if not active:
        session.end()

    return session


def authorization_headers(device: Device) -> dict[str, str]:
    return {
        "Authorization": f"Bearer fake-jwt:{device.device_id}",
    }


def test_should_ingest_telemetry_event(
    device_repository: InMemoryDeviceRepository,
    session_repository: InMemorySessionRepository,
    telemetry_event_repository: InMemoryTelemetryEventRepository,
) -> None:
    device = make_device()
    device_repository.save(device)
    session = make_session(device)
    session_repository.save(session)

    response = client.post(
        "/me/telemetry",
        headers=authorization_headers(device),
        json={
            "session_id": str(session.session_id),
            "event_type": "playback_started",
            "payload": {"duration_ms": 100},
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["event_id"]
    assert body["device_id"] == str(device.device_id)
    assert body["session_id"] == str(session.session_id)
    assert body["event_type"] == "playback_started"

    assert (
        telemetry_event_repository.find_by_id(UUID(body["event_id"]))
        is not None
    )


def test_should_reject_telemetry_without_bearer() -> None:
    response = client.post(
        "/me/telemetry",
        json={
            "session_id": str(uuid4()),
            "event_type": "playback_started",
            "payload": {},
        },
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_should_return_not_found_for_unknown_session(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    response = client.post(
        "/me/telemetry",
        headers=authorization_headers(device),
        json={
            "session_id": str(uuid4()),
            "event_type": "playback_started",
            "payload": {},
        },
    )

    assert response.status_code == 404


def test_should_return_forbidden_for_session_not_owned(
    device_repository: InMemoryDeviceRepository,
    session_repository: InMemorySessionRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    other_device = make_device(
        fingerprint="b" * 64,
        mac_address="11:22:33:44:55:66",
    )
    other_device.activate()
    other_session = make_session(other_device)
    session_repository.save(other_session)

    response = client.post(
        "/me/telemetry",
        headers=authorization_headers(device),
        json={
            "session_id": str(other_session.session_id),
            "event_type": "playback_started",
            "payload": {},
        },
    )

    assert response.status_code == 403


def test_should_ingest_log(
    device_repository: InMemoryDeviceRepository,
    session_repository: InMemorySessionRepository,
    log_repository: InMemoryLogRepository,
) -> None:
    device = make_device()
    device_repository.save(device)
    session = make_session(device)
    session_repository.save(session)

    response = client.post(
        "/me/logs",
        headers=authorization_headers(device),
        json={
            "session_id": str(session.session_id),
            "level": "warning",
            "message": "Buffer underrun detected",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["log_id"]
    assert body["device_id"] == str(device.device_id)
    assert body["level"] == "warning"

    assert log_repository.find_by_id(UUID(body["log_id"])) is not None


def test_should_reject_log_without_bearer() -> None:
    response = client.post(
        "/me/logs",
        json={
            "session_id": str(uuid4()),
            "level": "info",
            "message": "hello",
        },
    )

    assert response.status_code == 401
