from app.domain.entities.playlist_assignment import PlaylistAssignment
from app.domain.enums.playlist_assignment_status import (
    PlaylistAssignmentStatus,
)
from app.infrastructure.persistence.models.playlist_assignment_model import (
    PlaylistAssignmentModel,
)


class PlaylistAssignmentMapper:
    @staticmethod
    def to_model(
        assignment: PlaylistAssignment,
    ) -> PlaylistAssignmentModel:
        return PlaylistAssignmentModel(
            assignment_id=assignment.assignment_id,
            device_id=assignment.device_id,
            playlist_id=assignment.playlist_id,
            status=assignment.status.value,
            created_at=assignment.created_at,
            updated_at=assignment.updated_at,
        )

    @staticmethod
    def to_domain(
        model: PlaylistAssignmentModel,
    ) -> PlaylistAssignment:
        return PlaylistAssignment(
            device_id=model.device_id,
            playlist_id=model.playlist_id,
            assignment_id=model.assignment_id,
            status=PlaylistAssignmentStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
