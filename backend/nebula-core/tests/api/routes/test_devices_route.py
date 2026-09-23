from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.domain.entities.device import Device
from app.domain.entities.payment import Payment
from app.domain.enums.device_platform import DevicePlatform
from app.domain.enums.license_product import LicenseProduct
from app.domain.value_objects.app_version import AppVersion
from app.domain.value_objects.device_fingerprint import DeviceFingerprint
from app.domain.value_objects.mac_address import MacAddress
from app.infrastructure.repositories.in_memory_payment_repository import (
    InMemoryPaymentRepository,
)
from app.infrastructure.repositories.in_memory_device_repository import (
    InMemoryDeviceRepository,
)
from app.main import app


client = TestClient(app)


def admin_headers() -> dict[str, str]:
    return {
        "X-Admin-Token": get_settings().admin_api_key,
    }


def make_active_device() -> Device:
    device = Device(
        fingerprint=DeviceFingerprint("b" * 64),
        mac_address=MacAddress("02:AA:BB:CC:DD:EE"),
        platform=DevicePlatform.ANDROID_TV,
        app_version=AppVersion("0.3.0"),
    )
    device.activate()

    return device


def valid_payload() -> dict[str, str]:
    return {
        "fingerprint": "a" * 64,
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "platform": "android_tv",
        "app_version": "0.1.0",
    }


def register_device() -> dict:
    response = client.post(
        "/devices/register",
        json=valid_payload(),
    )

    assert response.status_code == 201

    return response.json()


def test_should_register_device_through_http(
    device_repository: InMemoryDeviceRepository,
) -> None:
    response = client.post(
        "/devices/register",
        json=valid_payload(),
    )

    assert response.status_code == 201

    body = response.json()

    assert body["device_id"]
    assert len(body["device_key"]) >= 32
    assert body["status"] == "pending"


def test_should_return_conflict_for_duplicate_device(
    device_repository: InMemoryDeviceRepository,
) -> None:
    first_response = client.post(
        "/devices/register",
        json=valid_payload(),
    )

    second_response = client.post(
        "/devices/register",
        json=valid_payload(),
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert "already registered" in second_response.json()["detail"]


def test_should_reject_invalid_fingerprint_length(
    device_repository: InMemoryDeviceRepository,
) -> None:
    payload = valid_payload()
    payload["fingerprint"] = "invalid"

    response = client.post(
        "/devices/register",
        json=payload,
    )

    assert response.status_code == 422


def test_should_activate_registered_device_through_http(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = register_device()

    response = client.post(
        f"/devices/{device['device_id']}/activate",
        headers=admin_headers(),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["device_id"] == device["device_id"]
    assert body["status"] == "active"


def test_should_return_not_found_when_activating_unknown_device(
    device_repository: InMemoryDeviceRepository,
) -> None:
    response = client.post(
        "/devices/00000000-0000-0000-0000-000000000000/activate",
        headers=admin_headers(),
    )

    assert response.status_code == 404


def test_should_return_conflict_when_device_is_already_active(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = register_device()

    first_response = client.post(
        f"/devices/{device['device_id']}/activate",
        headers=admin_headers(),
    )

    second_response = client.post(
        f"/devices/{device['device_id']}/activate",
        headers=admin_headers(),
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 409


def test_should_block_device(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = register_device()

    response = client.post(
        f"/devices/{device['device_id']}/block",
        headers=admin_headers(),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "blocked"


def test_should_revoke_device(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = register_device()

    response = client.post(
        f"/devices/{device['device_id']}/revoke",
        headers=admin_headers(),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "revoked"


def test_should_expire_device(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = register_device()

    response = client.post(
        f"/devices/{device['device_id']}/expire",
        headers=admin_headers(),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "expired"


def test_should_return_conflict_when_blocking_blocked_device(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = register_device()

    first_response = client.post(
        f"/devices/{device['device_id']}/block",
        headers=admin_headers(),
    )

    second_response = client.post(
        f"/devices/{device['device_id']}/block",
        headers=admin_headers(),
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 409


def test_should_reject_lifecycle_without_admin_token(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = register_device()

    response = client.post(
        f"/devices/{device['device_id']}/block",
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_should_reject_lifecycle_with_invalid_admin_token(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = register_device()

    response = client.post(
        f"/devices/{device['device_id']}/block",
        headers={"X-Admin-Token": "wrong-token"},
    )

    assert response.status_code == 401


def test_should_list_devices(
    device_repository: InMemoryDeviceRepository,
) -> None:
    register_device()

    response = client.get("/devices", headers=admin_headers())

    assert response.status_code == 200

    body = response.json()

    assert len(body["devices"]) == 1
    assert body["devices"][0]["status"] == "pending"
    assert "device_id" in body["devices"][0]


def test_should_reject_list_without_admin_token(
    device_repository: InMemoryDeviceRepository,
) -> None:
    register_device()

    response = client.get("/devices")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_should_delete_device_without_payments(
    device_repository: InMemoryDeviceRepository,
) -> None:
    body = register_device()
    device_id = body["device_id"]

    response = client.delete(
        f"/devices/{device_id}",
        headers=admin_headers(),
    )

    assert response.status_code == 204
    assert device_repository.find_by_id(UUID(device_id)) is None


def test_should_reject_delete_of_device_with_payments(
    device_repository: InMemoryDeviceRepository,
    payment_repository: InMemoryPaymentRepository,
) -> None:
    device = make_active_device()
    device_repository.save(device)

    payment_repository.save(
        Payment(
            device_id=device.device_id,
            product=LicenseProduct.LIFETIME,
            amount_cents=29900,
        )
    )

    response = client.delete(
        f"/devices/{device.device_id}",
        headers=admin_headers(),
    )

    assert response.status_code == 409
    assert device_repository.find_by_id(device.device_id) is not None


def test_should_return_404_when_deleting_unknown_device() -> None:
    response = client.delete(
        f"/devices/{uuid4()}",
        headers=admin_headers(),
    )

    assert response.status_code == 404


def test_should_require_admin_token_to_delete(
    device_repository: InMemoryDeviceRepository,
) -> None:
    body = register_device()

    response = client.delete(f"/devices/{body['device_id']}")

    assert response.status_code == 401


def test_should_register_webos_tv_device(
    device_repository: InMemoryDeviceRepository,
) -> None:
    """O app da LG Smart TV registra com a plataforma webos_tv."""
    payload = valid_payload()
    payload["platform"] = "webos_tv"
    payload["fingerprint"] = "c" * 64
    payload["mac_address"] = "02:99:88:77:66:55"

    response = client.post("/devices/register", json=payload)

    assert response.status_code == 201

    body = response.json()

    assert body["activation_code"]
    assert body["mac_address"] == "02:99:88:77:66:55"


def test_should_register_ios_device(
    device_repository: InMemoryDeviceRepository,
) -> None:
    payload = valid_payload()
    payload["platform"] = "ios"
    payload["fingerprint"] = "d" * 64
    payload["mac_address"] = "02:11:22:33:44:55"

    response = client.post("/devices/register", json=payload)

    assert response.status_code == 201
