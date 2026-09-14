from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials

from app.api.dependencies.device_repository import (
    get_device_repository,
)
from app.api.security.bearer import bearer_scheme
from app.api.security.current_device import AUTHENTICATE_HEADER
from app.api.security.services import get_access_token_service
from app.application.security.access_token_service import (
    AccessTokenService,
)
from app.domain.entities.device import Device
from app.domain.enums.device_status import DeviceStatus
from app.domain.repositories.device_repository import DeviceRepository


def get_current_portal_device(
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
    """Device autenticado no **portal do dono**.

    Diferente de ``get_current_device``, **não** exige status ``ACTIVE``: o
    dono entra no portal justamente para ativar/licenciar o Device. Devices
    ``REVOKED`` continuam bloqueados.
    """
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

    if device.status == DeviceStatus.REVOKED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Device is revoked.",
        )

    return device
