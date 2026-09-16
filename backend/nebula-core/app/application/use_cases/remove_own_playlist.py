from uuid import UUID

from app.application.exceptions import PlaylistNotFoundError
from app.domain.entities.device import Device
from app.domain.repositories.playlist_assignment_repository import (
    PlaylistAssignmentRepository,
)


class RemoveOwnPlaylistUseCase:
    """O usuário remove uma das listas do próprio Device."""

    def __init__(
        self,
        assignment_repository: PlaylistAssignmentRepository,
    ) -> None:
        self._assignments = assignment_repository

    def execute(self, device: Device, assignment_id: UUID) -> None:
        assignment = self._assignments.find_by_id(assignment_id)

        if assignment is None or assignment.device_id != device.device_id:
            raise PlaylistNotFoundError(
                "Playlist assignment not found for this Device."
            )

        if assignment.is_active:
            assignment.revoke()
            self._assignments.save(assignment)
