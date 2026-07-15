from fastapi.testclient import TestClient

from app.domain.entities.device import Device
from app.domain.enums.device_platform import DevicePlatform
from app.domain.value_objects.app_version import AppVersion
from app.domain.value_objects.device_fingerprint import (
    DeviceFingerprint,
)
from app.domain.value_objects.mac_address import MacAddress
from app.infrastructure.repositories.in_memory_device_repository import (
    InMemoryDeviceRepository,
)
from app.main import app


client = TestClient(app)


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


def valid_payload(device: Device) -> dict[str, str]:
    return {
        "device_id": str(device.device_id),
        "fingerprint": str(device.fingerprint),
        "device_key": str(device.device_key),
    }


def test_should_authenticate_active_device_through_http(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    response = client.post(
        "/auth/device",
        json=valid_payload(device),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["access_token"]
    assert body["expires_at"]
    assert body["device_status"] == "active"


def test_should_reject_invalid_credentials(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    payload = valid_payload(device)
    payload["device_key"] = "x" * 32

    response = client.post(
        "/auth/device",
        json=payload,
    )

    assert response.status_code == 401


def test_should_reject_pending_device(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device(active=False)
    device_repository.save(device)

    response = client.post(
        "/auth/device",
        json=valid_payload(device),
    )

    assert response.status_code == 403


def test_should_reject_invalid_request_schema() -> None:
    response = client.post(
        "/auth/device",
        json={
            "device_id": "invalid-uuid",
            "fingerprint": "invalid",
            "device_key": "short",
        },
    )

    assert response.status_code == 422
