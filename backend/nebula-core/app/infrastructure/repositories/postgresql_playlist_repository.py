from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session as SQLAlchemySession

from app.domain.entities.playlist import Playlist
from app.domain.repositories.playlist_repository import PlaylistRepository
from app.infrastructure.persistence.mappers.playlist_mapper import (
    PlaylistMapper,
)
from app.infrastructure.persistence.models.playlist_model import (
    PlaylistModel,
)


class PostgreSQLPlaylistRepository(PlaylistRepository):
    def __init__(
        self,
        database_session: SQLAlchemySession,
    ) -> None:
        self._database_session = database_session

    def save(self, playlist: Playlist) -> None:
        model = PlaylistMapper.to_model(playlist)

        self._database_session.merge(model)
        self._database_session.commit()

    def find_by_id(
        self,
        playlist_id: UUID,
    ) -> Playlist | None:
        statement = select(PlaylistModel).where(
            PlaylistModel.playlist_id == playlist_id
        )

        model = self._database_session.execute(
            statement
        ).scalar_one_or_none()

        if model is None:
            return None

        return PlaylistMapper.to_domain(model)

    def find_all(self) -> list[Playlist]:
        statement = select(PlaylistModel).order_by(
            PlaylistModel.name
        )

        models = self._database_session.execute(
            statement
        ).scalars().all()

        return [PlaylistMapper.to_domain(model) for model in models]
