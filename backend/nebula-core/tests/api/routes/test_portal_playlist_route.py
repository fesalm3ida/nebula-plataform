from fastapi.testclient import TestClient

from app.domain.entities.device import Device
from app.domain.enums.device_platform import DevicePlatform
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


def make_device() -> Device:
    return Device(
        fingerprint=DeviceFingerprint("a" * 64),
        mac_address=MacAddress("02:1A:2B:3C:4D:5E"),
        platform=DevicePlatform.ANDROID_TV,
        app_version=AppVersion("0.3.0"),
    )


def authorization_headers(device: Device) -> dict[str, str]:
    return {"Authorization": f"Bearer fake-jwt:{device.device_id}"}


def test_should_register_own_playlist(
    device_repository: InMemoryDeviceRepository,
    playlist_repository: InMemoryPlaylistRepository,
    playlist_assignment_repository: InMemoryPlaylistAssignmentRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    response = client.post(
        "/me/playlist",
        headers=authorization_headers(device),
        json={
            "name": "Minha Lista",
            "source_url": "http://host/get.php?username=u&password=p",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["name"] == "Minha Lista"
    assert body["format"] == "m3u"
    assert body["status"] == "active"

    active = playlist_assignment_repository.find_all_active_by_device_id(
        device.device_id
    )

    assert len(active) == 1
    assert str(active[0].playlist_id) == body["playlist_id"]


def test_should_return_registered_playlist(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    client.post(
        "/me/playlist",
        headers=authorization_headers(device),
        json={"name": "Lista A", "source_url": "http://host/a.m3u"},
    )

    response = client.get(
        "/me/playlist",
        headers=authorization_headers(device),
    )

    assert response.status_code == 200
    assert response.json()["playlist"]["name"] == "Lista A"


def test_should_replace_previous_playlist(
    device_repository: InMemoryDeviceRepository,
    playlist_assignment_repository: InMemoryPlaylistAssignmentRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    headers = authorization_headers(device)

    client.post(
        "/me/playlist",
        headers=headers,
        json={"name": "Antiga", "source_url": "http://host/old.m3u"},
    )

    client.post(
        "/me/playlist",
        headers=headers,
        json={"name": "Nova", "source_url": "http://host/new.m3u"},
    )

    response = client.get("/me/playlist", headers=headers)

    assert response.json()["playlist"]["name"] == "Nova"

    active = playlist_assignment_repository.find_all_active_by_device_id(
        device.device_id
    )

    assert len(active) == 1


def test_should_return_null_when_no_playlist(
    device_repository: InMemoryDeviceRepository,
) -> None:
    device = make_device()
    device_repository.save(device)

    response = client.get(
        "/me/playlist",
        headers=authorization_headers(device),
    )

    assert response.status_code == 200
    assert response.json()["playlist"] is None
