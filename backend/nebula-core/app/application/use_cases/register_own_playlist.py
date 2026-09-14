from dataclasses import dataclass
from uuid import UUID

from app.domain.entities.device import Device
from app.domain.entities.playlist import Playlist
from app.domain.entities.playlist_assignment import PlaylistAssignment
from app.domain.enums.playlist_format import PlaylistFormat
from app.domain.repositories.playlist_assignment_repository import (
    PlaylistAssignmentRepository,
)
from app.domain.repositories.playlist_repository import PlaylistRepository


@dataclass(frozen=True)
class RegisterOwnPlaylistCommand:
    device: Device
    name: str
    source_url: str
    format: str = "m3u"


@dataclass(frozen=True)
class RegisterOwnPlaylistResult:
    playlist_id: UUID
    assignment_id: UUID
    name: str
    format: str
    source_url: str
    status: str


class RegisterOwnPlaylistUseCase:
    """O **usuário** cadastra a própria lista no portal.

    Cria a Playlist e a associa ao Device dele. Como só existe uma lista
    ativa por Device, uma associação anterior é revogada (troca de lista).
    """

    def __init__(
        self,
        playlist_repository: PlaylistRepository,
        assignment_repository: PlaylistAssignmentRepository,
    ) -> None:
        self._playlists = playlist_repository
        self._assignments = assignment_repository

    def execute(
        self,
        command: RegisterOwnPlaylistCommand,
    ) -> RegisterOwnPlaylistResult:
        playlist = Playlist(
            name=command.name,
            format=PlaylistFormat(command.format),
            source_url=command.source_url,
        )

        self._playlists.save(playlist)

        current = self._assignments.find_active_by_device_id(
            command.device.device_id
        )

        if current is not None:
            current.revoke()
            self._assignments.save(current)

        assignment = PlaylistAssignment(
            device_id=command.device.device_id,
            playlist_id=playlist.playlist_id,
        )

        self._assignments.save(assignment)

        return RegisterOwnPlaylistResult(
            playlist_id=playlist.playlist_id,
            assignment_id=assignment.assignment_id,
            name=playlist.name,
            format=playlist.format.value,
            source_url=playlist.source_url,
            status=playlist.status.value,
        )
