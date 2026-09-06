from uuid import uuid4

from fastapi.testclient import TestClient

from app.application.ports.nebula_core_gateway import CorePlaylist
from app.application.security.admin_token_service import AdminTokenService
from tests.conftest import (
    FakeNebulaCoreGateway,
    admin_token_value,
)


def auth_headers(service: AdminTokenService) -> dict[str, str]:
    return {"Authorization": f"Bearer {admin_token_value(service)}"}


def test_should_list_playlists(
    client: TestClient,
    admin_token_service: AdminTokenService,
    fake_core_gateway: FakeNebulaCoreGateway,
) -> None:
    fake_core_gateway._playlists.append(
        CorePlaylist(
            playlist_id=uuid4(),
            name="Lista Principal",
            format="m3u",
            source_url="https://example.com/playlist.m3u",
            status="active",
        )
    )

    response = client.get(
        "/admin/playlists",
        headers=auth_headers(admin_token_service),
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body["playlists"]) == 1
    assert body["playlists"][0]["name"] == "Lista Principal"
    assert body["playlists"][0]["format"] == "m3u"


def test_should_create_playlist(
    client: TestClient,
    admin_token_service: AdminTokenService,
) -> None:
    response = client.post(
        "/admin/playlists",
        headers=auth_headers(admin_token_service),
        json={
            "name": "Lista Nova",
            "format": "m3u",
            "source_url": "https://example.com/new.m3u",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["name"] == "Lista Nova"
    assert body["status"] == "active"


def test_should_reject_without_token(client: TestClient) -> None:
    response = client.get("/admin/playlists")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_should_reject_invalid_token(client: TestClient) -> None:
    response = client.get(
        "/admin/playlists",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


def test_should_assign_playlist_to_device(
    client: TestClient,
    admin_token_service: AdminTokenService,
) -> None:
    response = client.post(
        "/admin/playlists/assignments",
        headers=auth_headers(admin_token_service),
        json={
            "device_id": str(uuid4()),
            "playlist_id": str(uuid4()),
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["status"] == "active"
    assert "assignment_id" in body
