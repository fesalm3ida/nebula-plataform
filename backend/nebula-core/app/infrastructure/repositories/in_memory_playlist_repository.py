from uuid import UUID

from app.domain.entities.playlist import Playlist
from app.domain.repositories.playlist_repository import PlaylistRepository


class InMemoryPlaylistRepository(PlaylistRepository):
    def __init__(self) -> None:
        self._playlists: dict[UUID, Playlist] = {}

    def save(self, playlist: Playlist) -> None:
        self._playlists[playlist.playlist_id] = playlist

    def find_by_id(self, playlist_id: UUID) -> Playlist | None:
        return self._playlists.get(playlist_id)

    def find_all(self) -> list[Playlist]:
        return sorted(
            self._playlists.values(),
            key=lambda playlist: playlist.name,
        )
