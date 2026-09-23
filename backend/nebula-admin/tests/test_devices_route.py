from uuid import uuid4

from fastapi.testclient import TestClient

from app.application.ports.nebula_core_gateway import CoreDevice
from app.application.security.admin_token_service import AdminTokenService
from tests.conftest import FakeNebulaCoreGateway, admin_token_value


def auth_headers(service: AdminTokenService) -> dict[str, str]:
    return {"Authorization": f"Bearer {admin_token_value(service)}"}


def test_should_list_devices(
    client: TestClient,
    admin_token_service: AdminTokenService,
    fake_core_gateway: FakeNebulaCoreGateway,
) -> None:
    fake_core_gateway._devices.append(
        CoreDevice(
            device_id=uuid4(),
            platform="android_tv",
            status="active",
            app_version="0.3.0",
            created_at="2026-09-06T00:00:00Z",
        )
    )

    response = client.get(
        "/admin/devices",
        headers=auth_headers(admin_token_service),
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body["devices"]) == 1
    assert body["devices"][0]["platform"] == "android_tv"
    assert body["devices"][0]["status"] == "active"


def test_should_reject_without_token(client: TestClient) -> None:
    response = client.get("/admin/devices")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_should_activate_device(
    client: TestClient,
    admin_token_service: AdminTokenService,
    fake_core_gateway: FakeNebulaCoreGateway,
) -> None:
    device = fake_core_gateway.add_device()

    response = client.post(
        f"/admin/devices/{device.device_id}/activate",
        headers=auth_headers(admin_token_service),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["device_id"] == str(device.device_id)
    assert body["status"] == "active"


def test_should_block_device(
    client: TestClient,
    admin_token_service: AdminTokenService,
    fake_core_gateway: FakeNebulaCoreGateway,
) -> None:
    device = fake_core_gateway.add_device(status="active")

    response = client.post(
        f"/admin/devices/{device.device_id}/block",
        headers=auth_headers(admin_token_service),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "blocked"


def test_should_return_404_for_unknown_device(
    client: TestClient,
    admin_token_service: AdminTokenService,
) -> None:
    response = client.post(
        f"/admin/devices/{uuid4()}/activate",
        headers=auth_headers(admin_token_service),
    )

    assert response.status_code == 404


def test_should_reject_lifecycle_without_token(
    client: TestClient,
    fake_core_gateway: FakeNebulaCoreGateway,
) -> None:
    device = fake_core_gateway.add_device()

    response = client.post(f"/admin/devices/{device.device_id}/activate")

    assert response.status_code == 401


def test_should_delete_device(
    client: TestClient,
    admin_token_service: AdminTokenService,
    fake_core_gateway: FakeNebulaCoreGateway,
) -> None:
    device = fake_core_gateway.add_device(status="pending")

    response = client.delete(
        f"/admin/devices/{device.device_id}",
        headers=auth_headers(admin_token_service),
    )

    assert response.status_code == 204

    listing = client.get(
        "/admin/devices",
        headers=auth_headers(admin_token_service),
    )

    assert listing.json()["devices"] == []


def test_should_return_409_when_device_has_payments(
    client: TestClient,
    admin_token_service: AdminTokenService,
    fake_core_gateway: FakeNebulaCoreGateway,
) -> None:
    device = fake_core_gateway.add_device(status="active")
    fake_core_gateway._device_has_payments = True

    response = client.delete(
        f"/admin/devices/{device.device_id}",
        headers=auth_headers(admin_token_service),
    )

    assert response.status_code == 409


def test_should_return_404_when_deleting_unknown_device(
    client: TestClient,
    admin_token_service: AdminTokenService,
) -> None:
    response = client.delete(
        f"/admin/devices/{uuid4()}",
        headers=auth_headers(admin_token_service),
    )

    assert response.status_code == 404
