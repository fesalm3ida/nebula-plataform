import asyncio

import httpx
import pytest

from app.application.exceptions import CoreCommunicationError
from app.infrastructure.clients.httpx_nebula_core_client import (
    HTTPXNebulaCoreClient,
)


def _playlist_payload() -> dict:
    return {
        "playlist_id": "7f9a1b2c-3d4e-4f5a-8b6c-000000000001",
        "name": "Lista Principal",
        "format": "m3u",
        "source_url": "https://example.com/playlist.m3u",
        "status": "active",
    }


def test_should_list_playlists() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"playlists": [_playlist_payload()]},
        )

    client = HTTPXNebulaCoreClient(
        base_url="https://core",
        service_token="token",
        transport=httpx.MockTransport(handler),
    )

    playlists = asyncio.run(client.list_playlists())

    assert len(playlists) == 1
    assert playlists[0].name == "Lista Principal"
    assert playlists[0].format == "m3u"


def test_should_list_devices() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "devices": [
                    {
                        "device_id": "7f9a1b2c-3d4e-4f5a-8b6c-000000000002",
                        "platform": "android_tv",
                        "status": "active",
                        "app_version": "0.3.0",
                        "created_at": "2026-09-06T00:00:00Z",
                    }
                ]
            },
        )

    client = HTTPXNebulaCoreClient(
        base_url="https://core",
        service_token="token",
        transport=httpx.MockTransport(handler),
    )

    devices = asyncio.run(client.list_devices())

    assert len(devices) == 1
    assert devices[0].platform == "android_tv"
    assert devices[0].status == "active"


def test_should_raise_core_error_on_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(502, json={})

    client = HTTPXNebulaCoreClient(
        base_url="https://core",
        service_token="token",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(CoreCommunicationError):
        asyncio.run(client.list_playlists())
