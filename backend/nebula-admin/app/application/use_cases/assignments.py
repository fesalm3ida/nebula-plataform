from dataclasses import dataclass
from uuid import UUID

from app.application.ports.nebula_core_gateway import NebulaCoreGateway


@dataclass(frozen=True)
class PlaylistAssignmentOut:
    assignment_id: UUID
    device_id: UUID
    playlist_id: UUID
    status: str


@dataclass(frozen=True)
class AssignPlaylistCommand:
    device_id: UUID
    playlist_id: UUID


class AssignPlaylistUseCase:
    def __init__(self, gateway: NebulaCoreGateway) -> None:
        self._gateway = gateway

    async def execute(
        self,
        command: AssignPlaylistCommand,
    ) -> PlaylistAssignmentOut:
        assignment = await self._gateway.assign_playlist_to_device(
            command.device_id,
            command.playlist_id,
        )

        return PlaylistAssignmentOut(
            assignment_id=assignment.assignment_id,
            device_id=assignment.device_id,
            playlist_id=assignment.playlist_id,
            status=assignment.status,
        )
