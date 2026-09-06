from app.domain.entities.playlist import Playlist
from app.domain.enums.playlist_format import PlaylistFormat
from app.domain.enums.playlist_status import PlaylistStatus
from app.infrastructure.persistence.models.playlist_model import (
    PlaylistModel,
)


class PlaylistMapper:
    @staticmethod
    def to_model(playlist: Playlist) -> PlaylistModel:
        return PlaylistModel(
            playlist_id=playlist.playlist_id,
            name=playlist.name,
            format=playlist.format.value,
            source_url=playlist.source_url,
            status=playlist.status.value,
            created_at=playlist.created_at,
            updated_at=playlist.updated_at,
        )

    @staticmethod
    def to_domain(model: PlaylistModel) -> Playlist:
        return Playlist(
            name=model.name,
            format=PlaylistFormat(model.format),
            source_url=model.source_url,
            playlist_id=model.playlist_id,
            status=PlaylistStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
