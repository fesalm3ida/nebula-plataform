from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import get_settings
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


def admin_headers() -> dict[str, str]:
    return {
        "X-Admin-Token": get_settings().admin_api_key,
    }


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


def create_playlist(
    name: str = "Lista Principal",
    source_url: str = "https://example.com/playlist.m3u",
) -> dict:
    response = client.post(
        "/playlists",
        headers=admin_headers(),
        json={
            "name": name,
            "format": "m3u",
            "source_url": source_url,
        },
    )

    assert response.status_code == 201

    return response.json()


def test_should_reject_without_admin_token() -> None:
    response = client.get("/playlists")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_should_reject_invalid_admin_token() -> None:
    response = client.get(
        "/playlists",
        headers={"X-Admin-Token": "wrong-token"},
    )

    assert response.status_code == 401


def test_should_create_playlist() -> None:
    response = client.post(
        "/playlists",
        headers=admin_headers(),
        json={
            "name": "Lista Principal",
            "format": "m3u",
            "source_url": "https://example.com/playlist.m3u",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["playlist_id"]
    assert body["name"] == "Lista Principal"
    assert body["format"] == "m3u"
    assert body["source_url"] == "https://example.com/playlist.m3u"
    assert body["status"] == "active"


def test_should_list_playlists() -> None:
    create_playlist()

    response = client.get("/playlists", headers=admin_headers())

    assert response.status_code == 200
    assert len(response.json()["playlists"]) == 1


def test_should_get_playlist() -> None:
    created = create_playlist()

    response = client.get(
        f"/playlists/{created['playlist_id']}",
        headers=admin_headers(),
    )

    assert response.status_code == 200
    assert response.json()["playlist_id"] == created["playlist_id"]


def test_should_return_not_found_for_unknown_playlist() -> None:
    response = client.get(
        f"/playlists/{uuid4()}",
        headers=admin_headers(),
    )

    assert response.status_code == 404


def test_should_update_playlist() -> None:
    created = create_playlist()

    response = client.patch(
        f"/playlists/{created['playlist_id']}",
        headers=admin_headers(),
        json={
            "name": "Lista Secundária",
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Lista Secundária"


def test_should_set_playlist_status() -> None:
    created = create_playlist()

    response = client.post(
        f"/playlists/{created['playlist_id']}/status",
        headers=admin_headers(),
        json={
            "status": "disabled",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "disabled"


def test_should_assign_playlist_to_device(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    created = create_playlist()

    response = client.post(
        "/playlists/assignments",
        headers=admin_headers(),
        json={
            "device_id": str(device.device_id),
            "playlist_id": created["playlist_id"],
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["device_id"] == str(device.device_id)
    assert body["playlist_id"] == created["playlist_id"]
    assert body["status"] == "active"


def test_should_reject_assignment_for_unknown_device() -> None:
    created = create_playlist()

    response = client.post(
        "/playlists/assignments",
        headers=admin_headers(),
        json={
            "device_id": str(uuid4()),
            "playlist_id": created["playlist_id"],
        },
    )

    assert response.status_code == 404


def test_should_reject_assignment_without_admin_token() -> None:
    response = client.post(
        "/playlists/assignments",
        json={
            "device_id": str(uuid4()),
            "playlist_id": str(uuid4()),
        },
    )

    assert response.status_code == 401
