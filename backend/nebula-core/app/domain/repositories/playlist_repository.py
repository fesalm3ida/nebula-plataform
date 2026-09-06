from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.playlist import Playlist


class PlaylistRepository(ABC):
    @abstractmethod
    def save(self, playlist: Playlist) -> None:
        """Create or update a Playlist."""

    @abstractmethod
    def find_by_id(self, playlist_id: UUID) -> Playlist | None:
        """Find a Playlist by its unique identifier."""

    @abstractmethod
    def find_all(self) -> list[Playlist]:
        """Return all registered Playlists."""
