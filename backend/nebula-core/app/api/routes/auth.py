from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.device_repository import (
    get_device_repository,
)
from app.api.schemas.device_authentication import (
    DeviceAuthenticationRequest,
    DeviceAuthenticationResponse,
)
from app.api.security.services import (
    get_access_token_service,
)
from app.application.exceptions import (
    DeviceNotActiveError,
    DeviceNotFoundError,
    InvalidDeviceCredentialsError,
)
from app.application.security.access_token_service import (
    AccessTokenService,
)
from app.application.use_cases.authenticate_device import (
    AuthenticateDeviceCommand,
    AuthenticateDeviceUseCase,
)
from app.domain.repositories.device_repository import DeviceRepository


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/device",
    response_model=DeviceAuthenticationResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate Device",
    description=(
        "Authenticates an active Device and returns a signed "
        "JWT access token."
    ),
)
def authenticate_device(
    request: DeviceAuthenticationRequest,
    repository: DeviceRepository = Depends(
        get_device_repository
    ),
    access_token_service: AccessTokenService = Depends(
        get_access_token_service
    ),
) -> DeviceAuthenticationResponse:
    use_case = AuthenticateDeviceUseCase(
        repository=repository,
        access_token_service=access_token_service,
    )

    command = AuthenticateDeviceCommand(
        device_id=request.device_id,
        device_key=request.device_key,
        fingerprint=request.fingerprint,
    )

    try:
        result = use_case.execute(command)

    except (
        DeviceNotFoundError,
        InvalidDeviceCredentialsError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Device credentials.",
        ) from error

    except DeviceNotActiveError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        ) from error

    except (TypeError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error

    return DeviceAuthenticationResponse(
        access_token=result.access_token,
        token_type=result.token_type,
        expires_at=result.expires_at,
        device_status=result.device_status,
    )
