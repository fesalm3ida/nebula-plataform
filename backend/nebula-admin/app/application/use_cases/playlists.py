from dataclasses import dataclass
from uuid import UUID

from app.application.ports.nebula_core_gateway import NebulaCoreGateway


@dataclass(frozen=True)
class PlaylistSummary:
    """Contrato de Playlist adaptado para a interface administrativa."""

    playlist_id: UUID
    name: str
    format: str
    source_url: str
    status: str


@dataclass(frozen=True)
class ListPlaylistsResult:
    playlists: list[PlaylistSummary]


@dataclass(frozen=True)
class CreatePlaylistCommand:
    name: str
    format: str
    source_url: str


class ListPlaylistsUseCase:
    def __init__(self, gateway: NebulaCoreGateway) -> None:
        self._gateway = gateway

    async def execute(self) -> ListPlaylistsResult:
        core_playlists = await self._gateway.list_playlists()

        return ListPlaylistsResult(
            playlists=[self._to_summary(playlist) for playlist in core_playlists]
        )

    @staticmethod
    def _to_summary(playlist) -> PlaylistSummary:
        return PlaylistSummary(
            playlist_id=playlist.playlist_id,
            name=playlist.name,
            format=playlist.format,
            source_url=playlist.source_url,
            status=playlist.status,
        )


class CreatePlaylistUseCase:
    def __init__(self, gateway: NebulaCoreGateway) -> None:
        self._gateway = gateway

    async def execute(
        self,
        command: CreatePlaylistCommand,
    ) -> PlaylistSummary:
        core_playlist = await self._gateway.create_playlist(
            command.name,
            command.format,
            command.source_url,
        )

        return PlaylistSummary(
            playlist_id=core_playlist.playlist_id,
            name=core_playlist.name,
            format=core_playlist.format,
            source_url=core_playlist.source_url,
            status=core_playlist.status,
        )
