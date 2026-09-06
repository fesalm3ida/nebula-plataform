from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session as SQLAlchemySession

from app.api.dependencies.database import get_db
from app.domain.repositories.playlist_repository import PlaylistRepository
from app.infrastructure.repositories.postgresql_playlist_repository import (
    PostgreSQLPlaylistRepository,
)


def get_playlist_repository(
    database_session: Annotated[
        SQLAlchemySession,
        Depends(get_db),
    ],
) -> PlaylistRepository:
    return PostgreSQLPlaylistRepository(database_session)
