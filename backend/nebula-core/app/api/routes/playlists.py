from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

# NOTE: estes endpoints representam a superficie de gestao administrativa
# (Nebula Admin). Por ora protegidos por um guard placeholder (X-Admin-Token).
from app.api.dependencies.device_repository import get_device_repository
from app.api.dependencies.playlist_assignment_repository import (
    get_playlist_assignment_repository,
)
from app.api.dependencies.playlist_repository import get_playlist_repository
from app.api.schemas.playlist import (
    PlaylistAssignmentRequest,
    PlaylistAssignmentResponse,
    PlaylistCreateRequest,
    PlaylistListResponse,
    PlaylistResponse,
    PlaylistStatusRequest,
    PlaylistUpdateRequest,
)
from app.api.security.admin import require_admin
from app.application.exceptions import (
    DeviceNotFoundError,
    PlaylistAssignmentAlreadyExistsError,
    PlaylistNotAvailableError,
    PlaylistNotFoundError,
)
from app.application.use_cases.assign_playlist_to_device import (
    AssignPlaylistToDeviceCommand,
    AssignPlaylistToDeviceUseCase,
)
from app.application.use_cases.create_playlist import (
    CreatePlaylistCommand,
    CreatePlaylistUseCase,
)
from app.application.use_cases.set_playlist_status import (
    SetPlaylistStatusCommand,
    SetPlaylistStatusUseCase,
)
from app.application.use_cases.update_playlist import (
    UpdatePlaylistCommand,
    UpdatePlaylistUseCase,
)
from app.domain.entities.playlist import Playlist
from app.domain.repositories.device_repository import DeviceRepository
from app.domain.repositories.playlist_assignment_repository import (
    PlaylistAssignmentRepository,
)
from app.domain.repositories.playlist_repository import PlaylistRepository


router = APIRouter(
    prefix="/playlists",
    tags=["Playlists"],
    dependencies=[Depends(require_admin)],
)


def _to_response(playlist: Playlist) -> PlaylistResponse:
    return PlaylistResponse(
        playlist_id=playlist.playlist_id,
        name=playlist.name,
        format=playlist.format,
        source_url=playlist.source_url,
        status=playlist.status,
        created_at=playlist.created_at,
        updated_at=playlist.updated_at,
    )


@router.post(
    "",
    response_model=PlaylistResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Playlist",
)
def create_playlist(
    payload: PlaylistCreateRequest,
    repository: PlaylistRepository = Depends(
        get_playlist_repository
    ),
) -> PlaylistResponse:
    use_case = CreatePlaylistUseCase(repository)

    result = use_case.execute(
        CreatePlaylistCommand(
            name=payload.name,
            format=payload.format,
            source_url=payload.source_url,
        )
    )

    return PlaylistResponse(
        playlist_id=result.playlist_id,
        name=result.name,
        format=result.format,
        source_url=result.source_url,
        status=result.status,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


@router.get(
    "",
    response_model=PlaylistListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Playlists",
)
def list_playlists(
    repository: PlaylistRepository = Depends(
        get_playlist_repository
    ),
) -> PlaylistListResponse:
    playlists = repository.find_all()

    return PlaylistListResponse(
        playlists=[_to_response(playlist) for playlist in playlists]
    )


@router.get(
    "/{playlist_id}",
    response_model=PlaylistResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Playlist",
)
def get_playlist(
    playlist_id: UUID,
    repository: PlaylistRepository = Depends(
        get_playlist_repository
    ),
) -> PlaylistResponse:
    playlist = repository.find_by_id(playlist_id)

    if playlist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found.",
        )

    return _to_response(playlist)


@router.patch(
    "/{playlist_id}",
    response_model=PlaylistResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Playlist",
)
def update_playlist(
    playlist_id: UUID,
    payload: PlaylistUpdateRequest,
    repository: PlaylistRepository = Depends(
        get_playlist_repository
    ),
) -> PlaylistResponse:
    use_case = UpdatePlaylistUseCase(repository)

    try:
        playlist = use_case.execute(
            UpdatePlaylistCommand(
                playlist_id=playlist_id,
                name=payload.name,
                source_url=payload.source_url,
            )
        )

    except PlaylistNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return _to_response(playlist)


@router.post(
    "/{playlist_id}/status",
    response_model=PlaylistResponse,
    status_code=status.HTTP_200_OK,
    summary="Set Playlist Status",
)
def set_playlist_status(
    playlist_id: UUID,
    payload: PlaylistStatusRequest,
    repository: PlaylistRepository = Depends(
        get_playlist_repository
    ),
) -> PlaylistResponse:
    use_case = SetPlaylistStatusUseCase(repository)

    try:
        playlist = use_case.execute(
            SetPlaylistStatusCommand(
                playlist_id=playlist_id,
                status=payload.status,
            )
        )

    except PlaylistNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    return _to_response(playlist)


@router.post(
    "/assignments",
    response_model=PlaylistAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign Playlist to Device",
)
def assign_playlist_to_device(
    payload: PlaylistAssignmentRequest,
    assignment_repository: PlaylistAssignmentRepository = Depends(
        get_playlist_assignment_repository
    ),
    playlist_repository: PlaylistRepository = Depends(
        get_playlist_repository
    ),
    device_repository: DeviceRepository = Depends(
        get_device_repository
    ),
) -> PlaylistAssignmentResponse:
    use_case = AssignPlaylistToDeviceUseCase(
        assignment_repository=assignment_repository,
        playlist_repository=playlist_repository,
        device_repository=device_repository,
    )

    try:
        result = use_case.execute(
            AssignPlaylistToDeviceCommand(
                device_id=payload.device_id,
                playlist_id=payload.playlist_id,
            )
        )

    except DeviceNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except PlaylistNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except (PlaylistNotAvailableError, PlaylistAssignmentAlreadyExistsError) as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return PlaylistAssignmentResponse(
        assignment_id=result.assignment_id,
        device_id=result.device_id,
        playlist_id=result.playlist_id,
        status=result.status,
    )
