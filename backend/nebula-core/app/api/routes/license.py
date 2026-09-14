from fastapi import APIRouter, Depends, status

from app.api.schemas.license import LicenseResponse
from app.api.security.current_device import get_current_device
from app.application.use_cases.get_device_license import (
    GetDeviceLicenseUseCase,
)
from app.domain.entities.device import Device


router = APIRouter(
    tags=["License"],
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
    current_device: Device = Depends(get_current_device),
) -> LicenseResponse:
    use_case = GetDeviceLicenseUseCase()

    result = use_case.execute(current_device)

    return LicenseResponse(
        device_id=result.device_id,
        status=result.status,
        license_type=result.license_type,
        activated_at=result.activated_at,
        expires_at=result.expires_at,
        days_remaining=result.days_remaining,
        expired=result.expired,
    )
