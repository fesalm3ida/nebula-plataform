from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.playlist_assignment_repository import (
    get_playlist_assignment_repository,
)
from app.api.dependencies.playlist_repository import (
    get_playlist_repository,
)
from app.api.schemas.portal_playlist import (
    PortalPlaylistEnvelope,
    PortalPlaylistRequest,
    PortalPlaylistResponse,
)
from app.api.security.current_portal_device import (
    get_current_portal_device,
)
from app.application.use_cases.register_own_playlist import (
    RegisterOwnPlaylistCommand,
    RegisterOwnPlaylistUseCase,
)
from app.domain.entities.device import Device
from app.domain.entities.playlist import Playlist
from app.domain.repositories.playlist_assignment_repository import (
    PlaylistAssignmentRepository,
)
from app.domain.repositories.playlist_repository import (
    PlaylistRepository,
)


router = APIRouter(
    tags=["Portal"],
)


def _to_response(playlist: Playlist) -> PortalPlaylistResponse:
    return PortalPlaylistResponse(
        playlist_id=playlist.playlist_id,
        name=playlist.name,
        format=playlist.format.value,
        source_url=playlist.source_url,
        status=playlist.status.value,
    )


@router.get(
    "/me/playlist",
    response_model=PortalPlaylistEnvelope,
    status_code=status.HTTP_200_OK,
    summary="Current Playlist (portal)",
    description="Lista de reprodução atualmente associada ao Device.",
)
def get_own_playlist(
    current_device: Device = Depends(get_current_portal_device),
    assignment_repository: PlaylistAssignmentRepository = Depends(
        get_playlist_assignment_repository
    ),
    playlist_repository: PlaylistRepository = Depends(
        get_playlist_repository
    ),
) -> PortalPlaylistEnvelope:
    assignment = assignment_repository.find_active_by_device_id(
        current_device.device_id
    )

    if assignment is None:
        return PortalPlaylistEnvelope(playlist=None)

    playlist = playlist_repository.find_by_id(assignment.playlist_id)

    if playlist is None:
        return PortalPlaylistEnvelope(playlist=None)

    return PortalPlaylistEnvelope(playlist=_to_response(playlist))


@router.post(
    "/me/playlist",
    response_model=PortalPlaylistResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register Own Playlist (portal)",
    description=(
        "O usuário cadastra a própria lista: cria a Playlist e a associa ao "
        "Device autenticado (substituindo a anterior, se houver)."
    ),
)
def register_own_playlist(
    payload: PortalPlaylistRequest,
    current_device: Device = Depends(get_current_portal_device),
    assignment_repository: PlaylistAssignmentRepository = Depends(
        get_playlist_assignment_repository
    ),
    playlist_repository: PlaylistRepository = Depends(
        get_playlist_repository
    ),
) -> PortalPlaylistResponse:
    use_case = RegisterOwnPlaylistUseCase(
        playlist_repository=playlist_repository,
        assignment_repository=assignment_repository,
    )

    try:
        result = use_case.execute(
            RegisterOwnPlaylistCommand(
                device=current_device,
                name=payload.name,
                source_url=payload.source_url,
                format=payload.format,
            )
        )

    except (TypeError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error

    return PortalPlaylistResponse(
        playlist_id=result.playlist_id,
        name=result.name,
        format=result.format,
        source_url=result.source_url,
        status=result.status,
    )
