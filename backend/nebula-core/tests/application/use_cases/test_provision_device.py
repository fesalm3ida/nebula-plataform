from uuid import uuid4

import pytest

from app.application.exceptions import (
    NoPlaylistAssignedError,
    PlaylistNotAvailableError,
    PlaylistNotFoundError,
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


def make_playlist() -> Playlist:
    return Playlist(
        name="Lista Principal",
        format=PlaylistFormat.M3U,
        source_url="https://example.com/playlist.m3u",
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

    assert result.playlist_id == playlist.playlist_id
    assert result.name == "Lista Principal"
    assert result.format == PlaylistFormat.M3U
    assert result.source_url == "https://example.com/playlist.m3u"


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
