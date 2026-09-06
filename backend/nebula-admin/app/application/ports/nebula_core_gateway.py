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
