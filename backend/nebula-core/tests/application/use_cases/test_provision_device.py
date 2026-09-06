from uuid import uuid4

import pytest

from app.application.exceptions import (
    NoPlaylistAssignedError,
    PlaylistNotAvailableError,
)
from app.application.use_cases.provision_device import (
    ProvisionDeviceCommand,
    ProvisionDeviceUseCase,
)
from app.domain.entities.playlist import Playlist
from app.domain.entities.playlist_assignment import PlaylistAssignment
from app.domain.enums.playlist_format import PlaylistFormat
from app.infrastructure.repositories.in_memory_playlist_assignment_repository import (
    InMemoryPlaylistAssignmentRepository,
)
from app.infrastructure.repositories.in_memory_playlist_repository import (
    InMemoryPlaylistRepository,
)


def make_playlist(
    name: str = "Lista Principal",
    source_url: str = "https://example.com/playlist.m3u",
) -> Playlist:
    return Playlist(
        name=name,
        format=PlaylistFormat.M3U,
        source_url=source_url,
    )


def test_should_provision_active_assignment() -> None:
    playlist_repository = InMemoryPlaylistRepository()
    assignment_repository = InMemoryPlaylistAssignmentRepository()

    device_id = uuid4()
    playlist = make_playlist()
    playlist_repository.save(playlist)
    assignment_repository.save(
        PlaylistAssignment(
            device_id=device_id,
            playlist_id=playlist.playlist_id,
        )
    )

    use_case = ProvisionDeviceUseCase(
        assignment_repository=assignment_repository,
        playlist_repository=playlist_repository,
    )

    result = use_case.execute(
        ProvisionDeviceCommand(device_id=device_id)
    )

    assert result.device_id == device_id
    assert len(result.content_endpoints) == 1

    endpoint = result.content_endpoints[0]

    assert endpoint.playlist_id == playlist.playlist_id
    assert endpoint.name == "Lista Principal"
    assert endpoint.format == PlaylistFormat.M3U
    assert endpoint.source_url == "https://example.com/playlist.m3u"


def test_should_provision_multiple_active_assignments() -> None:
    playlist_repository = InMemoryPlaylistRepository()
    assignment_repository = InMemoryPlaylistAssignmentRepository()

    device_id = uuid4()
    playlist_a = make_playlist()
    playlist_b = make_playlist(
        name="Lista Secundária",
        source_url="https://example.com/secondary.m3u",
    )
    playlist_repository.save(playlist_a)
    playlist_repository.save(playlist_b)
    assignment_repository.save(
        PlaylistAssignment(
            device_id=device_id,
            playlist_id=playlist_a.playlist_id,
        )
    )
    assignment_repository.save(
        PlaylistAssignment(
            device_id=device_id,
            playlist_id=playlist_b.playlist_id,
        )
    )

    use_case = ProvisionDeviceUseCase(
        assignment_repository=assignment_repository,
        playlist_repository=playlist_repository,
    )

    result = use_case.execute(
        ProvisionDeviceCommand(device_id=device_id)
    )

    assert len(result.content_endpoints) == 2
    assert {ep.source_url for ep in result.content_endpoints} == {
        "https://example.com/playlist.m3u",
        "https://example.com/secondary.m3u",
    }


def test_should_raise_when_device_has_no_assignment() -> None:
    playlist_repository = InMemoryPlaylistRepository()
    assignment_repository = InMemoryPlaylistAssignmentRepository()

    use_case = ProvisionDeviceUseCase(
        assignment_repository=assignment_repository,
        playlist_repository=playlist_repository,
    )

    with pytest.raises(NoPlaylistAssignedError):
        use_case.execute(
            ProvisionDeviceCommand(device_id=uuid4())
        )


def test_should_raise_when_assigned_playlist_is_disabled() -> None:
    playlist_repository = InMemoryPlaylistRepository()
    assignment_repository = InMemoryPlaylistAssignmentRepository()

    device_id = uuid4()
    playlist = make_playlist()
    playlist.disable()
    playlist_repository.save(playlist)
    assignment_repository.save(
        PlaylistAssignment(
            device_id=device_id,
            playlist_id=playlist.playlist_id,
        )
    )

    use_case = ProvisionDeviceUseCase(
        assignment_repository=assignment_repository,
        playlist_repository=playlist_repository,
    )

    with pytest.raises(PlaylistNotAvailableError):
        use_case.execute(
            ProvisionDeviceCommand(device_id=device_id)
        )
