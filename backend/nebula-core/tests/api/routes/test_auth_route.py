from fastapi.testclient import TestClient
from app.api.dependencies.device_repository import get_device_repository
from app.domain.entities.device import Device
from app.domain.enums.device_platform import DevicePlatform
from app.domain.value_objects.app_version import AppVersion
from app.domain.value_objects.device_fingerprint import DeviceFingerprint
from app.domain.value_objects.mac_address import MacAddress
from app.infrastructure.repositories.in_memory_device_repository import (InMemoryDeviceRepository)
from app.main import app


client = TestClient(app)


def reset_repository() -> InMemoryDeviceRepository:
    repository = get_device_repository()

    assert isinstance(repository, InMemoryDeviceRepository)

    repository._devices.clear()
    return repository


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


def authentication_payload(device: Device) -> dict[str, str]:
    return {
        "device_id": str(device.device_id),
        "device_key": str(device.device_key),
        "fingerprint": str(device.fingerprint),
    }


def test_should_authenticate_active_device_through_http() -> None:
    repository = reset_repository()
    device = make_device()
    repository.save(device)

    response = client.post(
        "/auth/device",
        json=authentication_payload(device),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["access_token"]
    assert body["expires_at"]
    assert body["device_status"] == "active"


def test_should_reject_invalid_credentials() -> None:
    repository = reset_repository()
    device = make_device()
    repository.save(device)

    payload = authentication_payload(device)
    payload["device_key"] = "x" * 32

    response = client.post(
        "/auth/device",
        json=payload,
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid Device credentials."


def test_should_reject_pending_device() -> None:
    repository = reset_repository()
    device = make_device(active=False)
    repository.save(device)

    response = client.post(
        "/auth/device",
        json=authentication_payload(device),
    )

    assert response.status_code == 403
    assert "pending" in response.json()["detail"]


def test_should_reject_invalid_request_schema() -> None:
    response = client.post(
        "/auth/device",
        json={
            "device_id": "invalid-uuid",
            "device_key": "short",
            "fingerprint": "invalid",
        },
    )

    assert response.status_code == 422
