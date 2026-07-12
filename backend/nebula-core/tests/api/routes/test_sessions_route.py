from uuid import uuid4

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
