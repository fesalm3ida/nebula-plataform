from fastapi.testclient import TestClient

from tests.conftest import FakeNebulaCoreGateway


def device_headers(token: str = "device-token") -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_should_login_user_with_mac_and_activation_code(
    client: TestClient,
) -> None:
    response = client.post(
        "/portal/auth/login",
        json={
            "mac_address": "02:1A:2B:3C:4D:5E",
            "activation_code": "123456",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["access_token"]
    assert body["device_status"] == "pending"


def test_should_require_device_token(client: TestClient) -> None:
    response = client.get("/portal/device")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_should_return_device_overview(
    client: TestClient,
    fake_core_gateway: FakeNebulaCoreGateway,
) -> None:
    response = client.get(
        "/portal/device",
        headers=device_headers(),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["device_id"]
    assert body["license"]["license_type"] is None
    assert body["playlist"] is None


def test_should_activate_device_from_portal(
    client: TestClient,
) -> None:
    response = client.post(
        "/portal/device/activation",
        headers=device_headers(),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["license"]["license_type"] == "trial"
    assert body["license"]["days_remaining"] == 7


def test_should_register_user_playlist(
    client: TestClient,
) -> None:
    response = client.post(
        "/portal/playlist",
        headers=device_headers(),
        json={
            "name": "Minha Lista",
            "source_url": "http://host/get.php?username=u&password=p",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["name"] == "Minha Lista"
    assert body["status"] == "active"

    overview = client.get("/portal/device", headers=device_headers())

    assert overview.json()["playlist"]["name"] == "Minha Lista"
