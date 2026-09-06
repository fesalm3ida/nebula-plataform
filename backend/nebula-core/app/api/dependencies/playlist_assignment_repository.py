from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session as SQLAlchemySession

from app.api.dependencies.database import get_db
from app.domain.repositories.playlist_assignment_repository import (
    PlaylistAssignmentRepository,
)
from app.infrastructure.repositories.postgresql_playlist_assignment_repository import (
    PostgreSQLPlaylistAssignmentRepository,
)


def get_playlist_assignment_repository(
    database_session: Annotated[
        SQLAlchemySession,
        Depends(get_db),
    ],
) -> PlaylistAssignmentRepository:
    return PostgreSQLPlaylistAssignmentRepository(database_session)
