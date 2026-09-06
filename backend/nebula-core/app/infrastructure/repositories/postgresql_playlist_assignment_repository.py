from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session as SQLAlchemySession

from app.domain.entities.playlist_assignment import PlaylistAssignment
from app.domain.enums.playlist_assignment_status import (
    PlaylistAssignmentStatus,
)
from app.domain.repositories.playlist_assignment_repository import (
    PlaylistAssignmentRepository,
)
from app.infrastructure.persistence.mappers.playlist_assignment_mapper import (
    PlaylistAssignmentMapper,
)
from app.infrastructure.persistence.models.playlist_assignment_model import (
    PlaylistAssignmentModel,
)


class PostgreSQLPlaylistAssignmentRepository(
    PlaylistAssignmentRepository
):
    def __init__(
        self,
        database_session: SQLAlchemySession,
    ) -> None:
        self._database_session = database_session

    def save(self, assignment: PlaylistAssignment) -> None:
        model = PlaylistAssignmentMapper.to_model(assignment)

        self._database_session.merge(model)
        self._database_session.commit()

    def find_by_id(
        self,
        assignment_id: UUID,
    ) -> PlaylistAssignment | None:
        statement = select(PlaylistAssignmentModel).where(
            PlaylistAssignmentModel.assignment_id == assignment_id
        )

        model = self._database_session.execute(
            statement
        ).scalar_one_or_none()

        if model is None:
            return None

        return PlaylistAssignmentMapper.to_domain(model)

    def find_active_by_device_id(
        self,
        device_id: UUID,
    ) -> PlaylistAssignment | None:
        statement = select(PlaylistAssignmentModel).where(
            PlaylistAssignmentModel.device_id == device_id,
            PlaylistAssignmentModel.status
            == PlaylistAssignmentStatus.ACTIVE.value,
        )

        model = self._database_session.execute(
            statement
        ).scalar_one_or_none()

        if model is None:
            return None

        return PlaylistAssignmentMapper.to_domain(model)
