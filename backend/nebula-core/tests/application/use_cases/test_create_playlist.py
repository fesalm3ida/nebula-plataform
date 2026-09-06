import pytest

from app.application.use_cases.create_playlist import (
    CreatePlaylistCommand,
    CreatePlaylistUseCase,
)
from app.domain.enums.playlist_format import PlaylistFormat
from app.domain.enums.playlist_status import PlaylistStatus
from app.infrastructure.repositories.in_memory_playlist_repository import (
    InMemoryPlaylistRepository,
)


def test_should_create_active_playlist() -> None:
    repository = InMemoryPlaylistRepository()
    use_case = CreatePlaylistUseCase(repository)

    result = use_case.execute(
        CreatePlaylistCommand(
            name="Lista Principal",
            format=PlaylistFormat.M3U,
            source_url="https://example.com/playlist.m3u",
        )
    )

    assert result.name == "Lista Principal"
    assert result.format == PlaylistFormat.M3U
    assert result.source_url == "https://example.com/playlist.m3u"
    assert result.status == PlaylistStatus.ACTIVE
    assert repository.find_by_id(result.playlist_id) is not None


def test_should_reject_empty_name() -> None:
    repository = InMemoryPlaylistRepository()
    use_case = CreatePlaylistUseCase(repository)

    with pytest.raises(
        ValueError,
        match="name cannot be empty",
    ):
        use_case.execute(
            CreatePlaylistCommand(
                name="   ",
                format=PlaylistFormat.M3U,
                source_url="https://example.com/playlist.m3u",
            )
        )


def test_should_normalize_name_and_source_url() -> None:
    repository = InMemoryPlaylistRepository()
    use_case = CreatePlaylistUseCase(repository)

    result = use_case.execute(
        CreatePlaylistCommand(
            name="  Lista Principal  ",
            format=PlaylistFormat.M3U,
            source_url="  https://example.com/playlist.m3u  ",
        )
    )

    assert result.name == "Lista Principal"
    assert result.source_url == "https://example.com/playlist.m3u"
