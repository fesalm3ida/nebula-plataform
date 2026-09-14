from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.device_repository import (
    get_device_repository,
)
from app.api.schemas.license import LicenseResponse
from app.api.security.current_portal_device import (
    get_current_portal_device,
)
from app.application.exceptions import (
    DeviceNotActiveError,
    LicenseExpiredError,
)
from app.application.use_cases.activate_own_device import (
    ActivateOwnDeviceUseCase,
)
from app.application.use_cases.get_device_license import (
    GetDeviceLicenseUseCase,
)
from app.domain.entities.device import Device
from app.domain.repositories.device_repository import DeviceRepository


router = APIRouter(
    tags=["License"],
)


def _to_response(device: Device) -> LicenseResponse:
    result = GetDeviceLicenseUseCase().execute(device)

    return LicenseResponse(
        device_id=result.device_id,
        status=result.status,
        license_type=result.license_type,
        activated_at=result.activated_at,
        expires_at=result.expires_at,
        days_remaining=result.days_remaining,
        expired=result.expired,
    )


@router.get(
    "/me/license",
    response_model=LicenseResponse,
    status_code=status.HTTP_200_OK,
    summary="Device License",
    description=(
        "Estado de licença do Device autenticado: tipo (trial, anual ou "
        "vitalícia), vencimento e dias restantes."
    ),
)
def get_license(
    current_device: Device = Depends(get_current_portal_device),
) -> LicenseResponse:
    return _to_response(current_device)


@router.post(
    "/me/activation",
    response_model=LicenseResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate Device (owner)",
    description=(
        "Primeira ativação feita pelo dono no portal: gratuita e concede o "
        "trial de 7 dias."
    ),
)
def activate_own_device(
    current_device: Device = Depends(get_current_portal_device),
    repository: DeviceRepository = Depends(
        get_device_repository
    ),
) -> LicenseResponse:
    use_case = ActivateOwnDeviceUseCase(repository)

    try:
        device = use_case.execute(current_device)

    except LicenseExpiredError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except DeviceNotActiveError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        ) from error

    return _to_response(device)
