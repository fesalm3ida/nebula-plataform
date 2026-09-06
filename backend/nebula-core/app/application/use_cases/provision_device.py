from dataclasses import dataclass
from uuid import UUID

from app.application.exceptions import (
    NoPlaylistAssignedError,
    PlaylistNotAvailableError,
    PlaylistNotFoundError,
)
from app.domain.enums.playlist_format import PlaylistFormat
from app.domain.enums.playlist_status import PlaylistStatus
from app.domain.repositories.playlist_assignment_repository import (
    PlaylistAssignmentRepository,
)
from app.domain.repositories.playlist_repository import PlaylistRepository


@dataclass(frozen=True)
class ProvisionDeviceCommand:
    device_id: UUID


@dataclass(frozen=True)
class ProvisionedContentEndpoint:
    """Fonte de conteudo autorizada e fornecida ao Player (ADR-021)."""

    playlist_id: UUID
    name: str
    format: PlaylistFormat
    source_url: str
    status: PlaylistStatus


@dataclass(frozen=True)
class ProvisionDeviceResult:
    device_id: UUID
    content_endpoints: list[ProvisionedContentEndpoint]


class ProvisionDeviceUseCase:
    def __init__(
        self,
        assignment_repository: PlaylistAssignmentRepository,
        playlist_repository: PlaylistRepository,
    ) -> None:
        self._assignment_repository = assignment_repository
        self._playlist_repository = playlist_repository

    def execute(
        self,
        command: ProvisionDeviceCommand,
    ) -> ProvisionDeviceResult:
        assignments = (
            self._assignment_repository.find_all_active_by_device_id(
                command.device_id
            )
        )

        if not assignments:
            raise NoPlaylistAssignedError(
                "Device does not have an active Playlist assigned."
            )

        content_endpoints: list[ProvisionedContentEndpoint] = []

        for assignment in assignments:
            playlist = self._playlist_repository.find_by_id(
                assignment.playlist_id
            )

            if playlist is None:
                raise PlaylistNotFoundError(
                    f"Playlist {assignment.playlist_id} does not exist."
                )

            if not playlist.is_available_for_provisioning:
                raise PlaylistNotAvailableError(
                    "A disabled Playlist cannot be provisioned."
                )

            content_endpoints.append(
                ProvisionedContentEndpoint(
                    playlist_id=playlist.playlist_id,
                    name=playlist.name,
                    format=playlist.format,
                    source_url=playlist.source_url,
                    status=playlist.status,
                )
            )

        return ProvisionDeviceResult(
            device_id=command.device_id,
            content_endpoints=content_endpoints,
        )
