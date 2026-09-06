from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import PlaylistNotFoundError
from app.domain.entities.playlist import Playlist
from app.domain.enums.playlist_status import PlaylistStatus
from app.domain.repositories.playlist_repository import PlaylistRepository


@dataclass(frozen=True)
class SetPlaylistStatusCommand:
    playlist_id: UUID
    status: PlaylistStatus


class SetPlaylistStatusUseCase:
    def __init__(self, repository: PlaylistRepository) -> None:
        self._repository = repository

    def execute(
        self,
        command: SetPlaylistStatusCommand,
    ) -> Playlist:
        playlist = self._repository.find_by_id(command.playlist_id)

        if playlist is None:
            raise PlaylistNotFoundError(
                f"Playlist {command.playlist_id} does not exist."
            )

        if command.status == PlaylistStatus.ACTIVE:
            playlist.activate()
        elif command.status == PlaylistStatus.DISABLED:
            playlist.disable()
        else:
            raise ValueError(
                f"Unsupported Playlist status: {command.status.value}"
            )

        self._repository.save(playlist)

        return playlist
