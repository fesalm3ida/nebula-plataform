from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.nebula_core_gateway import get_nebula_core_gateway
from app.api.schemas.playlists import (
    PlaylistCreateRequest,
    PlaylistListResponse,
    PlaylistOut,
)
from app.api.security.current_admin import get_current_admin
from app.application.exceptions import CoreCommunicationError
from app.application.ports.nebula_core_gateway import NebulaCoreGateway
from app.application.use_cases.playlists import (
    CreatePlaylistCommand,
    CreatePlaylistUseCase,
    ListPlaylistsUseCase,
)


router = APIRouter(
    prefix="/admin/playlists",
    tags=["Admin Playlists"],
    dependencies=[Depends(get_current_admin)],
)


def _to_out(playlist) -> PlaylistOut:
    return PlaylistOut(
        playlist_id=playlist.playlist_id,
        name=playlist.name,
        format=playlist.format,
        source_url=playlist.source_url,
        status=playlist.status,
    )


@router.get(
    "",
    response_model=PlaylistListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Playlists (BFF)",
)
async def list_playlists(
    gateway: NebulaCoreGateway = Depends(get_nebula_core_gateway),
) -> PlaylistListResponse:
    use_case = ListPlaylistsUseCase(gateway)

    try:
        result = await use_case.execute()
    except CoreCommunicationError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error

    return PlaylistListResponse(
        playlists=[_to_out(playlist) for playlist in result.playlists]
    )


@router.post(
    "",
    response_model=PlaylistOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create Playlist (BFF)",
)
async def create_playlist(
    payload: PlaylistCreateRequest,
    gateway: NebulaCoreGateway = Depends(get_nebula_core_gateway),
) -> PlaylistOut:
    use_case = CreatePlaylistUseCase(gateway)

    try:
        result = await use_case.execute(
            CreatePlaylistCommand(
                name=payload.name,
                format=payload.format,
                source_url=payload.source_url,
            )
        )
    except CoreCommunicationError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error

    return _to_out(result)
