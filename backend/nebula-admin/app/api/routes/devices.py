from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.nebula_core_gateway import get_nebula_core_gateway
from app.api.schemas.devices import (
    DeviceListResponse,
    DeviceOut,
    DeviceStatusResponse,
)
from app.api.security.current_admin import get_current_admin
from app.application.exceptions import (
    CoreCommunicationError,
    CoreConflictError,
    CoreResourceNotFoundError,
)
from app.application.ports.nebula_core_gateway import NebulaCoreGateway
from app.application.use_cases.list_devices import ListDevicesUseCase
from app.application.use_cases.set_device_status import (
    SetDeviceStatusCommand,
    SetDeviceStatusUseCase,
)


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


async def _apply_lifecycle(
    device_id: UUID,
    action: str,
    gateway: NebulaCoreGateway,
) -> DeviceStatusResponse:
    use_case = SetDeviceStatusUseCase(gateway)

    try:
        result = await use_case.execute(
            SetDeviceStatusCommand(device_id=device_id, action=action)
        )
    except CoreResourceNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except CoreConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    except CoreCommunicationError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error

    return DeviceStatusResponse(
        device_id=result.device_id,
        status=result.status,
    )


@router.post(
    "/{device_id}/activate",
    response_model=DeviceStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate Device (BFF)",
)
async def activate_device(
    device_id: UUID,
    gateway: NebulaCoreGateway = Depends(get_nebula_core_gateway),
) -> DeviceStatusResponse:
    return await _apply_lifecycle(device_id, "activate", gateway)


@router.post(
    "/{device_id}/block",
    response_model=DeviceStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Block Device (BFF)",
)
async def block_device(
    device_id: UUID,
    gateway: NebulaCoreGateway = Depends(get_nebula_core_gateway),
) -> DeviceStatusResponse:
    return await _apply_lifecycle(device_id, "block", gateway)


@router.post(
    "/{device_id}/revoke",
    response_model=DeviceStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoke Device (BFF)",
)
async def revoke_device(
    device_id: UUID,
    gateway: NebulaCoreGateway = Depends(get_nebula_core_gateway),
) -> DeviceStatusResponse:
    return await _apply_lifecycle(device_id, "revoke", gateway)


@router.post(
    "/{device_id}/reset-license",
    response_model=DeviceStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset Device License (BFF)",
    description=(
        "Remove a licença do aparelho e o devolve para 'aguardando "
        "ativação' (útil em suporte e testes)."
    ),
)
async def reset_device_license(
    device_id: UUID,
    gateway: NebulaCoreGateway = Depends(get_nebula_core_gateway),
) -> DeviceStatusResponse:
    return await _apply_lifecycle(device_id, "reset-license", gateway)
