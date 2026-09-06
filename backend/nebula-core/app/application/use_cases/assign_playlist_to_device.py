from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import (
    DeviceNotFoundError,
    PlaylistAssignmentAlreadyExistsError,
    PlaylistNotAvailableError,
    PlaylistNotFoundError,
)
from app.domain.entities.playlist_assignment import PlaylistAssignment
from app.domain.enums.playlist_assignment_status import (
    PlaylistAssignmentStatus,
)
from app.domain.repositories.device_repository import DeviceRepository
from app.domain.repositories.playlist_assignment_repository import (
    PlaylistAssignmentRepository,
)
from app.domain.repositories.playlist_repository import PlaylistRepository


@dataclass(frozen=True)
class AssignPlaylistToDeviceCommand:
    device_id: UUID
    playlist_id: UUID


@dataclass(frozen=True)
class AssignPlaylistToDeviceResult:
    assignment_id: UUID
    device_id: UUID
    playlist_id: UUID
    status: PlaylistAssignmentStatus


class AssignPlaylistToDeviceUseCase:
    def __init__(
        self,
        assignment_repository: PlaylistAssignmentRepository,
        playlist_repository: PlaylistRepository,
        device_repository: DeviceRepository,
    ) -> None:
        self._assignment_repository = assignment_repository
        self._playlist_repository = playlist_repository
        self._device_repository = device_repository

    def execute(
        self,
        command: AssignPlaylistToDeviceCommand,
    ) -> AssignPlaylistToDeviceResult:
        device = self._device_repository.find_by_id(command.device_id)

        if device is None:
            raise DeviceNotFoundError(
                f"Device {command.device_id} does not exist."
            )

        playlist = self._playlist_repository.find_by_id(
            command.playlist_id
        )

        if playlist is None:
            raise PlaylistNotFoundError(
                f"Playlist {command.playlist_id} does not exist."
            )

        if not playlist.is_available_for_provisioning:
            raise PlaylistNotAvailableError(
                "A disabled Playlist cannot be assigned to a Device."
            )

        existing = self._assignment_repository.find_active_by_device_id(
            command.device_id
        )

        if existing is not None:
            if existing.playlist_id == command.playlist_id:
                raise PlaylistAssignmentAlreadyExistsError(
                    "Device already has this Playlist assigned."
                )
            existing.revoke()
            self._assignment_repository.save(existing)

        assignment = PlaylistAssignment(
            device_id=command.device_id,
            playlist_id=command.playlist_id,
        )

        self._assignment_repository.save(assignment)

        return AssignPlaylistToDeviceResult(
            assignment_id=assignment.assignment_id,
            device_id=assignment.device_id,
            playlist_id=assignment.playlist_id,
            status=assignment.status,
        )
