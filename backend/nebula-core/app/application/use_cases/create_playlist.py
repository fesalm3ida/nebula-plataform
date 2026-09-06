from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.entities.playlist import Playlist
from app.domain.enums.playlist_format import PlaylistFormat
from app.domain.enums.playlist_status import PlaylistStatus
from app.domain.repositories.playlist_repository import PlaylistRepository


@dataclass(frozen=True)
class CreatePlaylistCommand:
    name: str
    format: PlaylistFormat
    source_url: str


@dataclass(frozen=True)
class CreatePlaylistResult:
    playlist_id: UUID
    name: str
    format: PlaylistFormat
    source_url: str
    status: PlaylistStatus
    created_at: datetime
    updated_at: datetime


class CreatePlaylistUseCase:
    def __init__(self, repository: PlaylistRepository) -> None:
        self._repository = repository

    def execute(
        self,
        command: CreatePlaylistCommand,
    ) -> CreatePlaylistResult:
        playlist = Playlist(
            name=command.name,
            format=command.format,
            source_url=command.source_url,
        )

        self._repository.save(playlist)

        return CreatePlaylistResult(
            playlist_id=playlist.playlist_id,
            name=playlist.name,
            format=playlist.format,
            source_url=playlist.source_url,
            status=playlist.status,
            created_at=playlist.created_at,
            updated_at=playlist.updated_at,
        )
