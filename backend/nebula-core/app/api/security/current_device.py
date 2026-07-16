from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials

from app.api.dependencies.device_repository import (
    get_device_repository,
)
from app.api.security.bearer import bearer_scheme
from app.api.security.services import get_access_token_service
from app.application.security.access_token_service import (
    AccessTokenService,
)
from app.domain.entities.device import Device
from app.domain.enums.device_status import DeviceStatus
from app.domain.repositories.device_repository import DeviceRepository


AUTHENTICATE_HEADER = {
    "WWW-Authenticate": "Bearer",
}


def get_current_device(
    credentials: HTTPAuthorizationCredentials | None = Security(
        bearer_scheme
    ),
    access_token_service: AccessTokenService = Depends(
        get_access_token_service
    ),
    repository: DeviceRepository = Depends(
        get_device_repository
    ),
) -> Device:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers=AUTHENTICATE_HEADER,
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme.",
            headers=AUTHENTICATE_HEADER,
        )

    try:
        device_id = (
            access_token_service.validate_device_access_token(
                credentials.credentials
            )
        )
    except (TypeError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token.",
            headers=AUTHENTICATE_HEADER,
        ) from error

    device = repository.find_by_id(device_id)

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token.",
            headers=AUTHENTICATE_HEADER,
        )

    if device.status != DeviceStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Device is not authorized while status is "
                f"{device.status.value}."
            ),
        )

    return device
