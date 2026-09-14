from fastapi.testclient import TestClient

from app.domain.entities.device import Device
from app.domain.enums.device_platform import DevicePlatform
from app.domain.value_objects.app_version import AppVersion
from app.domain.value_objects.device_fingerprint import DeviceFingerprint
from app.domain.value_objects.mac_address import MacAddress
from app.infrastructure.repositories.in_memory_device_repository import (
    InMemoryDeviceRepository,
)
from app.main import app


client = TestClient(app)


def make_device(*, active: bool = False) -> Device:
    device = Device(
        fingerprint=DeviceFingerprint("a" * 64),
        mac_address=MacAddress("02:1A:2B:3C:4D:5E"),
        platform=DevicePlatform.ANDROID_TV,
        app_version=AppVersion("0.3.0"),
    )

    if active:
        device.activate()

    return device


def test_should_authenticate_owner_with_mac_and_device_key(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    response = client.post(
        "/auth/portal",
        json={
            "mac_address": str(device.mac_address),
            "device_key": str(device.device_key),
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["device_id"] == str(device.device_id)
    assert body["device_status"] == "pending"
    assert body["access_token"]


def test_should_reject_wrong_device_key(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    response = client.post(
        "/auth/portal",
        json={
            "mac_address": str(device.mac_address),
            "device_key": "z" * 32,
        },
    )

    assert response.status_code == 401


def test_should_reject_unknown_mac_address(
    device_repository: InMemoryDeviceRepository,
) -> None:
    response = client.post(
        "/auth/portal",
        json={
            "mac_address": "02:99:99:99:99:99",
            "device_key": "123456",
        },
    )

    assert response.status_code == 401


def test_should_reject_revoked_device(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device(active=True)
    device.revoke()
    device_repository.save(device)

    response = client.post(
        "/auth/portal",
        json={
            "mac_address": str(device.mac_address),
            "device_key": str(device.device_key),
        },
    )

    assert response.status_code == 403
