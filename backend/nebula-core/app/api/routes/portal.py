from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.dependencies.playlist_assignment_repository import (
    get_playlist_assignment_repository,
)
from app.api.dependencies.playlist_repository import (
    get_playlist_repository,
)
from app.api.schemas.portal_playlist import (
    PortalPlaylistRequest,
    PortalPlaylistResponse,
    PortalPlaylistsResponse,
)
from app.api.security.current_portal_device import (
    get_current_portal_device,
)
from app.application.exceptions import PlaylistNotFoundError
from app.application.use_cases.register_own_playlist import (
    RegisterOwnPlaylistCommand,
    RegisterOwnPlaylistUseCase,
)
from app.application.use_cases.remove_own_playlist import (
    RemoveOwnPlaylistUseCase,
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


def _to_response(
    playlist: Playlist,
    assignment_id: UUID,
) -> PortalPlaylistResponse:
    return PortalPlaylistResponse(
        assignment_id=assignment_id,
        playlist_id=playlist.playlist_id,
        name=playlist.name,
        format=playlist.format.value,
        source_url=playlist.source_url,
        status=playlist.status.value,
    )


@router.get(
    "/me/playlists",
    response_model=PortalPlaylistsResponse,
    status_code=status.HTTP_200_OK,
    summary="Playlists (portal)",
    description=(
        "Listas de reprodução associadas ao Device — um Device pode ter "
        "uma ou várias."
    ),
)
def list_own_playlists(
    current_device: Device = Depends(get_current_portal_device),
    assignment_repository: PlaylistAssignmentRepository = Depends(
        get_playlist_assignment_repository
    ),
    playlist_repository: PlaylistRepository = Depends(
        get_playlist_repository
    ),
) -> PortalPlaylistsResponse:
    assignments = assignment_repository.find_all_active_by_device_id(
        current_device.device_id
    )

    playlists: list[PortalPlaylistResponse] = []

    for assignment in assignments:
        playlist = playlist_repository.find_by_id(assignment.playlist_id)

        if playlist is not None:
            playlists.append(
                _to_response(playlist, assignment.assignment_id)
            )

    return PortalPlaylistsResponse(playlists=playlists)


@router.delete(
    "/me/playlists/{assignment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove Playlist (portal)",
    description="Remove uma das listas de reprodução do Device.",
)
def remove_own_playlist(
    assignment_id: UUID,
    current_device: Device = Depends(get_current_portal_device),
    assignment_repository: PlaylistAssignmentRepository = Depends(
        get_playlist_assignment_repository
    ),
) -> Response:
    use_case = RemoveOwnPlaylistUseCase(assignment_repository)

    try:
        use_case.execute(current_device, assignment_id)
    except PlaylistNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return Response(status_code=status.HTTP_204_NO_CONTENT)


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
        assignment_id=result.assignment_id,
        playlist_id=result.playlist_id,
        name=result.name,
        format=result.format,
        source_url=result.source_url,
        status=result.status,
    )
