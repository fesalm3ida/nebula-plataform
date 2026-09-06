from app.domain.entities.playlist import Playlist
from app.domain.enums.playlist_format import PlaylistFormat
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


def test_should_save_and_find_playlist_by_id() -> None:
    repository = InMemoryPlaylistRepository()
    playlist = make_playlist()

    repository.save(playlist)

    restored = repository.find_by_id(playlist.playlist_id)

    assert restored is not None
    assert restored.playlist_id == playlist.playlist_id
    assert restored.name == playlist.name
    assert restored.source_url == playlist.source_url


def test_should_return_none_for_unknown_playlist() -> None:
    repository = InMemoryPlaylistRepository()

    assert repository.find_by_id(make_playlist().playlist_id) is None


def test_should_list_all_playlists_sorted_by_name() -> None:
    repository = InMemoryPlaylistRepository()

    playlist_b = make_playlist(name="Beta")
    playlist_a = make_playlist(name="Alpha")

    repository.save(playlist_b)
    repository.save(playlist_a)

    playlists = repository.find_all()

    assert [playlist.name for playlist in playlists] == [
        "Alpha",
        "Beta",
    ]
