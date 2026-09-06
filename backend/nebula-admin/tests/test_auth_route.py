from fastapi.testclient import TestClient

from tests.conftest import ADMIN_EMAIL, ADMIN_PASSWORD


def test_should_login(client: TestClient) -> None:
    response = client.post(
        "/admin/auth/login",
        json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body["email"] == ADMIN_EMAIL
    assert body["role"] == "super_admin"


def test_should_reject_invalid_credentials(client: TestClient) -> None:
    response = client.post(
        "/admin/auth/login",
        json={
            "email": ADMIN_EMAIL,
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
