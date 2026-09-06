from uuid import UUID

from app.domain.entities.playlist_assignment import PlaylistAssignment
from app.domain.enums.playlist_assignment_status import (
    PlaylistAssignmentStatus,
)
from app.domain.repositories.playlist_assignment_repository import (
    PlaylistAssignmentRepository,
)


class InMemoryPlaylistAssignmentRepository(
    PlaylistAssignmentRepository
):
    def __init__(self) -> None:
        self._assignments: dict[UUID, PlaylistAssignment] = {}

    def save(self, assignment: PlaylistAssignment) -> None:
        self._assignments[assignment.assignment_id] = assignment

    def find_by_id(
        self,
        assignment_id: UUID,
    ) -> PlaylistAssignment | None:
        return self._assignments.get(assignment_id)

    def find_active_by_device_id(
        self,
        device_id: UUID,
    ) -> PlaylistAssignment | None:
        return next(
            (
                assignment
                for assignment in self._assignments.values()
                if assignment.device_id == device_id
                and assignment.status == PlaylistAssignmentStatus.ACTIVE
            ),
            None,
        )
