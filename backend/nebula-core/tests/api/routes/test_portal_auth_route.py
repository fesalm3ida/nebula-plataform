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


def wrong_code(device: Device) -> str:
    """Retorna um codigo de 6 digitos garantidamente diferente."""
    return f"{(int(str(device.activation_code)) + 1) % 1000000:06d}"


def test_should_authenticate_user_with_mac_and_activation_code(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    response = client.post(
        "/auth/portal",
        json={
            "mac_address": str(device.mac_address),
            "activation_code": str(device.activation_code),
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["device_id"] == str(device.device_id)
    assert body["device_status"] == "pending"
    assert body["access_token"]


def test_should_reject_wrong_activation_code(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    response = client.post(
        "/auth/portal",
        json={
            "mac_address": str(device.mac_address),
            "activation_code": wrong_code(device),
        },
    )

    assert response.status_code == 401


def test_should_reject_malformed_activation_code(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    response = client.post(
        "/auth/portal",
        json={
            "mac_address": str(device.mac_address),
            "activation_code": "abc",
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
            "activation_code": "123456",
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
            "activation_code": str(device.activation_code),
        },
    )

    assert response.status_code == 403
