from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CorePlaylist:
    """Subconjunto do contrato de Playlist do Core consumido pelo Admin."""

    playlist_id: UUID
    name: str
    format: str
    source_url: str
    status: str


@dataclass(frozen=True)
class CoreDevice:
    """Subconjunto do contrato de Device do Core consumido pelo Admin."""

    device_id: UUID
    platform: str
    status: str
    app_version: str
    created_at: str


@dataclass(frozen=True)
class CorePlaylistAssignment:
    """Subconjunto do contrato de PlaylistAssignment do Core."""

    assignment_id: UUID
    device_id: UUID
    playlist_id: UUID
    status: str


class NebulaCoreGateway(ABC):
    """Porta de comunicação com o Nebula Core (único dono do domínio/persistência)."""

    @abstractmethod
    async def list_playlists(self) -> list[CorePlaylist]:
        """List playlists from the Nebula Core."""

    @abstractmethod
    async def create_playlist(
        self,
        name: str,
        format: str,
        source_url: str,
    ) -> CorePlaylist:
        """Create a playlist in the Nebula Core."""

    @abstractmethod
    async def list_devices(self) -> list[CoreDevice]:
        """List devices from the Nebula Core (admin)."""

    @abstractmethod
    async def assign_playlist_to_device(
        self,
        device_id: UUID,
        playlist_id: UUID,
    ) -> CorePlaylistAssignment:
        """Assign a playlist to a device in the Nebula Core (admin)."""
