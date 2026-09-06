from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.nebula_core_gateway import get_nebula_core_gateway
from app.api.schemas.devices import DeviceListResponse, DeviceOut
from app.api.security.current_admin import get_current_admin
from app.application.exceptions import CoreCommunicationError
from app.application.ports.nebula_core_gateway import NebulaCoreGateway
from app.application.use_cases.list_devices import ListDevicesUseCase


router = APIRouter(
    prefix="/admin/devices",
    tags=["Admin Devices"],
    dependencies=[Depends(get_current_admin)],
)


@router.get(
    "",
    response_model=DeviceListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Devices (BFF)",
)
async def list_devices(
    gateway: NebulaCoreGateway = Depends(get_nebula_core_gateway),
) -> DeviceListResponse:
    use_case = ListDevicesUseCase(gateway)

    try:
        result = await use_case.execute()
    except CoreCommunicationError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error

    return DeviceListResponse(
        devices=[
            DeviceOut(
                device_id=device.device_id,
                platform=device.platform,
                status=device.status,
                app_version=device.app_version,
                created_at=device.created_at,
            )
            for device in result.devices
        ]
    )
