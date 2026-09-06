from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.playlist_assignment_repository import (
    get_playlist_assignment_repository,
)
from app.api.dependencies.playlist_repository import get_playlist_repository
from app.api.schemas.provisioning import (
    ProvisionedContentEndpointResponse,
    ProvisioningResponse,
)
from app.api.security.current_device import get_current_device
from app.application.exceptions import (
    NoPlaylistAssignedError,
    PlaylistNotAvailableError,
    PlaylistNotFoundError,
)
from app.application.use_cases.provision_device import (
    ProvisionDeviceCommand,
    ProvisionDeviceUseCase,
)
from app.domain.entities.device import Device
from app.domain.repositories.playlist_assignment_repository import (
    PlaylistAssignmentRepository,
)
from app.domain.repositories.playlist_repository import PlaylistRepository


router = APIRouter(
    tags=["Provisioning"],
)


@router.get(
    "/me/provisioning",
    response_model=ProvisioningResponse,
    status_code=status.HTTP_200_OK,
    summary="Device Provisioning",
    description=(
        "Resolves the operational provisioning for the authenticated Device: "
        "its state and the list of authorized content endpoints (Playlists)."
    ),
)
def get_provisioning(
    current_device: Device = Depends(get_current_device),
    assignment_repository: PlaylistAssignmentRepository = Depends(
        get_playlist_assignment_repository
    ),
    playlist_repository: PlaylistRepository = Depends(
        get_playlist_repository
    ),
) -> ProvisioningResponse:
    use_case = ProvisionDeviceUseCase(
        assignment_repository=assignment_repository,
        playlist_repository=playlist_repository,
    )

    try:
        result = use_case.execute(
            ProvisionDeviceCommand(
                device_id=current_device.device_id,
            )
        )

    except (NoPlaylistAssignedError, PlaylistNotFoundError) as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except PlaylistNotAvailableError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return ProvisioningResponse(
        device_id=current_device.device_id,
        device_status=current_device.status,
        content_endpoints=[
            ProvisionedContentEndpointResponse(
                playlist_id=endpoint.playlist_id,
                name=endpoint.name,
                format=endpoint.format,
                source_url=endpoint.source_url,
                status=endpoint.status,
            )
            for endpoint in result.content_endpoints
        ],
    )
