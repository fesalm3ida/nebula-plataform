from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.domain.entities.device import Device
from app.domain.enums.device_platform import DevicePlatform
from app.domain.enums.license_type import LicenseType
from app.domain.value_objects.app_version import AppVersion
from app.domain.value_objects.device_fingerprint import DeviceFingerprint
from app.domain.value_objects.mac_address import MacAddress
from app.infrastructure.repositories.in_memory_device_repository import (
    InMemoryDeviceRepository,
)
from app.main import app


client = TestClient(app)


def make_device(*, active: bool = True) -> Device:
    device = Device(
        fingerprint=DeviceFingerprint("a" * 64),
        mac_address=MacAddress("AA:BB:CC:DD:EE:FF"),
        platform=DevicePlatform.ANDROID_TV,
        app_version=AppVersion("0.3.0"),
    )

    if active:
        device.activate()

    return device


def authorization_headers(device: Device) -> dict[str, str]:
    return {"Authorization": f"Bearer fake-jwt:{device.device_id}"}


def test_should_return_trial_license(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    response = client.get(
        "/me/license",
        headers=authorization_headers(device),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["device_id"] == str(device.device_id)
    assert body["license_type"] == "trial"
    assert body["status"] == "active"
    assert body["expired"] is False
    assert body["days_remaining"] == Device.TRIAL_DURATION_DAYS - 1


def test_should_report_lifetime_license_without_expiry(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device()
    device.grant_license(LicenseType.LIFETIME)
    device_repository.save(device)

    response = client.get(
        "/me/license",
        headers=authorization_headers(device),
    )

    body = response.json()

    assert body["license_type"] == "lifetime"
    assert body["expires_at"] is None
    assert body["days_remaining"] is None
    assert body["expired"] is False


def test_should_report_expired_trial(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device()
    device.license_expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    device_repository.save(device)

    response = client.get(
        "/me/license",
        headers=authorization_headers(device),
    )

    body = response.json()

    assert body["expired"] is True
    assert body["days_remaining"] == 0


def test_should_reject_without_credentials() -> None:
    response = client.get("/me/license")

    assert response.status_code == 401


def test_should_report_pending_device_as_unlicensed(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device(active=False)
    device_repository.save(device)

    response = client.get(
        "/me/license",
        headers=authorization_headers(device),
    )

    # O portal do dono precisa ver o estado antes da ativacao.
    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "pending"
    assert body["license_type"] is None
    assert body["expired"] is False


def test_should_activate_device_granting_trial(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device(active=False)
    device_repository.save(device)

    response = client.post(
        "/me/activation",
        headers=authorization_headers(device),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "active"
    assert body["license_type"] == "trial"
    assert body["days_remaining"] == Device.TRIAL_DURATION_DAYS - 1
    assert body["expired"] is False


def test_should_reject_activation_when_trial_expired(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device()
    device.license_expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    device_repository.save(device)

    response = client.post(
        "/me/activation",
        headers=authorization_headers(device),
    )

    assert response.status_code == 409
