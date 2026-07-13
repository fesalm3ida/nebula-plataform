from datetime import datetime
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.api.dependencies.device_repository import get_device_repository
from app.api.dependencies.session_repository import get_session_repository
from app.domain.entities.device import Device
from app.domain.enums.device_platform import DevicePlatform
from app.domain.value_objects.app_version import AppVersion
from app.domain.value_objects.device_fingerprint import DeviceFingerprint
from app.domain.value_objects.mac_address import MacAddress
from app.infrastructure.repositories.in_memory_device_repository import (
    InMemoryDeviceRepository,
)
from app.infrastructure.repositories.in_memory_session_repository import (
    InMemorySessionRepository,
)
from app.main import app


client = TestClient(app)


def reset_repositories() -> tuple[
    InMemoryDeviceRepository,
    InMemorySessionRepository,
]:
    device_repository = get_device_repository()
    session_repository = get_session_repository()

    assert isinstance(
        device_repository,
        InMemoryDeviceRepository,
    )
    assert isinstance(
        session_repository,
        InMemorySessionRepository,
    )

    device_repository._devices.clear()
    session_repository._sessions.clear()

    return device_repository, session_repository


def parse_api_datetime(value: str) -> datetime:
    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )


def make_device(active: bool = True) -> Device:
    device = Device(
        fingerprint=DeviceFingerprint("a" * 64),
        mac_address=MacAddress("AA:BB:CC:DD:EE:FF"),
        platform=DevicePlatform.ANDROID_TV,
        app_version=AppVersion("0.1.0"),
    )

    if active:
        device.activate()

    return device


def start_session_for_device(device: Device) -> dict:
    response = client.post(
        "/sessions",
        json={"device_id": str(device.device_id)},
    )

    assert response.status_code == 201

    return response.json()


def test_should_start_session_through_http() -> None:
    device_repository, _ = reset_repositories()

    device = make_device()
    device_repository.save(device)

    response = client.post(
        "/sessions",
        json={"device_id": str(device.device_id)},
    )

    assert response.status_code == 201

    body = response.json()

    assert body["session_id"]
    assert body["device_id"] == str(device.device_id)
    assert body["status"] == "active"
    assert body["started_at"]
    assert body["expires_at"]
    assert body["last_seen"]
    assert body["last_seen"] == body["started_at"]


def test_should_reject_unknown_device() -> None:
    reset_repositories()

    response = client.post(
        "/sessions",
        json={"device_id": str(uuid4())},
    )

    assert response.status_code == 404


def test_should_reject_pending_device() -> None:
    device_repository, _ = reset_repositories()

    device = make_device(active=False)
    device_repository.save(device)

    response = client.post(
        "/sessions",
        json={"device_id": str(device.device_id)},
    )

    assert response.status_code == 403


def test_should_reject_second_active_session() -> None:
    device_repository, _ = reset_repositories()

    device = make_device()
    device_repository.save(device)

    payload = {"device_id": str(device.device_id)}

    first_response = client.post(
        "/sessions",
        json=payload,
    )

    second_response = client.post(
        "/sessions",
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_should_reject_invalid_request_schema() -> None:
    reset_repositories()

    response = client.post(
        "/sessions",
        json={"device_id": "invalid-uuid"},
    )

    assert response.status_code == 422


def test_should_update_session_presence_through_http() -> None:
    device_repository, _ = reset_repositories()

    device = make_device()
    device_repository.save(device)

    session_body = start_session_for_device(device)
    session_id = session_body["session_id"]

    original_last_seen = parse_api_datetime(
        session_body["last_seen"]
    )

    response = client.post(
        f"/sessions/{session_id}/heartbeat"
    )

    assert response.status_code == 200

    body = response.json()

    updated_last_seen = parse_api_datetime(
        body["last_seen"]
    )

    assert body["session_id"] == session_id
    assert body["status"] == "active"
    assert updated_last_seen >= original_last_seen


def test_should_return_not_found_for_unknown_heartbeat_session() -> None:
    reset_repositories()

    response = client.post(
        f"/sessions/{uuid4()}/heartbeat"
    )

    assert response.status_code == 404


def test_should_reject_heartbeat_for_ended_session() -> None:
    device_repository, _ = reset_repositories()

    device = make_device()
    device_repository.save(device)

    session_body = start_session_for_device(device)
    session_id = session_body["session_id"]

    client.post(f"/sessions/{session_id}/end")

    response = client.post(
        f"/sessions/{session_id}/heartbeat"
    )

    assert response.status_code == 409
    assert "ended" in response.json()["detail"]


def test_should_reject_heartbeat_for_expired_session() -> None:
    device_repository, session_repository = reset_repositories()

    device = make_device()
    device_repository.save(device)

    session_body = start_session_for_device(device)
    session_id = session_body["session_id"]

    session = session_repository.find_by_id(
        UUID(session_id)
    )

    assert session is not None

    session.expire()
    session_repository.save(session)

    response = client.post(
        f"/sessions/{session_id}/heartbeat"
    )

    assert response.status_code == 409
    assert "expired" in response.json()["detail"]


def test_should_end_active_session_through_http() -> None:
    device_repository, _ = reset_repositories()

    device = make_device()
    device_repository.save(device)

    session_body = start_session_for_device(device)
    session_id = session_body["session_id"]

    response = client.post(
        f"/sessions/{session_id}/end"
    )

    assert response.status_code == 200
    assert response.json()["session_id"] == session_id
    assert response.json()["status"] == "ended"
    assert response.json()["ended_at"]


def test_should_return_not_found_when_ending_unknown_session() -> None:
    reset_repositories()

    response = client.post(
        f"/sessions/{uuid4()}/end"
    )

    assert response.status_code == 404


def test_should_return_conflict_when_session_is_already_ended() -> None:
    device_repository, _ = reset_repositories()

    device = make_device()
    device_repository.save(device)

    session_body = start_session_for_device(device)
    session_id = session_body["session_id"]

    client.post(f"/sessions/{session_id}/end")

    response = client.post(
        f"/sessions/{session_id}/end"
    )

    assert response.status_code == 409

