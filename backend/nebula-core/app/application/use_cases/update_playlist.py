from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import PlaylistNotFoundError
from app.domain.entities.playlist import Playlist
from app.domain.repositories.playlist_repository import PlaylistRepository


@dataclass(frozen=True)
class UpdatePlaylistCommand:
    playlist_id: UUID
    name: str | None = None
    source_url: str | None = None


class UpdatePlaylistUseCase:
    def __init__(self, repository: PlaylistRepository) -> None:
        self._repository = repository

    def execute(
        self,
        command: UpdatePlaylistCommand,
    ) -> Playlist:
        playlist = self._repository.find_by_id(command.playlist_id)

        if playlist is None:
            raise PlaylistNotFoundError(
                f"Playlist {command.playlist_id} does not exist."
            )

        if command.name is not None:
            playlist.update_name(command.name)

        if command.source_url is not None:
            playlist.update_source_url(command.source_url)

        self._repository.save(playlist)

        return playlist
