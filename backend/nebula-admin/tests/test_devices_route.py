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
