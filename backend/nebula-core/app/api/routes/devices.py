from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID


from app.api.dependencies.device_repository import get_device_repository
from app.api.schemas.device_registration import (
    DeviceRegistrationRequest,
    DeviceRegistrationResponse,
)
from app.application.exceptions import DeviceAlreadyRegisteredError
from app.application.use_cases.register_device import (
    RegisterDeviceCommand,
    RegisterDeviceUseCase,
)
from app.domain.repositories.device_repository import DeviceRepository

from app.api.schemas.device_activation import DeviceActivationResponse
from app.application.exceptions import ( DeviceAlreadyActiveError,  DeviceAlreadyRegisteredError, DeviceNotFoundError, )
from app.application.use_cases.activate_device import ( ActivateDeviceCommand, ActivateDeviceUseCase,)

router = APIRouter(
    prefix="/devices",
    tags=["Devices"],
)


@router.post(
    "/register",
    response_model=DeviceRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_device(
    request: DeviceRegistrationRequest,
    repository: DeviceRepository = Depends(get_device_repository),
) -> DeviceRegistrationResponse:
    use_case = RegisterDeviceUseCase(repository)

    command = RegisterDeviceCommand(
        fingerprint=request.fingerprint,
        mac_address=request.mac_address,
        platform=request.platform,
        app_version=request.app_version,
    )

    try:
        result = use_case.execute(command)

    except DeviceAlreadyRegisteredError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except (TypeError, ValueError) as error:
        raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error

    return DeviceRegistrationResponse(
        device_id=result.device_id,
        device_key=result.device_key,
        status=result.status,
    )

@router.post(
    "/{device_id}/activate",
    response_model=DeviceActivationResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate Device",
    description=(
        "Temporary development endpoint. "
        "It will later be replaced by a protected administrative flow."
    ),
)
def activate_device(
    device_id: UUID,
    repository: DeviceRepository = Depends(get_device_repository),
) -> DeviceActivationResponse:
    use_case = ActivateDeviceUseCase(repository)

    try:
        result = use_case.execute(
            ActivateDeviceCommand(device_id=device_id)
        )

    except DeviceNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except DeviceAlreadyActiveError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return DeviceActivationResponse(
        device_id=result.device_id,
        status=result.status,
    )
