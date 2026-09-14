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
from app.infrastructure.repositories.in_memory_payment_repository import (
    InMemoryPaymentRepository,
)
from app.main import app


client = TestClient(app)


def make_active_device() -> Device:
    device = Device(
        fingerprint=DeviceFingerprint("a" * 64),
        mac_address=MacAddress("02:1A:2B:3C:4D:5E"),
        platform=DevicePlatform.ANDROID_TV,
        app_version=AppVersion("0.3.0"),
    )
    device.activate()

    return device


def authorization_headers(device: Device) -> dict[str, str]:
    return {"Authorization": f"Bearer fake-jwt:{device.device_id}"}


def test_should_list_license_plans(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_active_device()
    device_repository.save(device)

    response = client.get(
        "/me/plans",
        headers=authorization_headers(device),
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body["plans"]) == 2
    assert {plan["product"] for plan in body["plans"]} == {
        "annual",
        "lifetime",
    }


def test_should_create_purchase_checkout(
    device_repository: InMemoryDeviceRepository,
    payment_repository: InMemoryPaymentRepository,
) -> None:
    device = make_active_device()
    device_repository.save(device)

    response = client.post(
        "/me/purchase",
        headers=authorization_headers(device),
        json={"product": "annual"},
    )

    assert response.status_code == 201

    body = response.json()

    assert body["payment_id"]
    assert body["checkout_url"].startswith("https://")

    payments = payment_repository.find_all_by_device_id(device.device_id)

    assert len(payments) == 1


def test_should_approve_payment_and_grant_license(
    device_repository: InMemoryDeviceRepository,
    payment_repository: InMemoryPaymentRepository,
) -> None:
    device = make_active_device()
    device_repository.save(device)

    client.post(
        "/me/purchase",
        headers=authorization_headers(device),
        json={"product": "lifetime"},
    )

    response = client.post(
        "/webhooks/mercadopago",
        json={"type": "payment", "data": {"id": "123456"}},
    )

    assert response.status_code == 200
    assert response.json()["approved"] == "true"

    persisted = device_repository.find_by_id(device.device_id)

    assert persisted is not None
    assert persisted.license_type == LicenseType.LIFETIME
    assert persisted.license_expires_at is None


def test_should_reject_webhook_without_payment_id() -> None:
    response = client.post(
        "/webhooks/mercadopago",
        json={"type": "payment", "data": {}},
    )

    assert response.status_code == 422
