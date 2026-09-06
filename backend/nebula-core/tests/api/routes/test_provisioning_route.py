from fastapi.testclient import TestClient

from app.domain.entities.device import Device
from app.domain.entities.playlist import Playlist
from app.domain.entities.playlist_assignment import PlaylistAssignment
from app.domain.enums.device_platform import DevicePlatform
from app.domain.enums.playlist_format import PlaylistFormat
from app.domain.value_objects.app_version import AppVersion
from app.domain.value_objects.device_fingerprint import DeviceFingerprint
from app.domain.value_objects.mac_address import MacAddress
from app.infrastructure.repositories.in_memory_device_repository import (
    InMemoryDeviceRepository,
)
from app.infrastructure.repositories.in_memory_playlist_assignment_repository import (
    InMemoryPlaylistAssignmentRepository,
)
from app.infrastructure.repositories.in_memory_playlist_repository import (
    InMemoryPlaylistRepository,
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
    return {
        "Authorization": f"Bearer fake-jwt:{device.device_id}",
    }


def test_should_provision_active_device(
    device_repository: InMemoryDeviceRepository,
    playlist_repository: InMemoryPlaylistRepository,
    playlist_assignment_repository: InMemoryPlaylistAssignmentRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    playlist = Playlist(
        name="Lista Principal",
        format=PlaylistFormat.M3U,
        source_url="https://example.com/playlist.m3u",
    )
    playlist_repository.save(playlist)

    playlist_assignment_repository.save(
        PlaylistAssignment(
            device_id=device.device_id,
            playlist_id=playlist.playlist_id,
        )
    )

    response = client.get(
        "/me/provisioning",
        headers=authorization_headers(device),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["playlist_id"] == str(playlist.playlist_id)
    assert body["name"] == "Lista Principal"
    assert body["format"] == "m3u"
    assert body["source_url"] == "https://example.com/playlist.m3u"
    assert body["status"] == "active"


def test_should_return_not_found_when_no_assignment(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    response = client.get(
        "/me/provisioning",
        headers=authorization_headers(device),
    )

    assert response.status_code == 404


def test_should_reject_without_bearer_token() -> None:
    response = client.get("/me/provisioning")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
